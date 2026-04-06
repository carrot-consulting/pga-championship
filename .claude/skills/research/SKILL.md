# Skill: Research

Use this skill when Alex asks for research, information gathering, or wants to understand a topic in depth.

**Powered by:** Brave Search MCP (`brave_web_search`)

---

## Setup

Brave Search requires an API key exported in your shell environment:

```bash
# Add to ~/.zshrc (one time)
export BRAVE_API_KEY=your_key_here
```

Get your API key at brave.com/search/api. The key itself lives in `.env` in this workspace.

---

## How to Invoke

- "Research [topic]"
- "Use the research skill to look into [topic]"
- "Do a deep dive on [topic]"
- "Quick search on [topic]"

---

## Step 1: Clarify Before Searching (Always)

Before running any search, ask these three questions in a single message:

1. **What exactly do you want to know?** (restate the question to confirm understanding)
2. **What's this for?** (client meeting, personal decision, project planning, general curiosity, etc.)
3. **Quick answer or deep dive?**
   - Quick: fast summary, 1-3 searches
   - Deep dive: thorough, cross-referenced, structured report

Wait for answers before proceeding.

---

## Step 2: Load Context

Based on the query type, read the relevant context files before searching:

| Query type | Load these files |
|---|---|
| Work / client / security / compliance | `context/work.md`, `context/current-priorities.md`, `context/goals.md` |
| Personal (cooking, travel, gardening, sports) | `context/personal-life.md` |
| Mixed or unclear | All four context files |

Also check `projects/` -- if an active project is directly relevant to the query, read its `README.md` for added specificity.

Use this context to:
- Frame search queries through Alex's specific lens
- Filter and prioritize results that are relevant to his work or interests
- Connect findings back to what he's currently working on

---

## Step 3: Research

**Quick (1-3 searches):**
- Run focused, targeted searches
- Skim results for the most relevant points

**Deep dive (4-8 searches):**
- Search across multiple angles: overview, trends, tools/solutions, risks, examples
- For work topics: prioritize sources relevant to SaaS, cybersecurity, ISO 27001, SOC 2, NIST
- For personal topics: prioritize practical, actionable sources
- Cross-reference findings -- flag conflicts rather than picking one side

Cap at 8 searches per session.

---

## Step 4: Output

### Quick answer

- 3-5 bullet findings
- 1-2 sentence **So what** -- why this matters for Alex specifically

### Deep dive

**1. Research Brief**
What was searched, what context was loaded, what angle was applied.

**2. Key Findings**
Bullets grouped by theme. Each finding tied to a source.

**3. Relevance to Alex**
How this connects to his current priorities, active projects, or Carrot Consulting work. Be specific -- don't just summarize, connect.

**4. Recommended Actions**
Concrete next steps. Not "consider looking into X" -- specific actions Alex can take.

**5. Sources**
List of URLs used.

---

## Edge Cases

- **Clearly personal query** (recipe, gardening, travel): skip work context files
- **Clearly work query** (ISO 27001, client research, security tools): skip personal context
- **Conflicting information in results**: flag the conflict explicitly and present both sides
- **Too broad a question**: narrow it down during the clarify step before searching
