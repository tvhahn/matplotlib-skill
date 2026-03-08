---
description: Create comprehensive handoff documentation for task continuation by colleagues or LLMs
argument-hint: [task number or description]
---

# Create Handoff Summary

Create a comprehensive handoff summary for seamless task continuation by colleagues or other LLMs.

## Your Task

Generate a detailed handoff document that enables anyone to pick up where you left off, including:

### 1. Context Analysis
- **Project Overview**: Brief description of the project and current phase
- **Task Context**: What specific task/feature is being worked on and why it's important
- **Current Status**: What has been completed and what's next
- **Priority Level**: Why this task matters for the MVP/product goals

### 2. Progress Documentation
- **Completed Work**: Detailed list of what's been finished
- **Current State**: Where things stand right now
- **Next Steps**: Clear direction on what to do next
- **Blockers**: Any impediments or dependencies

### 3. Technical Context
- **Key Files**: Use @ symbol to reference important files and their current status
- **Architecture**: Relevant system components and how they interact
- **Dependencies**: Required tools, libraries, or external services
- **Code Patterns**: Existing conventions to follow

### 4. Implementation Guidance
- **Detailed Tasks**: Break down remaining work into specific, actionable items
- **Success Criteria**: How to know when the task is complete
- **Testing Strategy**: How to verify the implementation works
- **Error Scenarios**: Common pitfalls and how to handle them

### 5. Development Environment
- **Commands**: Key commands needed (with proper prefixes like `uv run`)
- **File Locations**: Where to create new files or modify existing ones
- **Engineering Practices**: Code quality standards, commit patterns, etc.

## Document Structure

Use this template structure:

```markdown
# [Task Name] Handoff Summary: [Brief Description]

## Project Context
[Project description and current phase]

## Task Overview: [Task Name]
**Priority**: [Priority level and reasoning]
**Problem**: [What needs to be solved]
**Goal**: [What success looks like]

## Progress Made (This Session/Conversation)
### [Category 1]
### [Category 2]

## Current State
**Ready for**: [Next immediate step]
**Next Task**: [Specific next action]

### Key Files & Current Status
- **@file/path**: Status and description

## Remaining Work
### [Next Task] — **START HERE**
[Detailed description with specific deliverables]

### [Subsequent Tasks]
[Additional tasks in order]

## Technical Implementation Details
[Code examples, API patterns, etc.]

## Engineering Practices
[Commands, patterns, conventions to follow]

## Success Criteria
[How to know when done]
```

## Special Instructions

${ARGUMENTS ? `**Task Context:** Focus the handoff on: ${ARGUMENTS}` : "**Task Context:** Analyze the current conversation and recent work to determine the main task being handed off"}

### Quality Standards
- **Completeness**: Include everything needed to continue without asking questions
- **Clarity**: Use clear headings, bullet points, and examples
- **Actionability**: Provide specific next steps, not vague directions
- **Technical Accuracy**: Include exact commands, file paths, and code patterns
- **Context Preservation**: Capture both the "what" and the "why"

The handoff should be so comprehensive that someone could pick up the work immediately without needing to read the entire conversation history.
