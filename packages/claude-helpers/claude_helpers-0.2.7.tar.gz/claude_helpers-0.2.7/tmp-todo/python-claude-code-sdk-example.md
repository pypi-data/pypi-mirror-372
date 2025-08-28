# Example from Claude Code Docs

> Source: https://docs.anthropic.com/en/docs/claude-code/sdk#python

## Multi-turn conversations

```python
import asyncio
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions, query

# Method 1: Using ClaudeSDKClient for persistent conversations
async def multi_turn_conversation():
    async with ClaudeSDKClient() as client:
        # First query
        await client.query("Let's refactor the payment module")
        async for msg in client.receive_response():
            # Process first response
            pass
        
        # Continue in same session
        await client.query("Now add comprehensive error handling")
        async for msg in client.receive_response():
            # Process continuation
            pass
        
        # The conversation context is maintained throughout

# Method 2: Using query function with session management
async def resume_session():
    # Continue most recent conversation
    async for message in query(
        prompt="Now refactor this for better performance",
        options=ClaudeCodeOptions(continue_conversation=True)
    ):
        if type(message).__name__ == "ResultMessage":
            print(message.result)

    # Resume specific session
    async for message in query(
        prompt="Update the tests", 
        options=ClaudeCodeOptions(
            resume="550e8400-e29b-41d4-a716-446655440000",
            max_turns=3
        )
    ):
        if type(message).__name__ == "ResultMessage":
            print(message.result)

# Run the examples
asyncio.run(multi_turn_conversation())
```

## Custom permission prompt tool

```md
Optionally, use --permission-prompt-tool to pass in an MCP tool that we will use to check whether or not the user grants the model permissions to invoke a given tool. When the model invokes a tool the following happens:

We first check permission settings: all settings.json files, as well as --allowedTools and --disallowedTools passed into the SDK; if one of these allows or denies the tool call, we proceed with the tool call
Otherwise, we invoke the MCP tool you provided in --permission-prompt-tool
The --permission-prompt-tool MCP tool is passed the tool name and input, and must return a JSON-stringified payload with the result. The payload must be one of:
```

```
// tool call is allowed
{
  "behavior": "allow",
  "updatedInput": {...}, // updated input, or just return back the original input
}

// tool call is denied
{
  "behavior": "deny",
  "message": "..." // human-readable string explaining why the permission was denied
}
```
### Implementation examples:

```
import asyncio
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

async def use_permission_prompt():
    """Example using custom permission prompt tool"""
    
    # MCP server configuration
    mcp_servers = {
        # Example configuration - uncomment and configure as needed:
        # "security": {
        #     "command": "npx",
        #     "args": ["-y", "@modelcontextprotocol/server-security"],
        #     "env": {"API_KEY": "your-key"}
        # }
    }
    
    async with ClaudeSDKClient(
        options=ClaudeCodeOptions(
            permission_prompt_tool_name="mcp__security__approval_prompt",  # Changed from permission_prompt_tool
            mcp_servers=mcp_servers,
            allowed_tools=["Read", "Grep"],
            disallowed_tools=["Bash(rm*)", "Write"],
            system_prompt="You are a security auditor"
        )
    ) as client:
        await client.query("Analyze and fix the security issues")
        
        # Monitor tool usage and permissions
        async for message in client.receive_response():
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'type'):  # Added check for 'type' attribute
                        if block.type == 'tool_use':
                            print(f"[Tool: {block.name}] ", end='')
                    if hasattr(block, 'text'):
                        print(block.text, end='', flush=True)
            
            # Check for permission denials in error messages
            if type(message).__name__ == "ErrorMessage":
                if hasattr(message, 'error') and "Permission denied" in str(message.error):
                    print(f"\n⚠️ Permission denied: {message.error}")

# Example MCP server implementation (Python)
# This would be in your MCP server code
async def approval_prompt(tool_name: str, input: dict, tool_use_id: str = None):
    """Custom permission prompt handler"""
    # Your custom logic here
    if "allow" in str(input):
        return json.dumps({
            "behavior": "allow",
            "updatedInput": input
        })
    else:
        return json.dumps({
            "behavior": "deny",
            "message": f"Permission denied for {tool_name}"
        })

asyncio.run(use_permission_prompt())

```
