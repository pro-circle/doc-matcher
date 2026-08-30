# Doc Matcher

Yes — that makes the product much cleaner.

We should deliberately remove the enterprise/document-governance complexity for the first version.

DocAlign — Simple Core Product

Input

Master Document

.docx

.pdf

Child Document

.docx only

Output

Does the Child Document follow the Master Document's pattern, structure, formatting and semantic rules?

Not:

"Are the two documents identical?"

1. Exact workflow

          MASTER DOCUMENT
          DOCX / PDF
               │
               ▼
       ┌─────────────────┐
       │ Analyze Master  │
       └────────┬────────┘
                │
                ▼
        MASTER PROFILE
                │
                │
                ▼
        CHILD DOCUMENT
             DOCX
                │
                ▼
       ┌─────────────────┐
       │ Analyze Child   │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Compare Against │
       │ Master Profile  │
       └────────┬────────┘
                │
                ▼
       ┌─────────────────┐
       │ Alignment Score │
       └────────┬────────┘
                │
                ▼
          FINAL REPORT

That's it.

2. What the Master teaches the AI

We don't need complicated "memory" initially.

When the Master is uploaded, extract its document profile.

Example

MASTER PROFILE
────────────────────────────

Document Structure
✓ Title
✓ Introduction
✓ Objectives
✓ Methodology
✓ Results
✓ Conclusion
✓ References

Typography
✓ Arial
✓ Body: 11 pt
✓ Heading 1: 16 pt
✓ Heading 2: 14 pt
✓ Bold headings

Layout
✓ A4
✓ 1-inch margins
✓ Justified paragraphs
✓ 1.15 line spacing

Formatting
✓ Heading numbering
✓ Consistent spacing
✓ Centered figures
✓ Caption below figures

Language
✓ British English
✓ Defined terminology

Colors
✓ Heading color
✓ Table styling
✓ Accent color

Assets
✓ Images
✓ Tables

This becomes the Master Profile.

3. Then upload the Child Document

The Child document goes through the same analysis.

For example:

CHILD DOCUMENT
────────────────────────────

Structure
✓ Title
✓ Introduction
✓ Objectives
⚠ Methodology
✓ Results
✓ Conclusion
✓ References

Typography
✓ Arial
⚠ Body: 12 pt
✓ Heading 1: 16 pt
✓ Heading 2: 14 pt

Layout
✓ A4
✓ Margins
⚠ Paragraph alignment
✓ Line spacing

4. The AI doesn't compare exact text

This is the most important rule.

Suppose Master:

"The proposed system provides intelligent monitoring of industrial machinery."

Child:

"Our system enables intelligent monitoring for heavy machinery."

We shouldn't report:

❌ Content mismatch.

Instead:

Semantic Pattern
────────────────────

Master concept:
Intelligent monitoring of machinery

Child concept:
Intelligent monitoring of machinery

Meaning:
✓ Aligned

5. What should actually be compared?

I'd keep it to 6 categories.

CategoryWhat we checkStructureSections, headings, order, hierarchyTypographyFont, size, bold, italicLayoutAlignment, margins, spacing, positioningFormattingTables, lists, captions, numberingVisualColors, images, basic visual placementSemanticMeaning, terminology, required concepts

That's enough for a very powerful first version.

6. Example result

Imagine the Master says:

Heading:
16px Arial Bold
Left aligned

Body:
11px Arial
Justified
1.15 spacing

Child has:

Heading:
16px Arial Bold
Left aligned ✓

Body:
12px Arial
Left aligned ❌
1.15 spacing ✓

The result:

╔══════════════════════════════════════╗
║          ALIGNMENT RESULT             ║
║                                       ║
║              91%                      ║
║             ALIGNED                   ║
║                                       ║
╠══════════════════════════════════════╣
║ Structure             ✓ 100%          ║
║ Typography            ⚠  94%          ║
║ Layout                ⚠  87%          ║
║ Formatting            ✓  96%          ║
║ Visual                ✓  93%          ║
║ Semantic              ✓  98%          ║
╚══════════════════════════════════════╝

Then:

Issues

⚠ BODY TEXT

Master:
Arial — 11 pt — Justified

Child:
Arial — 12 pt — Left aligned

Recommended:
Change body text to Arial 11 pt
Change alignment to Justified

7. The UI should be extremely simple

I'd make the homepage almost stupidly simple.

