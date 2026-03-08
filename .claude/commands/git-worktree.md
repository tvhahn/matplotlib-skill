---
allowed-tools: Bash(*)
description: Create a git worktree with dev container config and gitignored files copied for parallel development
argument-hint: <branch-name> [destination-path]
---

# Git Worktree Setup

Create a new git worktree for parallel development, copying necessary configuration files and setting up the Python environment.

## Environment Context

**Repository root:**
!`git rev-parse --show-toplevel`

**Repository name:**
!`basename $(git rev-parse --show-toplevel)`

**Current branch:**
!`git branch --show-current`

**Existing worktrees:**
!`git worktree list`

**Available local branches:**
!`git branch --format='%(refname:short)' | head -15`

**Available remote branches (sample):**
!`git branch -r --format='%(refname:short)' | head -10`

**Gitignored files to copy (if they exist):**
!`for f in .env .claude/settings.local.json deploy/.env.azure; do [ -f "$f" ] && echo "$f"; done`

## Input Parameters

- **Branch name** (required): `$1`
- **Destination path** (optional): `$2`

## Your Task

Complete these steps in order:

### Step 1: Validate Input

1. Verify branch name `$1` is provided - if not, show usage and exit
2. Check if branch exists locally or on remote

### Step 2: Determine Destination Path

If `$2` is provided, use it. Otherwise:
- Remove common prefixes: `claude/`, `feature/`, `fix/`, `bugfix/`, `hotfix/`
- Remove random suffixes (like `-WJp2Z`)
- Build destination: `../<repo-name>-<short-name>`

### Step 3: Create the Worktree

```bash
git worktree add <destination-path> <branch-name>
```

### Step 4: Copy Gitignored Configuration Files

Copy `.env`, `.claude/settings.local.json`, `deploy/.env.azure` if they exist.

### Step 5: Add Port Overrides to .env

Calculate unique ports based on worktree count to avoid conflicts.

### Step 6: Fix Hardcoded Ports in docker-compose.yml

Check and fix any hardcoded ports in docker-compose.yml.

### Step 7: Add Git Mount for Devcontainer

Add volume mount for main repo's `.git` directory so git works inside the devcontainer.

### Step 8: Customize Devcontainer Name

Update devcontainer.json name to be unique for VS Code.

### Step 9: Display Summary

Show location, branch, ports, copied files, and next steps.

## Error Handling

- If branch doesn't exist: List available branches and exit
- If destination already exists: Show error and suggest different path
- If worktree creation fails: Show git error message
- If file copy fails: Continue (files are optional), note which failed

## Example Usage

```bash
# Auto-derived destination
/git-worktree claude/add-table-metadata-WJp2Z
# Creates: ../account-research-table-metadata

# Custom destination
/git-worktree feature/new-api ~/Documents/api-worktree

# Remote branch that doesn't exist locally yet
/git-worktree origin/main-v2
```
