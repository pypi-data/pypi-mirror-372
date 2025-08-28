# Sub-Agent Resource Access Workaround

## Problem
Claude Code sub-agents (invoked via Task tool) cannot access MCP Resources API directly. This is a known issue with multiple reports on GitHub.

## Solution
We've created MCP Tools that emulate the Resources API functionality:

### Tools Available

#### 1. `list-memory-bank-resources`
Lists all available Memory Bank resources.

**Usage:**
```python
# List all static resources
list-memory-bank-resources()

# List resources for specific component
list-memory-bank-resources(release="02-alpha", component="01-modus-id")
```

**Returns:**
- Formatted list of available resources with URIs
- Current context (release, component, increment)
- Instructions for reading resources

#### 2. `read-memory-bank-resource`
Reads any Memory Bank resource by URI with pagination.

**Usage:**
```python
# Read first page
read-memory-bank-resource(uri="architecture://tech-context/code-standards.md", page=1)

# Read specific page
read-memory-bank-resource(uri="progress://02-alpha/01-modus-id/journal", page=2)
```

**Returns:**
- Resource content with clear pagination markers
- Navigation instructions if multiple pages exist
- Error messages with helpful suggestions

### Supported URI Schemes

- `architecture://` - Architecture and tech context files
- `progress://` - Progress journals and state
- `todo://` - Task decomposition and increment details
- `memory-bank://` - General Memory Bank resources

### Examples

```python
# Get tech context
read-memory-bank-resource(uri="architecture://tech-context/code-standards.md")

# Get current journal
read-memory-bank_resource(uri="progress://02-alpha/01-modus-id/journal")

# Get component specification
read-memory-bank-resource(uri="architecture://02-alpha/01-modus-id/component")

# Get current increment details
read-memory-bank-resource(uri="todo://02-alpha/01-modus-id/increment")
```

### Pagination

Resources are paginated at ~5000 tokens per page. When a resource has multiple pages:

1. The response includes `📄 **PAGE X OF Y**` marker
2. If more pages exist, you'll see `⚠️ **CONTENT CONTINUES**`
3. Clear instructions show how to read the next page
4. You **MUST** read all pages to get complete context

### Integration in Prompts

When creating prompts for sub-agents, include these instructions:

```markdown
## Accessing Memory Bank Resources

Since you're running as a sub-agent, use these MCP tools instead of direct resource access:

1. **List resources:** `list-memory-bank-resources(release, component)`
2. **Read resources:** `read-memory-bank-resource(uri, page=1)`

Always check for pagination markers and read ALL pages when they exist.
```

### Testing

The workaround has been validated with `test_subagent_simulation.py`:

```bash
MEMORY_BANK_PATH=/path/to/memory_bank uv run python test_subagent_simulation.py
```

This confirms:
- ✅ Sub-agents can list all resources
- ✅ Sub-agents can read any resource
- ✅ Pagination works with clear instructions
- ✅ Sub-agents understand navigation
- ✅ All resource types are accessible

## Implementation Details

The workaround is implemented in:
- `src/claude_helpers/memory_bank/mcp_resource_tools.py` - Tool definitions
- `src/claude_helpers/memory_bank/mcp_main.py` - Integration into main MCP server

The tools wrap existing resource functions but provide them through the Tools API instead of Resources API, making them accessible to sub-agents.