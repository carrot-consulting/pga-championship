# Skill: Security Review

Scan the latest activity log for security risks. Rate findings by severity: Critical / High / Medium / Low.

---

## How to Invoke

- "Run security review"
- "Security scan the activity log"
- "Review today's work for risks"
- "Security review of yesterday's session"

---

## Workflow

### Step 1: Identify the target activity log

Default: the most recent file in `archives/activity-log/` (sort by filename -- newest date wins).

If the user specifies a date, use `archives/activity-log/YYYY-MM-DD.md`.

Read the full activity log file.

### Step 2: Pull changed files from git

Cross-reference the commits in the activity log. For each file that was Added or Modified, read its current contents to inspect for risks -- don't rely on filenames alone.

### Step 3: Analyze for risks

Check across these categories:

| Category | What to look for |
|---|---|
| Secrets / credentials | API keys, tokens, passwords hardcoded in any tracked file |
| Personal / business data | Full name, location, client details, revenue figures in committed files |
| Gitignore gaps | Sensitive files that exist on disk but aren't excluded |
| Insecure patterns | Hardcoded values that should come from env, missing input validation |
| Third-party integrations | New MCP servers, external APIs, or dependencies added -- assess trust level |
| Permission / access changes | Changes to settings.json, .claude/ config, or system-level files |

### Step 4: Rate each finding

| Severity | Meaning |
|---|---|
| Critical | Immediate risk -- secret exposed, data leaking, action required now |
| High | Significant risk -- should be fixed before next session |
| Medium | Moderate risk -- worth addressing, not urgent |
| Low | Informational -- best practice gap, low impact |

### Step 5: Produce the report

```markdown
# Security Review — YYYY-MM-DD
_Activity log reviewed: archives/activity-log/YYYY-MM-DD.md_

## Summary
X critical, X high, X medium, X low

## Findings

### Critical
**[Title]**
- File: `path/to/file`
- Risk: description
- Action: what to do

### High
...

### Medium
...

### Low
...

## No Issues Found
(list any categories explicitly checked and cleared)
```

### Step 6: Save

Save to `archives/security-review/YYYY-MM-DD.md`.

Tell the user the file path and headline counts (e.g. "1 critical, 2 medium, 1 low").

---

## Edge Cases

- **No activity log exists:** Tell the user and ask if they want to generate one first
- **No issues found:** Still save the report -- a clean bill of health is worth recording
- **User specifies a past date:** Use the corresponding activity log file
