# DocAlign — MVP

An AI document alignment checker. Upload a **Master Document** (PDF/DOCX) and a **Document to Verify** (DOCX), get an alignment score plus a table of concrete, actionable changes.

Two deliverables in one repo:

1. **Frontend** — the React app running here (TanStack Start + Vite + Tailwind).
2. **Backend** — a complete FastAPI service written into `backend/`, which you run and deploy yourself from VS Code.

No auth, no database, no persistence. Files go straight into analysis and results live in memory for the session.

## 1. User experience

**Home (`/`)**

- Title "DocAlign", subtitle "AI Document Alignment Checker".
- Drop zone 1: MASTER DOCUMENT — PDF or DOCX.
- Down arrow.
- Drop zone 2: DOCUMENT TO VERIFY — DOCX only.
- `Analyze` button, disabled until both files are present.
- Progress states while running: Analyzing master → Analyzing document → Comparing → Building report.

**Results (`/results`)**

- Big score header: `91% ALIGNED` with a colour band.
- Six category bars: Structure, Typography, Layout, Formatting, Visual, Semantic.
- Master Profile panel (collapsible) — the extracted structure, typography, layout, formatting, language, colours, assets.
- **Change table**: Section | Master | Document | Change Required, with action badges:
  - 🟢 No change · 🟡 Modify · 🔴 Add · 🔵 Move · 🟣 Remove
- Filter chips by action and by category; a "hide no-change rows" toggle.
- Clicking a row opens a detail panel: master values, document values, status, recommendation, reason, confidence. Long text uses a compact stacked Master / Document / Change diff instead of dumping paragraphs into the table.
- Copy-report and print buttons.

Language rule: the UI never says "Child" — it says "Document to Verify". Internal field names stay `master_document` / `child_document`.

## 2. Backend (`backend/`, FastAPI)

```
backend/
  app/
    main.py                 FastAPI app, CORS, routes
    config.py               env loading, Groq key pool
    groq_client.py          4-key rotation + retry/backoff
    models.py               Pydantic: MasterProfile, DocumentProfile, ChangeItem, AlignmentReport
    extract/
      docx_extract.py       python-docx: styles, fonts, sizes, alignment, spacing,
                            section/page setup, headings, tables, lists, images, colours
      pdf_extract.py        pdfplumber/PyMuPDF: fonts, sizes, margins, alignment
                            heuristics, headings, figures
    analyze/
      master_analyzer.py    raw extraction -> Master Profile
      child_analyzer.py     same extraction -> Document Profile
      alignment_engine.py   deterministic scoring for Structure/Typography/
                            Layout/Formatting/Visual
      ai_reasoner.py        Groq pass for Semantic + change-item phrasing
      orchestrator.py       runs the whole pipeline, merges scores
    prompts/                system prompts for profile summarisation,
                            semantic alignment, change-item generation
  requirements.txt
  .env.example
  README.md                 run + deploy instructions
```

**Endpoints**

- `POST /api/analyze` — multipart `master` + `child`; returns the full report.
- `POST /api/analyze/master` — master only; returns just the Master Profile (used for the preview step).
- `GET /api/health`.

**Pipeline**

```text
Master (PDF/DOCX) -> extract -> Master Profile
Child (DOCX)      -> extract -> Document Profile
Both -> Alignment Engine (deterministic: structure, typography, layout, formatting, visual)
     -> AI Reasoner (semantic meaning, terminology, requirement strength: SHALL vs MAY)
     -> Change Items -> weighted overall score -> Report
```

**Scoring** — each category scored 0–100 from its own checks; overall is a weighted mean (Structure 25, Semantic 25, Typography 15, Layout 15, Formatting 10, Visual 10).

**Change item shape** (exactly what the UI renders):

```json
{
  "id": "chg_004",
  "category": "structure",
  "section": "Objectives",
  "master": "Objectives",
  "document": "Project Goals",
  "action": "modify",
  "change": "Rename \"Project Goals\" → \"Objectives\"",
  "severity": "medium",
  "reason": "Section naming does not follow the Master pattern",
  "confidence": 0.96
}
```

**Guardrails baked into the prompts**

- Never report a mismatch merely because wording differs — compare meaning.
- Never fabricate content. Missing concepts produce "Add a requirement covering X", not an invented paragraph.
- Every change string is an imperative action, never a label like "semantic mismatch".
- Flag meaning-changing word swaps (SHALL → MAY, must → should) as high severity.

**Groq key rotation** — `GROQ_API_KEY_1..4` in `.env`. A pool assigns one key per pipeline task (master analysis, child analysis, semantic compare, change generation) and round-robins on 429/5xx with bounded backoff. Model: `openai/gpt-oss-120b`.

## 3. Frontend technical notes

- Routes: `src/routes/index.tsx` (upload) and `src/routes/results.tsx`, each with its own head metadata.
- `VITE_API_BASE_URL` in `.env` points at your FastAPI instance (default `http://localhost:8000`).
- Report is held in a small client store and passed to the results route; a refresh returns the user to upload.
- Client-side validation: master accepts `.pdf`/`.docx`, verify document accepts `.docx` only, 20 MB cap, clear inline errors.
- Design: minimal, near-monochrome with a single accent, one distinctive typeface pairing, semantic tokens in `src/styles.css` — no hardcoded colour utilities.
- Graceful failure states if the backend is unreachable, plus a demo report so the UI is reviewable before the backend is running.

## 4. Out of scope for this version

Auth, Supabase persistence, saved master profiles, version history, auto-fix/rewrite, multi-document batches.
