---
name: accenture-pptx
description: This skill should be used when the user asks to "create an Accenture presentation", "make a PPTX", "generate a PowerPoint", "build slides", "create a deck", "make an Accenture deck", or mentions creating a branded presentation for a client.
context: fork
---

# Accenture PPTX Generator

## 1. Objective

Produce Accenture-branded PowerPoint (`.pptx`) files from natural-language requests. Source material (repo, file, URL) is analyzed by a subagent that returns a JSON array of slides; the main agent validates it and generates the deck via `accenture_theme.py`, enforcing brand colors, typography, and layout without manual formatting.

## 2. When to Use / When NOT to Use

**Use this skill when:**
- The user asks for a PowerPoint, PPTX, deck, slides, or presentation
- The user mentions Accenture branding or a client deliverable
- The user provides a topic, agenda, or content to convert into slides

**Do NOT use this skill when:**
- The user asks to *edit* an existing PPTX (use `python-pptx` directly instead)
- The user wants Google Slides, Keynote, or PDF output
- The user only wants slide content as text or markdown without generating a file

---

## 3. Prerequisites

| Requirement | Details |
|-------------|---------|
| Python | 3.10+ |
| python-pptx | `pip install python-pptx` |
| cairosvg | `pip install cairosvg` (SVG icon rendering) |
| Theme module | `scripts/accenture_theme.py` (relative to this skill's root directory) |
| Fonts | Graphik family installed on the system; PPTX opens anyway, PowerPoint substitutes if missing |
| Write access | User's home directory (`~/`) for the output file |

Verify before running:
```bash
python -c "import pptx; print('python-pptx ok')"
python -c "import cairosvg; print('cairosvg ok')"
ls scripts/accenture_theme.py
```

---

## 4. Procedure

### Step 1 — Note the theme module location

The design system is at `scripts/accenture_theme.py` (relative to this skill's root). It will be loaded in Step 4 when you need to write the script.

### Step 2 — Ask the user for parameters

Before reading any source or writing code, ask the user the following questions. Group them in a single message — do not ask one at a time.

**Always ask:**
- **Core subject**: What is this presentation about? (If not already clear from the request)
- **Audience**: Business stakeholders or a technical team?
- **Intent**: Inform, sell, align, or train?

**If the input is a project directory or codebase**, also ask:
- **What to include** (offer a checklist): README summary · architecture overview · key features · tech stack · roadmap · open issues

**If the input is a document or file**, also ask:
- **Framing**: Faithful summary, or reshaped narrative for a specific audience?

**If a client is implied but not named**, also ask:
- **Client name** for the "Prepared for" label.

If you can make a reasonable inference, state the assumption and proceed — don't block on every missing detail. Date defaults to current month + year.

### Step 2b — Analyze source material (subagent)

**Run this step only if the user provided a source to read:** a repository path, a file, a URL, or a document.

> **HARD RULE**: NEVER read or analyze the source yourself. NEVER build the slide plan in the main context. The only permitted path is: launch subagent → receive JSON → proceed. If the subagent fails twice, stop and report the error — do not fall back to self-analysis.

**Before launching**, read `references/icons.md` (relative to this skill's root). Embed its full content verbatim in the subagent prompt under an **"## Available Icons"** heading — this must appear in the prompt before the output instructions.

**Launch** an `Explore` subagent (or `general-purpose` if web/URL access is needed) using the Agent tool. Instruct the subagent to:
1. Analyze the source scoped to what the user selected in Step 2 (e.g. "README + architecture + tech stack, skip open issues")
2. Keep all bullet text ≤ 8 words
3. Frame content for the audience and intent declared in Step 2
4. Always open with `title_slide` and close with `closing_slide`
5. Insert `section_divider` between logical groups
6. Target 6–12 slides total
7. Use the **Available Icons** section embedded in this prompt (sourced from `references/icons.md`) to populate the `icon` field — set `null` if no icon matches strongly
8. Return **only** the raw JSON array — response must start with `[` and end with `]`, no prose, no markdown fences

**After the subagent returns**: verify the response starts with `[` and ends with `]`. If not, re-invoke once with: *"Return ONLY the JSON array starting with [ and ending with ]. No other text."* If it fails again, stop and report to the user.

#### Slide JSON Schema

Every slide is one object with **exactly these 8 fields** — all always present, unused ones set to `null`:

```json
{
  "slide_type": "title_slide | section_divider | content_slide | closing_slide",
  "title":    "string",
  "subtitle": "string | null",
  "layout":   "bullet_list | two_column | card_grid | null",
  "icon":     "analyze | investigate | compare | goal | intelligence | ai_chip | agent | metrics | dashboard | engineering | null",
  "bullets":  ["string"] | null,
  "columns":  [{"heading": "string", "bullets": ["string"]}, {"heading": "string", "bullets": ["string"]}] | null,
  "cards":    [{"heading": "string", "bullets": ["string"]}] | null
}
```

**Field usage by type:**

| `slide_type`      | `layout` | `bullets` | `columns` | `cards` | `icon` |
|-------------------|----------|-----------|-----------|---------|--------|
| `title_slide`     | null     | null      | null      | null    | null   |
| `section_divider` | null     | null      | null      | null    | null   |
| `content_slide`   | `bullet_list` | ✓   | null      | null    | opt.   |
| `content_slide`   | `two_column`  | null | ✓ (2)   | null    | opt.   |
| `content_slide`   | `card_grid`   | null | null    | ✓ (2–4)| null   |
| `closing_slide`   | null     | null      | null      | null    | null   |

**Minimal example (6-slide deck):**

```json
[
  {"slide_type": "title_slide",     "title": "AI Agent Platform", "subtitle": "Prepared for Banca Generali · March 2026", "layout": null, "icon": null, "bullets": null, "columns": null, "cards": null},
  {"slide_type": "section_divider", "title": "01 — The Challenge", "subtitle": "Context and pain points", "layout": null, "icon": null, "bullets": null, "columns": null, "cards": null},
  {"slide_type": "content_slide",   "title": "Current Pain Points", "subtitle": null, "layout": "bullet_list", "icon": "analyze", "bullets": ["Manual processes slow throughput", "Siloed data limits AI potential", "No unified audit trail"], "columns": null, "cards": null},
  {"slide_type": "content_slide",   "title": "Three Core Capabilities", "subtitle": null, "layout": "card_grid", "icon": null, "bullets": null, "columns": null, "cards": [{"heading": "Ingest", "bullets": ["Real-time multi-source ingestion"]}, {"heading": "Process", "bullets": ["LLM orchestration + agent routing"]}, {"heading": "Deliver", "bullets": ["API-first output with audit trail"]}]},
  {"slide_type": "content_slide",   "title": "Before vs After", "subtitle": null, "layout": "two_column", "icon": "compare", "bullets": null, "columns": [{"heading": "Before", "bullets": ["Slow manual review", "High error rate"]}, {"heading": "After", "bullets": ["Automated pipeline", "99% accuracy"]}], "cards": null},
  {"slide_type": "closing_slide",   "title": "Thank You", "subtitle": "contact@accenture.com", "layout": null, "icon": null, "bullets": null, "columns": null, "cards": null}
]
```

### Step 3 — Validate and complete the slide plan

**If Step 2b ran:** the JSON array from the subagent is your deck plan. Validate it:
- First slide is `title_slide`, last is `closing_slide`
- Total slides 6–12 (unless user specified otherwise)
- Each `content_slide` has a consistent `layout` + the matching field populated (`bullets`, `columns`, or `cards`)
- Correct any violations before proceeding — do not ask the user, fix silently

**If Step 2b did NOT run** (no source material, user described the content directly): outline the deck yourself:
- Slide 1: `title_slide` — always first
- Middle: `section_divider` between logical groups, `content_slide` for body slides
- Last slide: `closing_slide` — always last
- Target **6–12 slides** unless the user specifies otherwise
- Produce the same JSON array format before writing any code

**Choosing the right layout per slide:**

| Content type | Layout to use |
|--------------|---------------|
| Sequential or hierarchical points | `bullet_list` |
| Two contrasting groups (before/after, pros/cons) | `two_column` |
| 2–4 parallel concepts of equal weight | `card_grid` |
| Dense narrative or many points | `bullet_list` (split across slides if needed) |

**Card grid rules — decide autonomously:**
- Use a card grid **only** when the concepts are truly parallel and comparable (e.g. three pillars, four phases, N components)
- Number of cards = number of concepts (2, 3, or 4) — **never pad with empty cards to reach a fixed count**
- Card height: always compute with `Card.auto_height(bullets, card_w)` per card, then take the max across all cards
- If any card would exceed ~3.5 in height (many long bullets), switch to `bullet_list` instead

### Step 4 — Generate and run the Python script from the JSON plan

Iterate over the JSON array from Step 3. For each slide object, call the corresponding `SlideFactory` method and populate it using the non-null fields.

Read `scripts/accenture_theme.py` and `scripts/template.py` from this skill's root directory to load the design system and the reference template. Then write and run the generation script.

### Step 4b — Render icons from the JSON plan

For each slide where `icon` is non-null, call `Draw.icon(slide, slide["icon"], left, top, size)`.

Placement rules:
- Size: 1.0–1.5 in
- Position: bottom-right of the content area — `top ≈ zones["content_top"] + zones["content_height"] - size`
- For `bullet_list` slides: reduce bullet width by ~2.5 in to leave room on the right

Icon selection was already handled by the subagent in Step 2b. Do not re-evaluate icon choices here.

### Step 5 — Report the result

After saving, tell the user the **exact absolute path** of the generated file.

---

## 5. Expected Output

| Item | Details |
|------|---------|
| File | `<headline-slug>.pptx` saved to `~/` (or custom path if specified) |
| Slide count | 6–12 slides: title → sections → content → closing |
| Branding | Accenture purple `#A000FF`, Graphik font, `>` brand mark, tagline |
| File naming | Slugify the headline — lowercase, spaces→hyphens, strip special chars |

Example: headline `"AI Strategy 2026"` → `~/ai-strategy-2026.pptx`

---

## 6. Do / Don't

| | |
|---|---|
| **DO** | Use `Colors.*` constants for all colors |
| **DO** | Use `Typography.SIZE["body"]` etc. for font sizes |
| **DO** | Use `Layout.GUTTER` for element spacing |
| **DO** | Keep bullet text ≤ 8 words |
| **DO** | Always include `title_slide` + `closing_slide` |
| **DO** | Use `section_divider` to separate logical groups |
| **DO** | Save output to `~/` by default |
| **DO** | Report the exact saved path to the user |
| **DON'T** | Hardcode hex values like `"#A000FF"` |
| **DON'T** | Hardcode raw pt numbers |
| **DON'T** | Use arbitrary spacing values |
| **DON'T** | Write full long sentences as bullets |
| **DON'T** | Start or end the deck with a `content_slide` |
| **DON'T** | Cram all content into a single section |
| **DON'T** | Save to absolute paths like `/home/<user>/` |
| **DON'T** | Save silently without confirming |

---

## 7. Golden Path Example

A complete example showing the expected flow from request to output.

---

**User:** "Create a deck on our AI agent platform for a client demo"

---

**Skill (Step 2 — asking parameters):**

> A few quick questions before I start:
>
> 1. **Audience** — business stakeholders or a technical team?
> 2. **Intent** — sell/demo, inform, or align?
> 3. **Client name** — who is the deck prepared for? (for the "Prepared for" label)

---

**User:** "Business stakeholders, it's a sales demo. Client is Banca Generali."

---

**Skill (Step 3 — slide outline, stated before coding):**

> Here's the structure I'll use:
>
> | # | Type | Title |
> |---|------|-------|
> | 1 | `title_slide` | AI Agent Platform — Banca Generali |
> | 2 | `section_divider` | 01 — The Challenge |
> | 3 | `content_slide` | Current Pain Points *(bullet_list)* |
> | 4 | `section_divider` | 02 — Our Solution |
> | 5 | `content_slide` | Platform Overview *(bullet_list + `agent` icon)* |
> | 6 | `content_slide` | Three Core Capabilities *(card_grid, 3 cards)* |
> | 7 | `section_divider` | 03 — Why Accenture |
> | 8 | `content_slide` | Track Record & Methodology *(two_column)* |
> | 9 | `content_slide` | Next Steps *(bullet_list + `goal` icon)* |
> | 10 | `closing_slide` | Thank You |

---

**Skill (Step 4 — writes and runs the script, then reports):**

> Saved: `~/ai-agent-platform-banca-generali.pptx`

---

## 8. Troubleshooting

### `ModuleNotFoundError: No module named 'pptx'`
**Cause:** `python-pptx` is not installed in the active Python environment.
**Fix:** Run `pip install python-pptx`. If using a virtualenv, activate it first, then retry.

---

### `ModuleNotFoundError: No module named 'accenture_theme'`
**Cause:** The `sys.path.insert` path is wrong or the skill's `scripts/` directory is missing.
**Fix:** Confirm the file exists:
```bash
ls scripts/accenture_theme.py
```
If missing, reinstall the skill. The path in `sys.path.insert` must be exactly `os.path.expanduser("~/.claude/skills/accenture-pptx/scripts")`.

---

### Slide text appears in the wrong font (not Graphik)
**Cause:** The Graphik font family is not installed on the operating system.
**Fix:** Install the Graphik fonts, or temporarily override `Typography.PRIMARY = "Calibri"` at the top of your script. The PPTX file will open correctly; PowerPoint/LibreOffice will substitute the nearest available font.

---

### `PermissionError` when saving the file
**Cause:** The output path is not writable (read-only directory, stale file handle, or path collision).
**Fix:** Change the output path to an explicitly writable location:
```python
out = os.path.expanduser("~/Desktop/output.pptx")
```

---

### Cards or columns overflow or get clipped
**Cause:** Too many bullet items for the available content height, or font size too large.
**Fix:** Reduce content per slide (split into two slides), or drop one font size step — e.g. change `Typography.SIZE["body"]` to `Typography.SIZE["small"]`.
