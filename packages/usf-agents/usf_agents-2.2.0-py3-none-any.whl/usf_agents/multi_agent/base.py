import json
from typing import List, Dict, Any, Optional, AsyncGenerator, Union

from ..usfAgent import USFAgent
from ..types import Message, RunOptions, AgentResult, Tool, ToolCall
from ..types.multi_agent import (
    AgentId,
    AgentSpec,
    ContextMode,
    TaskPayload,
    ToolCallExecutionResult,
)
from .context import shape_context_for_mode, to_openai_messages_from_task


def _collect_final_answer(agent: USFAgent, messages: List[Message], options: Optional[RunOptions] = None) -> Dict[str, Any]:
    """
    Helper to run the USFAgent and collect either final_answer or first tool_calls requirement.
    Returns:
      {
        'status': 'final' | 'tool_calls' | 'error',
        'content': Optional[str],
        'tool_calls': Optional[List[Dict[str, Any]]],
        'raw_chunks': List[Dict[str, Any]]  # plan/tool_calls/final chunks as yielded
      }
    """
    # The run() is async generator; we need to consume it synchronously from async context
    # This helper is intended to be awaited by wrapper methods.
    raise RuntimeError("This helper must be awaited via _acollect_final_answer")


async def _acollect_final_answer(agent: USFAgent, messages: List[Message], options: Optional[RunOptions] = None) -> Dict[str, Any]:
    raw_chunks: List[Dict[str, Any]] = []
    async for chunk in agent.run(messages, options or {}):
        raw_chunks.append(chunk)
        if chunk.get('type') == 'tool_calls':
            return {
                'status': 'tool_calls',
                'content': None,
                'tool_calls': chunk.get('tool_calls'),
                'raw_chunks': raw_chunks
            }
        if chunk.get('type') == 'final_answer':
            return {
                'status': 'final',
                'content': chunk.get('content', ''),
                'tool_calls': None,
                'raw_chunks': raw_chunks
            }
    # If nothing decisive was returned
    return {
        'status': 'error',
        'content': None,
        'tool_calls': None,
        'raw_chunks': raw_chunks
    }


class BaseAgentWrapper:
    """
    Composition wrapper over USFAgent that enforces isolation and provides
    unified entry points for message-based and task-based execution.
    """

    def __init__(self, spec: AgentSpec):
        if not spec or not isinstance(spec, dict):
            raise Exception("BaseAgentWrapper Error: spec is required")

        self.id: AgentId = spec.get('id') or ''
        self.name: str = spec.get('name') or self.id or 'agent'
        self.agent_type: str = spec.get('agent_type', 'generic')
        self.backstory: str = spec.get('backstory', '') or ''
        self.goal: str = spec.get('goal', '') or ''
        self.context_mode: ContextMode = spec.get('context_mode', 'NONE')  # default policy for sub usage

        usf_config = spec.get('usf_config') or {}
        # Ensure backstory/goal are present in agent config for consistent behavior
        usf_config = {
            **usf_config,
            'backstory': self.backstory,
            'goal': self.goal,
        }

        # Memory is isolated per wrapper by virtue of distinct USFAgent instance.
        self.usf = USFAgent(usf_config)

        # Allow manager/generic agents to have native tools (not sub-agents as tools)
        self._native_tools: List[Tool] = spec.get('tools', []) or []

    async def run_messages(self, messages: List[Message], options: Optional[RunOptions] = None) -> AsyncGenerator[AgentResult, None]:
        """
        Direct entry for message-based usage (main entry points).
        Yields the underlying USFAgent chunks unmodified.
        """
        async for chunk in self.usf.run(messages, options or {}):
            yield chunk  # pass-through preserving structure

    async def run_task(
        self,
        task: TaskPayload,
        calling_agent_msgs: Optional[List[Message]] = None,
        context_param: Optional[Dict[str, Any]] = None,
        options: Optional[RunOptions] = None
    ) -> Dict[str, Any]:
        """
        Task-based entry (used for agent-as-tool flows or programmatic invocations).
        Shapes messages using current context_mode policy and executes the USFAgent.
        Returns a dict with either final content or a tool_calls request.
        """
        # Build messages based on this agent's default policy
        shaped_messages = shape_context_for_mode(
            self.context_mode,
            task,
            calling_agent_msgs=calling_agent_msgs,
            context_param=context_param
        )
        result = await _acollect_final_answer(self.usf, shaped_messages, options)
        return result

    def get_public_tool(self) -> Optional[Tool]:
        """
        Default: no direct public tool surface. Subclasses may override.
        """
        return None

    def list_native_tools(self) -> List[Tool]:
        """
        Native external tools configured for this agent (excludes sub-agents).
        """
        return list(self._native_tools)