┌─────────────────────────────────────────────┐
│                                             │
│                 DocAlign                    │
│     AI Document Alignment Checker           │
│                                             │
│                                             │
│       MASTER DOCUMENT                       │
│                                             │
│    ┌───────────────────────────────┐        │
│    │                               │        │
│    │    Drop PDF / DOCX here       │        │
│    │                               │        │
│    └───────────────────────────────┘        │
│                                             │
│                                             │
│                 ↓                           │
│                                             │
│       CHILD DOCUMENT                        │
│                                             │
│    ┌───────────────────────────────┐        │
│    │                               │        │
│    │    Drop DOCX here             │        │
│    │                               │        │
│    └───────────────────────────────┘        │
│                                             │
│                                             │
│             [ Analyze ]                     │
│                                             │
└─────────────────────────────────────────────┘

That's basically the entire input experience.

8. Results page

After analysis:
Instead of showing only:

❌ Font mismatch
⚠ Alignment mismatch

the result should directly show what in the document needs to change, while the Master acts as the reference.

Result table

For example:

SectionMaster DocumentDocument to VerifyResult / Change RequiredTitleMachineShield EdgeMachineShield🔴 Change "MachineShield" → "MachineShield Edge"IntroductionPresentMissing🔴 Add "Introduction" sectionObjectivesObjectivesProject Goals🟡 Rename "Project Goals" → "Objectives"MethodologyPresent after ObjectivesPresent before Objectives🔴 Move "Methodology" below "Objectives"System ArchitecturePresentArchitecture🟡 Rename "Architecture" → "System Architecture"ConclusionPresentPresent🟢 No changeBody textArial, 11 pt, justifiedTimes New Roman, 12 pt, left🔴 Change to Arial, 11 pt, justifiedFigure 1Center alignedLeft aligned🟡 Move Figure 1 → centerTerminologyArtificial IntelligenceArtificial inteligence🔴 Change "inteligence" → "intelligence"

This is far more actionable.

The result page

I'd make the main result screen something like:

┌─────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT ALIGNMENT                          │
│                                                                     │
│                         91% ALIGNED                                 │
│                                                                     │
├──────────────┬────────────────────┬────────────────────┬────────────┤
│ SECTION      │ MASTER             │ DOCUMENT           │ CHANGE     │
├──────────────┼────────────────────┼────────────────────┼────────────┤
│ Title        │ MachineShield Edge │ MachineShield      │ Change     │
│              │                    │                    │ "Machine- │
│              │                    │                    │ Shield" →  │
│              │                    │                    │ "Machine-  │
│              │                    │                    │ Shield     │
│              │                    │                    │ Edge"      │
├──────────────┼────────────────────┼────────────────────┼────────────┤
│ Introduction │ Introduction       │ —                  │ Add        │
│              │                    │                    │ "Introduc- │
│              │                    │                    │ tion"      │
├──────────────┼────────────────────┼────────────────────┼────────────┤
│ Objectives   │ Objectives         │ Project Goals      │ Rename     │
│              │                    │                    │ "Project    │
│              │                    │                    │ Goals" →   │
│              │                    │                    │ "Objectives"│
├──────────────┼────────────────────┼────────────────────┼────────────┤
│ Methodology  │ Section 3          │ Section 2          │ Move       │
│              │                    │                    │ Section 2  │
│              │                    │                    │ → Section 3│
├──────────────┼────────────────────┼────────────────────┼────────────┤
│ Conclusion   │ Conclusion         │ Conclusion         │ ✓ No change│
└──────────────┴────────────────────┴────────────────────┴────────────┘

But I'd make one important distinction

The Result / Change Required column should contain the actual actionable modification.

Not:

❌ Semantic mismatch

Instead:

Change "Project Goals" → "Objectives"

Not:

❌ Missing section

Instead:

Add "Introduction" after "Abstract"

Not:

❌ Wrong ordering

Instead:

Move "Methodology" after "Objectives"

Not:

❌ Content differs

Instead:

Replace "The proposed system monitors machines" with a statement covering the Master requirement for real-time monitoring.

That makes the AI genuinely useful.

For longer content

We shouldn't dump entire paragraphs into the table.

Use a compact diff:

Master
────────────────────────────
The system shall provide
real-time monitoring of
machine conditions.

Document
────────────────────────────
The system provides
machine monitoring.

Change
────────────────────────────
Add the missing requirement:

"real-time monitoring of
machine conditions"

Or:

Master:
"The system SHALL authenticate
users before access."

Document:
"The system MAY authenticate
users before access."

🔴 Change:
"MAY" → "SHALL"

This is particularly powerful because the AI is identifying a meaning-changing word, not just a textual difference.

Result categories

I'd keep the result column to four actions:

🟢 No Change

No change required.

🟡 Modify

Change "Project Goals" → "Objectives"

🔴 Add

Add "References" section after "Conclusion"

🔵 Move

Move "Methodology" below "Objectives"

Potentially:

🟣 Remove

Remove "Appendix" section.

