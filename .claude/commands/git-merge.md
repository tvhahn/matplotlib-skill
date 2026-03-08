---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git branch:*), Bash(git merge-base:*), Bash(git merge-tree:*), Bash(git merge:*), Bash(git rev-parse:*), Bash(git shortlog:*), Bash(git show:*), Bash(git checkout -- :*), Bash(git merge --abort), Bash(git reset:*), Read, Grep, Glob, AskUserQuestion
description: Analyze git merge scenarios with conflict detection and interactive resolution guidance
argument-hint: <source-branch> [into <target-branch>]
---

# Git Merge Command

Analyze and execute git merges with intelligent conflict detection, risk assessment, and interactive resolution guidance.

## Context Analysis

**Current repository status:**
!`git status --porcelain`

**Current branch:**
!`git branch --show-current`

**Recent commit history:**
!`git log --oneline -5`

**Available local branches:**
!`git branch --format='%(refname:short)' | head -20`

**Available remote branches:**
!`git branch -r --format='%(refname:short)' | head -10`

**Mid-merge state check:**
!`git rev-parse -q --verify MERGE_HEAD 2>/dev/null && echo "MERGE_IN_PROGRESS" || echo "NO_MERGE_IN_PROGRESS"`

## Input Parameters

- **Source branch** (required): The branch to merge FROM
- **Target branch** (optional): The branch to merge INTO (defaults to current branch)

**Argument format:** `<source-branch>` or `<source-branch> into <target-branch>`

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : "**No arguments provided** - you must ask which branch to merge"}

## Your Task

Complete these phases in order:

---

### Phase 1: Pre-Flight Checks & Argument Parsing

#### 1.1 Parse Arguments
- If `into <target>` is specified, use `<target>` as target branch
- Otherwise, target is the current branch
- If no arguments provided, use `AskUserQuestion` to ask which branch to merge

#### 1.2 Validate Environment
Check for blocking conditions:

| Condition | Check Command | Recovery Action |
|-----------|---------------|-----------------|
| Dirty working tree | `git status --porcelain` has output | "Please commit or stash changes first" |
| Mid-merge state | MERGE_HEAD exists | "Complete or abort current merge: `git merge --abort`" |
| Source branch missing | Branch not in local or remote | List available branches |
| Target branch missing | Branch not found | List available branches |

---

### Phase 2: Merge Analysis

#### 2.1 Find Common Ancestor
```bash
git merge-base <target-branch> <source-branch>
```

#### 2.2 Analyze Divergence
```bash
git log --oneline <target>..<source>
git log --oneline <source>..<target>
git shortlog -sn <target>..<source>
```

#### 2.3 Identify Changed Files
```bash
git diff --name-only $(git merge-base <target> <source>)..<source>
git diff --name-only $(git merge-base <target> <source>)..<target>
```

#### 2.4 Preview Conflicts with merge-tree
```bash
git merge-tree --write-tree --no-messages <target> <source> 2>&1
```

#### 2.5 Present Analysis Summary

---

### Phase 3: Conflict Deep-Dive (if conflicts detected)

For each conflicting file, categorize the conflict type, show three-way context, and provide interactive resolution guidance using `AskUserQuestion`.

---

### Phase 4: Merge Execution

Confirm merge strategy with user (--no-ff recommended), execute the merge, and handle any conflicts.

---

### Phase 5: Post-Merge Verification

Verify merge success, check for residual conflict markers, and display summary.

---

### Phase 6: Post-Merge Actions (Optional)

Offer to run tests, push to remote, or delete source branch.

---

## Important Notes

- **NEVER use `-i` flags** (interactive modes are not supported)
- **NEVER use `--no-edit`** with rebase commands
- **Always preserve ORIG_HEAD** for recovery
- **Use merge-tree for conflict preview** - it doesn't modify the working tree
- **Document all user decisions** during conflict resolution for audit trail