class SubAgent(BaseAgentWrapper):
    """
    SubAgent that can expose a tool surface for managers (agent-as-tool),
    while keeping its internals (tools, memory) fully private.
    """

    def get_public_tool(self, schema: Dict[str, Any], alias: Optional[str] = None) -> Tool:
        """
        Provide a callable OpenAI tool definition for this SubAgent. This is a light adapter;
        a richer AgentToolAdapter is provided in the adapter module.
        """
        tool_name = alias or f"agent_{self.id}"
        # Minimal tool schema; developers can pass richer JSON schema via `schema`.
        return {
            'type': 'function',
            'function': {
                'name': tool_name,
                'description': schema.get('description', f"Invoke sub-agent {self.name} ({self.id})"),
                'parameters': schema.get('parameters', {
                    'type': 'object',
                    'properties': {
                        'task': {'type': 'string', 'description': 'Task name/description'},
                        'input': {'type': 'object', 'description': 'Structured inputs for the task'},
                        'context_param': {'type': 'object', 'description': 'Lightweight context object'}
                    },
                    'required': ['task']
                })
            }
        }

    async def execute_as_tool(
        self,
        tool_call: ToolCall,
        calling_context: Optional[List[Message]],
        context_param: Optional[Dict[str, Any]] = None,
        options: Optional[RunOptions] = None
    ) -> ToolCallExecutionResult:
        """
        Execute the sub-agent when invoked as a tool. Parses ToolCall arguments into TaskPayload,
        shapes context per this agent's context_mode, and returns a normalized tool result.
        """
        try:
            func = tool_call.get('function') or {}
            tool_name = func.get('name') or f"agent_{self.id}"
            raw_args = func.get('arguments') or '{}'
            try:
                args = json.loads(raw_args)
            except Exception:
                # Accept non-JSON args gracefully
                args = {'task': str(raw_args)}

            task: TaskPayload = {
                'task': args.get('task') or 'task',
                'input': args.get('input') or {},
                'metadata': args.get('metadata') or {}
            }
            # Allow explicit context_param override at call-time
            call_context_param = context_param if context_param is not None else args.get('context_param')

            shaped_messages = shape_context_for_mode(
                self.context_mode,
                task,
                calling_agent_msgs=calling_context,
                context_param=call_context_param
            )

            collected = await _acollect_final_answer(self.usf, shaped_messages, options)

            if collected['status'] == 'final':
                return {
                    'success': True,
                    'content': collected.get('content') or '',
                    'error': None,
                    'tool_name': tool_name,
                    'raw': collected
                }
            if collected['status'] == 'tool_calls':
                # The sub-agent requested tools; return as not-final so the caller can handle execution
                return {
                    'success': False,
                    'content': '',
                    'error': 'Sub-agent requested tool_calls; external execution required.',
                    'tool_name': tool_name,
                    'raw': collected
                }
            return {
                'success': False,
                'content': '',
                'error': 'Sub-agent returned no final content.',
                'tool_name': tool_name,
                'raw': collected
            }
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'error': f'execute_as_tool error: {e}',
                'tool_name': tool_call.get('function', {}).get('name', f"agent_{self.id}"),
                'raw': None
            }


