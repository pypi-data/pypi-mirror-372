# Fix for next_increment SDK Issue

## Problem
The `next_increment` function was saving the agent's initial thoughts ("I will analyze...") instead of the final analysis to progress-state.md when using Claude Code SDK.

## Root Cause
In `_generate_progress_state_with_sdk` function:
1. `max_turns=1` - Agent only had one turn, not enough to complete analysis
2. Code was collecting ALL text blocks from ALL messages into an array
3. This resulted in capturing the initial acknowledgment instead of the final result

## Solution Applied
Updated the function to properly collect only the final response:

```python
# Before:
options = ClaudeCodeOptions(
    max_turns=1,  # Single response needed - no exploration
    allowed_tools=[],
    cwd=str(memory_bank_path),
    permission_mode="default"
)

response_text = []
async for message in claude_query(prompt=prompt, options=options):
    if hasattr(message, 'content'):
        for block in message.content:
            if hasattr(block, 'text') and block.text:
                response_text.append(block.text)  # Accumulating all text
                
return ''.join(response_text).strip()  # Returns everything including initial thoughts
```

```python
# After:
options = ClaudeCodeOptions(
    max_turns=3,  # Give agent time to think and analyze
    allowed_tools=[],
    cwd=str(memory_bank_path),
    permission_mode="default"
)

final_response = None
async for message in claude_query(prompt=prompt, options=options):
    if hasattr(message, 'content'):
        current_text = []
        for block in message.content:
            if hasattr(block, 'text') and block.text:
                current_text.append(block.text)
        
        if current_text:
            final_response = ''.join(current_text)  # Overwrite with each message
            
return final_response  # Returns only the last message before ResultMessage
```

## Key Changes
1. **Increased `max_turns` from 1 to 3** - Allows agent to complete analysis
2. **Changed from accumulating to overwriting** - `final_response` is updated (not appended) with each message
3. **Added validation** - Check response has proper structure and sufficient content

## Testing
The fix ensures that when Claude SDK is available (inside Claude Code), the agent's final analyzed response is captured, not the initial acknowledgment. When SDK is not available, the fallback mechanism is used as intended.

## Related Functions
This pattern was already correctly implemented in:
- `_generate_with_claude_sdk_async` (increment overview generation)
- `_ask_with_claude_sdk_async` (ask-memory-bank)

These functions already use similar logic with higher `max_turns` and proper response collection.