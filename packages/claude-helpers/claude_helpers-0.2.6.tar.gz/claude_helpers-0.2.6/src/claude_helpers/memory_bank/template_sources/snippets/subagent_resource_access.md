# Sub-Agent Resource Access Instructions

**IMPORTANT**: As a sub-agent invoked via Task tool, you cannot access MCP Resources API directly. Use these alternative MCP tools instead:

## Listing Available Resources
```
list-memory-bank-resources(release="{release}", component="{component}")
```

This will show you all available resources including:
- Tech context files (code standards, testing standards, etc.)
- Current increment details and journals
- Component specifications
- Task decomposition

## Reading Resources
```
read-memory-bank-resource(uri="<resource_uri>", page=1)
```

### Common Resources You'll Need:

**Tech Context:**
- `architecture://tech-context/code-standards.md` - Coding standards
- `architecture://tech-context/testing-standards.md` - Testing requirements
- `architecture://tech-context/tech-stack.md` - Technology stack

**Component Context:**
- `architecture://{release}/{component}/component` - Component specification
- `todo://{release}/{component}/increment` - Current increment details
- `todo://{release}/{component}/decomposition` - Full task breakdown

**Progress Tracking:**
- `progress://{release}/{component}/journal` - Current work journal
- `progress://{release}/{component}/state` - Combined progress state

## Important: Pagination

⚠️ **Resources may be paginated!** Always:
1. Check for `📄 **PAGE X OF Y**` markers
2. If you see `⚠️ **CONTENT CONTINUES**`, read the next page
3. Use the provided command to read subsequent pages
4. **Read ALL pages** to get complete context

Example:
```
# If page 1 shows "PAGE 1 OF 3" and "CONTENT CONTINUES":
read-memory-bank-resource(uri="architecture://tech-context/code-standards.md", page=2)
read-memory-bank-resource(uri="architecture://tech-context/code-standards.md", page=3)
```

## Why This Workaround?

You're running as a sub-agent through the Task tool, which has a limitation: sub-agents cannot access the MCP Resources API directly. These tools provide the same functionality through the MCP Tools API, which sub-agents CAN access.