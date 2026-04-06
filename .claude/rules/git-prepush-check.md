# Rule: Git Pre-Push Security Check

Before any `git push`, scan all staged and modified tracked files for the following. Flag findings and confirm with Alex before proceeding.

---

## What to Scan For

### Secrets & Credentials
- API keys, tokens, passwords, or secrets in any tracked file
- Anything that looks like a credential, even if the variable name seems innocent

### Personal Information
- Full name (Alex Simonin) in files that weren't already tracking it
- Location, timezone, or contact details
- Travel plans, financial details, or health information

### Business-Sensitive Data
- Client names, contract details, or revenue figures
- Engagement scope or pricing information

### Gitignored Files That Slipped Through
- `.env` -- should never be committed
- `.mcp.json` -- should never be committed
- `CLAUDE.local.md` -- should never be committed
- `research-output/` -- should never be committed
- Any file matching patterns in `.gitignore`

### Inappropriate for a Public Repo
- Internal notes, draft strategies, or anything that would be embarrassing or harmful if public
- Private research outputs or client-adjacent findings

---

## How to Handle Findings

1. **Stop the push**
2. List each finding clearly: file, line, what was found, severity
3. Ask Alex to confirm before proceeding
4. If Alex confirms it's safe, proceed. If not, remove the sensitive content and re-stage.

---

## What Does Not Need Flagging

- Changes to `.gitignore` that add new exclusions (safe by definition)
- Changes to files already known to contain public-safe information (e.g. `context/personal-life.md` interests section)
- Binary files (logos, images) unless the filename suggests sensitivity
