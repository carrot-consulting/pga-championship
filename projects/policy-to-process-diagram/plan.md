# Plan: policy-to-process-diagram Skill

## Context

Alex needs a reusable Claude Code skill that takes a policy or procedure document and produces a process diagram, annotated with security controls and inefficiency findings. This is both a consulting productivity tool (faster client deliverables) and a potential differentiator for Carrot Consulting engagements (ISO 27001, SOC 2 Type 2, NIST).

This is a prompt-engineering task -- no code. The skill is a structured instruction file (SKILL.md) that tells Claude exactly how to behave when invoked.

---

## Files to Create

| File | Purpose |
|---|---|
| `.claude/skills/policy-to-process-diagram/SKILL.md` | The skill itself -- Claude reads this when invoked |
| `references/examples/policy-to-process-diagram-example.md` | Concrete example input + expected output to anchor quality |
| Update `projects/policy-to-process-diagram/README.md` | Mark status as Active |

---

## Diagram Format: Mermaid, Auto-Detect Type

Mermaid is the right choice -- Claude generates it natively, it renders in VS Code, GitHub, and Notion, no external tools needed. Alex can paste output directly into client reports.

Claude will auto-detect the diagram type based on the document:

| Document characteristics | Mermaid type |
|---|---|
| Single actor, linear/branching steps | `flowchart TD` |
| Multiple actors with handoffs | `sequenceDiagram` |
| State machine / lifecycle (e.g. incident states) | `stateDiagram-v2` |
| Multiple sub-processes that are phases of one flow | `flowchart TD` with `subgraph` blocks |

Claude states which type it chose and why before producing the diagram. Alex can override if needed.

**Diagram size cap:** Max ~15 nodes. For long documents, Claude focuses on the core process flow and flags what was omitted.

---

## Output Format (4 Sections, Always in This Order)

### Section 1: Process Summary
3-5 sentence paragraph: what the process is, who owns it, main actors/roles, scope. This is the client-facing context block.

### Section 2: Process Diagram
- Mermaid code block with a one-line note on diagram type chosen
- Node labels in plain English (no jargon)
- Security control steps highlighted via `classDef` (green background)
- Decision points (approvals, reviews) as diamond shapes `{}`
- If multiple distinct sub-processes: produce one diagram per sub-process

### Section 3: Security Controls Map
Table with columns: **Step Name | Control Type | Framework Reference | Strength**

- Control types: Access control, Authentication, Authorization, Logging/Audit trail, Approval gate, Encryption, Segregation of duties, Data classification
- Framework default: ISO 27001 Annex A (most common for Alex's engagements). Switch to SOC 2 or NIST if document context specifies.
- Strength rating: Strong / Adequate / Weak / Missing + one-line reason
- Flag implied controls (e.g., "the system logs access" with no mechanism/owner/frequency) as needing documentation -- these are audit risk

### Section 4: Findings and Recommendations
Two sub-sections, numbered list across both (so Alex can reference by number in client conversations):

**Inefficiencies:** Redundant steps, manual tasks that could be automated, bottlenecks, unclear ownership -- each with a recommended action.

**Control Gaps:** Missing controls, referencing specific framework control IDs (e.g., "ISO 27001 A.9.2.6") and a specific remediation (not "consider improving" -- actionable steps).

---

## SKILL.md Structure

1. **Purpose** -- what this skill does and when to use it
2. **How to Invoke** -- flexible invocation patterns (see below)
3. **Clarifying Question** -- ask once if framework context is unknown: "Is there a specific framework for this engagement (ISO 27001, SOC 2, NIST)?"
4. **Analysis Process** -- 7 explicit phases Claude works through internally before writing output
5. **Output Format** -- exact template with placeholder examples for each section
6. **Edge Case Rules** -- ambiguous steps, implied vs. missing controls, document too long, multiple sub-processes
7. **Tone and Style** -- client-facing register, specific framework references (e.g. "ISO 27001 A.9.1.1" not "access control"), actionable findings

### Analysis Process (the core of the skill)
Claude works through these phases before producing any output:
1. Read the entire document. Identify actors, steps, decisions, and documented controls.
2. Determine diagram type. State the choice.
3. Map nodes and edges mentally before writing Mermaid syntax.
4. Identify documented controls.
5. Identify implied controls (exist but undocumented -- audit risk).
6. Identify gaps and inefficiencies.
7. Assemble output in section order.

### Invocation Patterns
Any of these work:
- "Use the policy-to-process-diagram skill" (Claude asks for document if not provided)
- "Use the policy-to-process-diagram skill on [pasted text or uploaded file]"
- "Map this policy into a process diagram"
- Upload a PDF/doc and say "process diagram this"

---

## Example File: references/examples/policy-to-process-diagram-example.md

Contains a realistic fictional input (~400 words): "Access Management Procedure v1.0" for a SaaS company with:
- Actors: Employee, Line Manager, IT Admin
- Covers: Access request, approval, provisioning, periodic review
- Intentional gap: No deprovisioning trigger for role changes (ISO 27001 A.9.2.6)
- Intentional inefficiency: Manual email approval with no SLA

Full expected output follows the 4-section format. This anchors Claude's output quality across sessions and calibrates the Weak/Missing control boundary.

---

## Key Design Decisions

| Decision | Choice |
|---|---|
| Diagram format | Mermaid -- Claude-native, renders without tools |
| Diagram type | Auto-detect, stated explicitly so Alex can override |
| Framework default | ISO 27001 (Alex's most common engagement) |
| Control annotation | Mermaid `classDef` color-coding (green = control step) |
| Multiple sub-processes | Separate diagrams preferred over one giant subgraph |
| Implied controls | Explicitly flagged -- undocumented controls are audit risk |
| Findings format | Numbered list -- referenceable in client conversations |
| Example file | Yes -- anchors quality, defines Weak vs. Missing calibration |

---

## Rendering Note (for SKILL.md)

Mermaid output can be rendered at mermaid.live, pasted into a Notion page, or viewed in VS Code with the "Markdown Preview Mermaid Support" extension. Include this note in SKILL.md so it's there when Alex needs it.

---

## Verification

After creation, test by invoking: "Use the policy-to-process-diagram skill" and pasting the example input from the example file. Check that:
- Diagram type is correctly detected and stated
- Mermaid renders without syntax errors at mermaid.live
- Controls table references specific ISO 27001 Annex A controls
- Both findings from the example (email approval inefficiency + deprovisioning gap) appear in Section 4
