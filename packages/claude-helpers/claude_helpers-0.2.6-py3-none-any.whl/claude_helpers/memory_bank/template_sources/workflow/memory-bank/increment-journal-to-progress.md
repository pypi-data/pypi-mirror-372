---
role: analyzer
task: journal_to_progress
description: Convert increment journal entries to structured progress-state section
---

# Convert Journal to Progress State

You are analyzing journal entries from a completed increment to generate a structured progress-state section.

## Context
- Release: {release}
- Component: {component}
- Completed Increment: {increment_name}

## Journal Content to Analyze

{journal_content}

## Existing Progress State (for context, do not modify)

{existing_state}

## Your Task

Based on the journal entries above, generate ONLY the new progress-state section for increment {increment_name}.

### 1. Extract State (Technical Implementation)
From the journal entries, identify and list:
- **Files Created or Modified**: Extract actual file paths mentioned (e.g., `src/module/file.py`)
- **Components Implemented**: Classes, functions, modules created
- **Patterns & Architecture**: Design patterns, architectural decisions applied
- **Configuration Changes**: Settings, parameters, environment variables added
- **Dependencies**: New libraries, packages, or integrations added

### 2. Extract Progress (Business Functionality)
From the journal entries, identify:
- **Functionality Delivered**: What features or capabilities were implemented
- **Interfaces Exposed**: APIs, methods, or integration points created
- **Quality Achievements**: Test coverage, security measures, performance metrics
- **Business Value**: How this increment moves the project forward

### 3. Format Output

Generate a markdown section with this EXACT structure:

```markdown
## {increment_name}

### State
- **Files Created**:
  - `path/to/file.py` - Brief description of purpose
  - `path/to/another.py` - What it does

- **Components**:
  - ComponentName: Purpose and responsibility
  - AnotherComponent: What it handles

- **Patterns Used**:
  - Pattern name - How it's applied in this increment
  - Another pattern - Its application

- **Configuration**:
  - Setting/parameter - Value and purpose
  - Environment variable - What it controls

### Progress
- **Functionality Delivered**:
  - Feature description - Business value provided
  - Another feature - User benefit

- **Interfaces**:
  - API endpoint/method - What it exposes
  - Integration point - How it connects

- **Quality Achievements**:
  - Test coverage: X%
  - Security: Specific measures implemented
  - Performance: Optimizations applied

- **Next Steps Ready**:
  - What the next increment can now build upon
  - Integration points available for future work
```

## Guidelines

1. **Be Specific**: Use actual names, paths, and values from the journal
2. **Be Concise**: Keep descriptions brief but informative
3. **Be Technical in State**: Focus on implementation details
4. **Be Business-Oriented in Progress**: Focus on value and functionality
5. **Extract Real Data**: Don't invent information not in the journal
6. **Maintain Structure**: Follow the exact format above

## Important

- Output ONLY the formatted markdown section
- Start with `## {increment_name}` header
- Do not include any explanations, metadata, or markdown code blocks
- The output will be directly appended to progress-state.md
- If journal is empty or minimal, still generate a basic structure noting what was tracked