class ManagerAgent(BaseAgentWrapper):
    """
    ManagerAgent that can aggregate native tools and sub-agents (as tools).
    This base implementation avoids hard dependency on adapter/registry modules to prevent cycles.
    """

    def __init__(self, spec: AgentSpec):
        super().__init__(spec)
        # Track sub-agents and their tool schemas for later tool list composition
        self._sub_entries: List[Dict[str, Any]] = []  # [{'sub': SubAgent, 'schema': Dict, 'alias': Optional[str]}]

    def add_sub_agent(self, sub: SubAgent, tool_schema: Dict[str, Any], alias: Optional[str] = None) -> None:
        """
        Register a sub-agent with an associated tool schema. Tool definition will be generated
        dynamically in list_tools to avoid circular imports with adapter.
        """
        self._sub_entries.append({'sub': sub, 'schema': tool_schema or {}, 'alias': alias})

    def list_tools(self) -> List[Tool]:
        """
        Compose native tools + sub-agent tools. Uses the sub-agent's own get_public_tool
        for now; later the adapter module can be used for richer behavior.
        """
        tools: List[Tool] = []
        tools.extend(self.list_native_tools())

        for entry in self._sub_entries:
            sub: SubAgent = entry['sub']
            schema: Dict[str, Any] = entry['schema']
            alias: Optional[str] = entry.get('alias')
            try:
                tools.append(sub.get_public_tool(schema, alias=alias))
            except Exception:
                # Fallback minimal definition if sub provides no tool surface
                tools.append({
                    'type': 'function',
                    'function': {
                        'name': alias or f"agent_{sub.id}",
                        'description': f"Invoke sub-agent {sub.name} ({sub.id})",
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                'task': {'type': 'string'},
                                'input': {'type': 'object'},
                                'context_param': {'type': 'object'}
                            },
                            'required': ['task']
                        }
                    }
                })
        return tools

    async def delegate(
        self,
        sub_id: AgentId,
        task: TaskPayload,
        policy: Union[ContextMode, str] = 'inherit_manager_policy',
        context_param: Optional[Dict[str, Any]] = None,
        calling_context: Optional[List[Message]] = None,
        options: Optional[RunOptions] = None
    ) -> ToolCallExecutionResult:
        """
        Delegate a TaskPayload to a registered sub-agent with a specific policy.
        If policy == 'inherit_manager_policy', uses sub.context_mode.
        Otherwise, uses the provided ContextMode value.
        """
        # Find sub-agent
        target: Optional[SubAgent] = None
        for entry in self._sub_entries:
            if entry['sub'].id == sub_id:
                target = entry['sub']
                break

        if not target:
            return {
                'success': False,
                'content': '',
                'error': f'Sub-agent {sub_id} not found',
                'tool_name': f'agent:{sub_id}',
                'raw': None
            }

        # Determine mode
        if isinstance(policy, str) and policy == 'inherit_manager_policy':
            mode: ContextMode = target.context_mode
        else:
            mode = policy  # type: ignore

        shaped_messages = shape_context_for_mode(
            mode,
            task,
            calling_agent_msgs=calling_context,
            context_param=context_param
        )

        collected = await _acollect_final_answer(target.usf, shaped_messages, options)

        if collected['status'] == 'final':
            return {
                'success': True,
                'content': collected.get('content') or '',
                'error': None,
                'tool_name': f'agent:{sub_id}',
                'raw': collected
            }
        if collected['status'] == 'tool_calls':
            return {
                'success': False,
                'content': '',
                'error': 'Sub-agent requested tool_calls; external execution required.',
                'tool_name': f'agent:{sub_id}',
                'raw': collected
            }
        return {
            'success': False,
            'content': '',
            'error': 'Delegation produced no final content.',
            'tool_name': f'agent:{sub_id}',
            'raw': collected
        }
