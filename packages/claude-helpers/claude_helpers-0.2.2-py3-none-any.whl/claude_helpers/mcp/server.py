"""MCP server for Claude Helpers HIL integration."""

from fastmcp import FastMCP
from ..hil.core import ask_human_hil, voice_input_hil, HILError


# Create MCP server instance
mcp = FastMCP("Claude Helpers HIL")


@mcp.tool(name="ask-human")
def ask_human(query: str, sender_role: str = "assistant") -> str:
    """
    Ask a question to the human developer via the Human-in-the-Loop system.
    
    Use this whenever you need human input, clarification, or decision-making help.
    The human can respond via text or voice input (they choose in the UI).
    
    Timeout is controlled by Claude Code's MCP_TOOL_TIMEOUT setting.
    
    Args:
        query: The question text to ask the human
        sender_role: Who is asking (e.g. "assistant", "developer", "designer")
        
    Returns:
        The human's answer (transcribed if voice, or text if typed)
        
    Examples:
        - ask_human("Should I implement this using approach A or B?", "assistant")
        - ask_human("Does this error handling look correct?", "code reviewer")
        - ask_human("What's the preferred naming convention here?", "developer")
    """
    if not query.strip():
        return "Error: Query cannot be empty"
        
    try:
        # Create formatted question with role context
        formatted_question = f"[{sender_role}] {query}"
        # Use default HIL timeout - MCP_TOOL_TIMEOUT will control the overall timeout
        return ask_human_hil(formatted_question)
    except HILError as e:
        return f"HIL Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"


@mcp.prompt()
def ask(query: str = None) -> str:
    """Prompt to ask human for input, optionally with voice.
    
    This replaces the /voice slash command for more native MCP integration.
    
    Args:
        query: Optional initial query or context
        
    Returns:
        Formatted prompt to initiate human interaction
    """
    if query:
        prompt = f"""
Please ask the human the following question:

{query}

Use the `ask-human` tool to get their response. The human can respond via text or voice input.
"""
    else:
        prompt = """
Please ask the human for input using the `ask-human` tool. 

You can ask for:
- Clarification on requirements
- Decision between implementation approaches  
- Feedback on current progress
- Any other input needed to continue

The human can respond via text or voice input based on their preference.
"""
    
    return prompt


def run_mcp_server():
    """Run the MCP server with stdio transport."""
    mcp.run()  # Default transport is stdio