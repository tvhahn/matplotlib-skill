---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git add:*)
description: Generate structured git commit with conventional format and file tracking
argument-hint: [optional commit message]
---

# Git Commit Command

Generate a comprehensive, well-structured git commit message following conventional commit standards and best practices.

## Context Analysis

**Current repository status:**
!`git status --porcelain`

**Staged changes (if any):**
!`git diff --cached --stat`

**Unstaged changes (if any):**
!`git diff --stat`

**Current branch:**
!`git branch --show-current`

**Recent commit history for context:**
!`git log --oneline -5`

## Your Task

Based on the above git context, create a structured commit following these requirements:

### 1. Analyze Changes
- Review all staged and unstaged changes
- Identify the primary purpose of the changes
- Note any new files, deletions, or significant refactoring
- Assess the scope and impact of modifications

### 2. Stage Appropriate Files
- Add relevant untracked files to staging area if needed
- Ensure only intended changes are staged for commit

### 3. Generate Commit Message
Use this exact format:
```
<emoji> <type>(<scope>): <subject>

<body using bullet points if needed>

<footer if applicable>

Changed files:
New: <list of new files>
Modified: <list of modified files>
Deleted: <list of deleted files if any>
```

### Commit Message Guidelines

**Emoji Selection:**
- new feature
- bug fix
- configuration/tooling
- documentation
- refactoring
- style/formatting
- performance
- security
- tests
- deployment

**Type Classification:**
- `feat` - new feature
- `fix` - bug fix
- `docs` - documentation
- `style` - formatting, missing semi colons, etc
- `refactor` - code restructuring
- `test` - adding tests
- `chore` - maintenance tasks
- `perf` - performance improvements
- `security` - security-related changes

**Scope Examples:**
- `auth` - authentication
- `ui` - user interface
- `api` - API changes
- `config` - configuration
- `deps` - dependencies
- `build` - build system
- `ci` - continuous integration

**Subject Line:**
- Use imperative mood ("add" not "added" or "adds")
- Keep under 50 characters
- No period at the end
- Capitalize first letter

**Body (if needed):**
- Use bullet points for multiple changes
- Explain the "why" not just the "what"
- Reference issue numbers if applicable
- Keep lines under 72 characters

### 4. Execute Commit
- Run the git commit command with the generated message
- Verify the commit was created successfully
- Show final git status

## Special Instructions

${ARGUMENTS ? `**Custom message context:** ${ARGUMENTS}` : ""}

- If there are no changes to commit, report the clean status and exit
- If there are only unstaged changes, ask whether to stage them first
- Always verify the commit succeeds and show confirmation
- Include the commit hash in your final response
