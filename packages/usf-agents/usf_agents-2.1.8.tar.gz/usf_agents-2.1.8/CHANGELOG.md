# Changelog

All notable changes to the USF Agent SDK will be documented in this file.

## [2.1.8] - 2025-01-28

### 🔧 Fixed
- **CRITICAL FIX**: Resolved `BadRequestError: Response format is not allowed with tools` error
  - Removed empty `tools: []` parameter from final response API calls in `generate_final_response_with_openai()` and `stream_final_response_with_openai()`
  - The USF API was rejecting requests that included the `tools` parameter even when empty
  - This fix ensures final response calls work correctly without tool-related parameters

### ✨ Added
- **Debug Mode**: Comprehensive debug logging functionality
  - Added `debug` parameter to agent configuration
  - Shows complete API request payloads, headers, and responses
  - Masks API keys in debug output for security (shows first 10 and last 4 characters)
  - Includes error details with full context when API calls fail
  - Works across all API calls: planning, tool calling, and final response generation

### 🚀 Enhanced
- **Error Handling**: Improved error messages with detailed API response information
  - Enhanced error messages now include actual server response bodies when available
  - Better context about which stage of the process failed
  - More specific guidance for different types of errors (401, 403, 404, 429, 5xx)

### 📚 Documentation
- Updated README.md with comprehensive debug mode documentation
- Added troubleshooting section for the fixed error
- Created `debug_example.py` with practical debug mode usage examples
- Created `test_fix.py` to verify the fixes work correctly

### 🔧 Technical Details

#### Files Modified:
- `usf_agents/usfMessageHandler.py`:
  - Added `_debug_log()` function for consistent debug output
  - Removed `tools: []` parameter from OpenAI API calls
  - Enhanced error handling with response body capture
  - Added debug logging to all API call functions

- `usf_agents/usfPlanner.py`:
  - Added `_debug_log()` function
  - Enhanced error handling with response body capture
  - Added debug logging to planning and tool call functions

#### Debug Mode Features:
- **Global Debug**: `{'debug': True}` enables debug for all stages
- **Stage-Specific Debug**: Enable debug only for specific stages (planning, tool_calling, final_response)
- **Per-Request Debug**: Override debug mode for individual requests
- **Security**: API keys are automatically masked in debug output
- **Comprehensive**: Shows URLs, headers, payloads, responses, and errors

#### Usage Examples:
```python
# Enable debug mode
agent = USFAgent({
    'api_key': 'your-api-key',
    'debug': True,  # Shows all API call details
    'model': 'usf-mini'
})

# Stage-specific debug
agent = USFAgent({
    'api_key': 'your-api-key',
    'final_response': {
        'debug': True  # Only debug final response calls
    }
})

# Per-request debug
async for result in agent.run(messages, {
    'debug': True  # Enable debug for this request only
}):
    pass
```

### 🐛 Bug Fixes
- Fixed parameter filtering to exclude `debug` from API calls
- Improved JSON parsing error handling
- Enhanced network error detection and reporting

---

## [1.0.0] - Previous Release

### Initial Features
- Multi-stage configuration support
- Manual tool execution
- Provider flexibility
- Memory management
- Streaming support
- Automatic date/time appending
- Date/time override functionality
- Extra parameters support
- Type hints support
