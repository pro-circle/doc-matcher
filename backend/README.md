# DocAlign — FastAPI backend

Analyzes a **Master Document** (PDF/DOCX) and a **Document to Verify** (DOCX),
and returns an alignment report: category scores plus actionable change items.

## Run locally

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then paste your four Groq keys
uvicorn app.main:app --reload --port 8000
```

Point the frontend at it with `VITE_API_BASE_URL=http://localhost:8000`.

## Endpoints

| Method | Path                  | Body                       | Returns          |
| ------ | --------------------- | -------------------------- | ---------------- |
| GET    | `/api/health`         | —                          | status + key count |
| POST   | `/api/analyze/master` | multipart `master`         | `MasterProfile`  |
| POST   | `/api/analyze`        | multipart `master`, `child`| `AlignmentReport`|

## Pipeline

```
Master (PDF/DOCX) --extract--> raw profile ─┐
                                            ├─> Alignment Engine (deterministic)
Child  (DOCX)     --extract--> raw profile ─┘        structure / typography /
                                                     layout / formatting / visual
                                            └─> AI Reasoner (Groq)
                                                     semantic meaning + terminology
                                            └─> Change phrasing pass (Groq)
                                            └─> Weighted score -> AlignmentReport
```

Weights: Structure 25, Semantic 25, Typography 15, Layout 15, Formatting 10, Visual 10.

## Groq key rotation

`GROQ_API_KEY_1..4` are loaded into a pool. Each pipeline task
(`master_analysis`, `child_analysis`, `semantic_compare`, `change_generation`)
starts on its own key; on 429/5xx the request rotates to the next key with
bounded exponential backoff (max 4 attempts). 400/401/403 are terminal.
Fewer than four keys still works — tasks share what is available.

Model: `openai/gpt-oss-120b` (override with `GROQ_MODEL`).

## Guardrails

The prompts enforce that the AI:

- compares **meaning**, not exact wording;
- never fabricates content — a missing concept produces "Add a statement covering X";
- emits imperative instructions ("Rename X → Y"), never labels ("semantic mismatch");
- treats meaning-changing word swaps (SHALL → MAY) as high severity.

If Groq is unreachable, deterministic scoring still returns a full report and
the master profile falls back to rule-based extraction.

## Deploy

Any container/VM host works, e.g.:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Set `CORS_ORIGINS` to your deployed frontend origin.