So the user can scan the entire document quickly.

The AI pipeline changes slightly

Instead of generating a generic score first:

Master
  ↓
Understand
  ↓
Master rules/profile
  ↓
Understand new document
  ↓
Compare
  ↓
Generate CHANGE ITEMS
  ↓
Result table

Each change item should have a structured representation:

{
  "section": "Objectives",
  "master": "Objectives",
  "document": "Project Goals",
  "action": "rename",
  "change": "\"Project Goals\" → \"Objectives\"",
  "severity": "medium",
  "reason": "Section naming does not follow the Master pattern",
  "confidence": 0.96
}

Then the UI simply renders these change objects.

And the most important rule

The AI should not invent content.

If the Master says:

System shall provide real-time monitoring.

and the new document doesn't contain that concept, the AI can say:

Add the missing requirement related to real-time monitoring.

But it shouldn't automatically fabricate an entire paragraph unless we explicitly add an AI Rewrite/Auto-Fix feature later.

So the MVP remains:

Find → Identify → Show exact section/word → Recommend the change.

That's a much cleaner and more trustworthy product.

9. Detailed issue

Clicking an issue:

BODY TEXT ALIGNMENT

Master Document
────────────────────
Font: Arial
Size: 11 pt
Alignment: Justified
Spacing: 1.15

Child Document
────────────────────
Font: Arial
Size: 11 pt
Alignment: Left

Status
────────────────────
⚠ Alignment mismatch

Recommendation
────────────────────
Change body paragraph alignment
from LEFT → JUSTIFIED.

No unnecessary AI jargon.

10. Architecture can also stay simple

We don't need 10 microservices.

I'd start with:

                 React.js
                    │
                    ▼
                 FastAPI
                    │
           ┌────────┴────────┐
           ▼                 ▼
     Master Analyzer    Child Analyzer
           │                 │
           └────────┬────────┘
                    ▼
             Alignment Engine
                    │
                    ▼
               AI Reasoner
                    │
                    ▼
                 Report

Backend

Python + FastAPI.

Frontend

Next.js + TypeScript.

Document processing

DOCX/PDF extraction.

AI

One good LLM initially.

Storage

For MVP, we can even avoid a database.

Upload Master
      ↓
Analyze
      ↓
Master Profile
      ↓
Upload Child
      ↓
Compare
      ↓
Result

Once we need saved Master profiles, then add a database.

11. One thing I strongly recommend

Don't call the second document "Child" in the UI.

Internally, sure, we can call it:

master_document
child_document

But user-facing language should be:

Master Document

and

Document to Verify

That immediately tells the user what they're doing.

So:

MASTER DOCUMENT
PDF / DOCX

DOCUMENT TO VERIFY
DOCX

Much more professional.

12. The core intelligence

The entire application can basically be reduced to:

MASTER
   ↓
Extract
   ↓
Understand
   ↓
Create Master Profile
   ↓
          ┌───────────────┐
          │               │
          ▼               ▼
       Structure       Semantics
          │               │
          ▼               ▼
       Formatting       Content
          │               │
          └───────┬───────┘
                  ▼
             ALIGNMENT
                  │
                  ▼
             Differences
                  │
                  ▼
           Recommendations

And your key principle remains:

The Child does not need to contain the same words as the Master. It needs to follow the Master’s intended structure, rules, style, alignment and meaning.

That's a clear, focused product.

I would build exactly this MVP first, get the comparison accuracy right, and only afterward consider things like persistent memory, multiple Masters, Auto-Fix, version history, or multimedia.
- Suggested tech stack
1. React.js (Tanstack, vite, tailwind css)
2. Fast API
3. Groq api keys (openai-gpt-oss-120b (4 key rotation or each key for each task))
4. No lovable cloud use Supabase db for storing master and child doc (using browser keys).
5. Keep the ui simple and minimal and upgrade later.
6. Keys in .env
7. No auth and registration for now.
8. Must support ms word pdf as master doc and only ms word as child.
9. Use Powerful orchestration and .dekiverable
A powerful mvp with core feature

This project was built with [Lovable](https://lovable.dev).

## Build with Lovable

Continue developing this project in the [Lovable editor](https://lovable.dev/projects/2d68d65a-91f7-43bc-a9ba-83fcf261182f).

- **Ship faster**: describe what you want to build and Lovable handles the code.
- **Stay in sync**: every change made in Lovable is committed straight to this repository.
- **Full ownership**: this code is yours. Push to `main` on GitHub and your changes sync back into Lovable, ready for your next prompt.

## Development

Prefer working locally? You need Node.js and npm — [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating).

```sh
git clone <this-repository-url>
cd <repository-name>
npm i
npm run dev
```
