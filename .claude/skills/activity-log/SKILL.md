# Skill: Activity Log

Generate an end-of-day summary of everything done in this session, sourced from git history and context files.

---

## How to Invoke

- "Generate activity log"
- "End of day summary"
- "Log today's session"
- "What did we do today?"

---

## Template

Use `templates/activity-log.md` as the structure for all activity log outputs.

---

## Workflow

### Step 1: Gather git data

Run the following to get today's commits and file changes:

```bash
git -C /Users/alexsimonin/Desktop/max log --since="midnight" --pretty=format:"%h %s" --name-status
```

If no commits exist today, note that and still produce a summary from context.

### Step 2: Load context

Read these files:
- `context/current-priorities.md` -- to determine the Focus field and frame the session
- `decisions/log.md` -- pull any entries added today for the Decisions Logged field

### Step 3: Produce the summary

Follow the structure in `templates/activity-log.md`:

- **Date / Focus** -- today's date (DD-MM-YY) and a 1-line description of the session's main theme
- **Commits** -- list each commit hash and message
- **What Got Done** -- for each file in Added / Modified / Deleted, write a brief explanation of *what it is and why*, not just the filename
- **Open Items / Next Steps** -- anything started but not finished, or logical next actions
- **Memory Updates** -- preferences learned, decisions logged (from `decisions/log.md`), rules created

### Step 4: Save

Save to `archives/activity-log/DD-MM-YY.md`.

Tell the user the file path after saving.

---

## Security

Never write the following into the activity log:
- API keys, tokens, passwords, or any credential values
- Client names or identifying details
- Revenue figures or contract values
- Any content that would be sensitive if read by a third party

Reference these things by type only (e.g. "API key updated" not "API key `abc123` updated").

---

## Edge Cases

- **No commits today:** Note it, but still summarize any session work described by the user or visible from context
- **Multiple sessions in one day:** Append to the existing file rather than overwriting
- **User specifies a different date:** Use that date for the git query and filename
