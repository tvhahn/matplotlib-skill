---
allowed-tools: Bash(git log:*), Bash(git config:*), Bash(date:*), Bash(git branch:*), Bash(mkdir:*), Write
argument-hint: [date-info] [context/purpose description]
description: Generate professional timesheet entry from git history for a specific date
---

# Timesheet Generator

Generate a professional timesheet summary from git commits for the specified date.

**Arguments**: $ARGUMENTS

## Context

- Current git user: !`git config user.name`
- Current branch: !`git branch --show-current`

## Instructions

You are creating a timesheet entry for a project manager who is not technical. 

**Step 1: Parse the date**
From the arguments "$ARGUMENTS", intelligently extract:
1. The target date (could be in formats like "September 11, 2025", "last Thursday", "2025-09-11", etc.)
2. Any context about what the work focused on

**Step 2: Get git history**
Use git log to get detailed commit history for that specific date. Use the format:
```bash
git log --since="YYYY-MM-DD 00:00:00" --until="YYYY-MM-DD 23:59:59" --author="$(git config user.name)" --all
```

**Step 3: Generate timesheet summary**

Create the timesheet folder if it doesn't exist:
```bash
mkdir -p timesheets
```

Generate the timesheet content in this format:

```
## Work Summary - [Date]

[Executive summary paragraph starting with "Focused on..." that explains the main themes and objectives of the day's development work. Keep it 2-3 sentences max.]

• [Business-friendly bullet point describing what was accomplished - integrate the git commit purpose into natural language]
• [Another bullet point for the next major task/commit]
• [Continue for each significant piece of work]

**Focus Areas**: [Comma-separated list of key technical areas worked on]

**Proposed Titles**:
1. [Short, professional title option 1]
2. [Short, professional title option 2]
3. [Short, professional title option 3]
```

**Step 4: Save timesheet**

Save the timesheet to a file in the timesheets folder with the format:
- Filename: `timesheets/YYYY-MM-DD-[brief-context].md`
- Example: `timesheets/2025-09-11-agent-workflow-development.md`
- Use kebab-case for the context portion and keep it concise (2-4 words)

**Formatting Guidelines:**
- Executive summary should start with "Focused on..." 
- Remove all technical jargon and commit hash references
- Convert technical tasks into business value language
- Do not include timestamps in bullet points
- Do not include bullet point section headings - integrate the work type naturally into the description
- Make each bullet point focus on the accomplishment, not the process
- Extract 3-6 key focus areas that summarize the technical domains
- For proposed titles: keep them concise (5-10 words), focus on business value not technical details, and make them suitable for timesheet/project tracking systems

**Example transformation:**
- Git commit: "🐛 fix(dev): resolve HTTP request logging issues in Pydantic AI integration"
- Timesheet entry: "• Resolved critical issues with API request logging and monitoring to ensure complete visibility into AI service interactions"

If no commits are found for the specified date, clearly state this and suggest checking the date format or git history.