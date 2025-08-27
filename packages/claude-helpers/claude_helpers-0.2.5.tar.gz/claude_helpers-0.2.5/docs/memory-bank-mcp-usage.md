# Memory Bank MCP Usage Guide

## For Claude Agents

### 1. List Available Resources

MCP automatically provides resource discovery through the built-in `resources/list` method. 
When you use `ListMcpResourcesTool`, it will show all available resources with their URIs.

### 2. Read Resources

To read any resource, use `ReadMcpResourceTool`:

```
ReadMcpResourceTool(
    server="memory-bank-kenoma",
    uri="progress://02-alpha/01-modus-id/journal"
)
```

The response will be JSON with these fields:
- `content` - The actual content of the resource
- `pagination` - Info about pages if content is large
- `uri` - The resource URI
- `name` - Human-readable name
- `mime_type` - Content type (usually text/markdown)

### 3. Common Resource URIs

#### Current Work
- `progress://02-alpha/01-modus-id/journal` - Current increment journal
- `todo://02-alpha/01-modus-id/increment` - Current increment specification
- `progress://02-alpha/01-modus-id/state` - Combined project state

#### Component Information
- `architecture://02-alpha/01-modus-id/component` - Component specification
- `todo://02-alpha/01-modus-id/decomposition` - Task breakdown

#### Standards & Context
- `architecture://tech-context/code-standards.md` - Coding standards
- `architecture://tech-context/tech-stack.md` - Technology stack

#### Historical Journals
- `progress://02-alpha/01-modus-id/01-models-and-protocols/journal` - Increment 01 journal
- `progress://02-alpha/01-modus-id/02-configuration-and-exceptions/journal` - Increment 02 journal
- `progress://02-alpha/01-modus-id/03-hmac-state-manager/journal` - Increment 03 journal

### 4. Resource Response Format

Resources return JSON with these fields:

```json
{
  "uri": "progress://02-alpha/01-modus-id/journal",
  "name": "Journal - 01-modus-id/05-auth0-oauth-client",
  "content": "...",
  "mime_type": "text/markdown"
}
```

MCP clients handle large content appropriately. No manual pagination is needed.

### 5. Adding Journal Entries

Use the `journal-note` tool:

```
journal-note(
    release="02-alpha",
    component="01-modus-id",
    role="dev",
    message="Implemented feature X with pattern Y"
)
```

### 6. Moving to Next Increment

When increment is complete:

```
next-increment(
    release="02-alpha",
    component="01-modus-id"
)
```

This will:
1. Generate progress-state section from journal
2. Move to next increment
3. Create new journal for the new increment

## Resource Structure in Memory Bank

```
memory_bank_kenoma/
├── architecture/
│   ├── tech-context/        # Standards and guidelines
│   └── releases/
│       └── 02-alpha/
│           └── components/
│               └── 01-modus-id.md  # Component spec
├── implementation/
│   └── releases/
│       └── 02-alpha/
│           └── components/
│               └── 01-modus-id/
│                   ├── component.md
│                   ├── decomposition.md
│                   └── increments/
│                       ├── 01-models-and-protocols.md
│                       ├── 02-configuration-and-exceptions.md
│                       └── ...
└── progress/
    └── releases/
        └── 02-alpha/
            └── components/
                └── 01-modus-id/
                    ├── progress-state.md
                    └── increments/
                        ├── 01-models-and-protocols/
                        │   └── journal.md
                        ├── 02-configuration-and-exceptions/
                        │   └── journal.md
                        └── ...
```

## Examples for Claude Agents

### Example 1: Check Current State

```python
# 1. List resources (built-in MCP method)
ListMcpResourcesTool(server="memory-bank-kenoma")

# 2. Read current journal
response = ReadMcpResourceTool(
    server="memory-bank-kenoma",
    uri="progress://02-alpha/01-modus-id/journal"
)
# Parse JSON response to get content

# 3. Check current increment
response = ReadMcpResourceTool(
    server="memory-bank-kenoma",
    uri="todo://02-alpha/01-modus-id/increment"
)
```

### Example 2: Add Progress and Move Forward

```python
# 1. Add journal entry about completed work
journal-note(
    release="02-alpha",
    component="01-modus-id",
    role="dev",
    message="Completed JWKS cache implementation with TTL support"
)

# 2. Add tech-lead review
journal-note(
    release="02-alpha",
    component="01-modus-id",
    role="tech-lead",
    message="Reviewed: Cache implementation is solid, TTL correctly handled"
)

# 3. Move to next increment
next-increment(release="02-alpha", component="01-modus-id")
```

### Example 3: Review Historical Progress

```python
# Read journal from specific past increment
response = ReadMcpResourceTool(
    server="memory-bank-kenoma",
    uri="progress://02-alpha/01-modus-id/03-hmac-state-manager/journal"
)

# Check combined state
response = ReadMcpResourceTool(
    server="memory-bank-kenoma",
    uri="progress://02-alpha/01-modus-id/state"
)
```