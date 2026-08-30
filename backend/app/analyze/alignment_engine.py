"""Deterministic comparison of two document profiles.

Produces change items and 0-100 scores for structure, typography, layout,
formatting and visual. Semantic scoring is handled by the AI reasoner.
"""

from __future__ import annotations

import difflib
import re
from typing import Dict, List, Optional, Tuple

from ..models import ChangeItem, DocumentProfile

_counter = 0


def _next_id() -> str:
    global _counter
    _counter += 1
    return f"chg_{_counter:03d}"


def reset_ids() -> None:
    global _counter
    _counter = 0


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def _similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def _score(penalties: List[float]) -> float:
    return max(0.0, round(100.0 - sum(penalties), 1))


def compare_structure(
    master: DocumentProfile, child: DocumentProfile
) -> Tuple[List[ChangeItem], float]:
    changes: List[ChangeItem] = []
    penalties: List[float] = []

    master_headings = master.headings
    child_headings = list(child.headings)
    used: set[int] = set()
    matches: Dict[int, int] = {}

    for m_index, m_heading in enumerate(master_headings):
        best_index, best_score = -1, 0.0
        for c_index, c_heading in enumerate(child_headings):
            if c_index in used:
                continue
            score = _similar(m_heading.text, c_heading.text)
            if score > best_score:
                best_index, best_score = c_index, score

        if best_score >= 0.85:
            used.add(best_index)
            matches[m_index] = best_index
            changes.append(
                ChangeItem(
                    id=_next_id(),
                    category="structure",
                    section=m_heading.text,
                    master=m_heading.text,
                    document=child_headings[best_index].text,
                    action="none",
                    change="No change required",
                    severity="none",
                    reason="Matches the Master pattern",
                    confidence=round(best_score, 2),
                )
            )
        elif best_score >= 0.45:
            used.add(best_index)
            matches[m_index] = best_index
            penalties.append(5)
            changes.append(
                ChangeItem(
                    id=_next_id(),
                    category="structure",
                    section=m_heading.text,
                    master=m_heading.text,
                    document=child_headings[best_index].text,
                    action="modify",
                    change=f'Rename "{child_headings[best_index].text}" -> "{m_heading.text}"',
                    severity="medium",
                    reason="Section naming does not follow the Master pattern",
                    confidence=round(1 - best_score / 2, 2),
                )
            )
        else:
            penalties.append(12)
            after = master_headings[m_index - 1].text if m_index > 0 else None
            instruction = f'Add a "{m_heading.text}" section'
            if after:
                instruction += f' after "{after}"'
            changes.append(
                ChangeItem(
                    id=_next_id(),
                    category="structure",
                    section=m_heading.text,
                    master=m_heading.text,
                    document="—",
                    action="add",
                    change=instruction,
                    severity="high",
                    reason="Required Master section is absent",
                    confidence=0.93,
                )
            )

    # Ordering: matched headings must appear in the Master's relative order.
    ordered = [matches[key] for key in sorted(matches)]
    for position in range(1, len(ordered)):
        if ordered[position] < ordered[position - 1]:
            m_index = sorted(matches)[position]
            heading = master_headings[m_index]
            previous = master_headings[sorted(matches)[position - 1]]
            penalties.append(6)
            changes.append(
                ChangeItem(
                    id=_next_id(),
                    category="structure",
                    section=heading.text,
                    master=f"After \"{previous.text}\"",
                    document=f"Before \"{previous.text}\"",
                    action="move",
                    change=f'Move "{heading.text}" below "{previous.text}"',
                    severity="medium",
                    reason="Section order differs from the Master hierarchy",
                    confidence=0.9,
                )
            )

    for c_index, c_heading in enumerate(child_headings):
        if c_index in used:
            continue
        penalties.append(4)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="structure",
                section=c_heading.text,
                master="—",
                document=c_heading.text,
                action="remove",
                change=f'Remove the "{c_heading.text}" section',
                severity="low",
                reason="Section has no counterpart in the Master pattern",
                confidence=0.7,
            )
        )

    return changes, _score(penalties)


def compare_typography(
    master: DocumentProfile, child: DocumentProfile
) -> Tuple[List[ChangeItem], float]:
    changes: List[ChangeItem] = []
    penalties: List[float] = []
    m, c = master.typography, child.typography

    m_body = _describe_body(master)
    c_body = _describe_body(child)
    font_differs = bool(m.body_font and c.body_font and _normalize(m.body_font) != _normalize(c.body_font))
    size_differs = bool(
        m.body_size_pt and c.body_size_pt and abs(m.body_size_pt - c.body_size_pt) >= 0.5
    )

    if font_differs or size_differs:
        penalties.append(14 if font_differs else 8)
        target = ", ".join(
            part
            for part in [
                m.body_font,
                f"{m.body_size_pt:g} pt" if m.body_size_pt else None,
            ]
            if part
        )
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="typography",
                section="Body text",
                master=m_body,
                document=c_body,
                action="modify",
                change=f"Change body text to {target}",
                severity="high" if font_differs else "medium",
                reason="Body typography does not match the Master profile",
                confidence=0.97,
            )
        )
    else:
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="typography",
                section="Body text",
                master=m_body,
                document=c_body,
                action="none",
                change="No change required",
                severity="none",
                reason="Matches the Master pattern",
                confidence=0.95,
            )
        )

    for key, size in m.heading_sizes_pt.items():
        child_size = c.heading_sizes_pt.get(key)
        if child_size is None:
            continue
        if abs(child_size - size) >= 0.5:
            penalties.append(6)
            changes.append(
                ChangeItem(
                    id=_next_id(),
                    category="typography",
                    section=key,
                    master=f"{size:g} pt",
                    document=f"{child_size:g} pt",
                    action="modify",
                    change=f"Change {key} size to {size:g} pt",
                    severity="medium",
                    reason="Heading size does not match the Master profile",
                    confidence=0.95,
                )
            )

    if m.bold_headings and c.bold_headings is False:
        penalties.append(6)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="typography",
                section="Headings",
                master="Bold headings",
                document="Regular weight headings",
                action="modify",
                change="Set headings to bold",
                severity="low",
                reason="Master uses bold headings throughout",
                confidence=0.85,
            )
        )

    return changes, _score(penalties)


def compare_layout(
    master: DocumentProfile, child: DocumentProfile
) -> Tuple[List[ChangeItem], float]:
    changes: List[ChangeItem] = []
    penalties: List[float] = []
    m, c = master.layout, child.layout

    if m.page_size and c.page_size and m.page_size != c.page_size:
        penalties.append(12)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="layout",
                section="Page size",
                master=m.page_size,
                document=c.page_size,
                action="modify",
                change=f"Change page size to {m.page_size}",
                severity="medium",
                reason="Page size differs from the Master",
                confidence=0.96,
            )
        )

    if m.margins_in and c.margins_in:
        deltas = {
            side: abs(value - c.margins_in.get(side, value))
            for side, value in m.margins_in.items()
        }
        if any(delta >= 0.15 for delta in deltas.values()):
            penalties.append(10)
            changes.append(
                ChangeItem(
                    id=_next_id(),
                    category="layout",
                    section="Margins",
                    master=_describe_margins(m.margins_in),
                    document=_describe_margins(c.margins_in),
                    action="modify",
                    change=f"Change margins to {_describe_margins(m.margins_in)}",
                    severity="low",
                    reason="Page margins differ from the Master layout",
                    confidence=0.85,
                )
            )

    if m.body_alignment and c.body_alignment and m.body_alignment != c.body_alignment:
        penalties.append(13)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="layout",
                section="Paragraph alignment",
                master=m.body_alignment,
                document=c.body_alignment,
                action="modify",
                change=f"Change body paragraph alignment to {m.body_alignment}",
                severity="medium",
                reason="Paragraph alignment does not follow the Master layout",
                confidence=0.93,
            )
        )

    if m.line_spacing and c.line_spacing and abs(m.line_spacing - c.line_spacing) >= 0.1:
        penalties.append(8)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="layout",
                section="Line spacing",
                master=f"{m.line_spacing:g}",
                document=f"{c.line_spacing:g}",
                action="modify",
                change=f"Change line spacing to {m.line_spacing:g}",
                severity="low",
                reason="Line spacing differs from the Master layout",
                confidence=0.82,
            )
        )

    return changes, _score(penalties)


def compare_formatting(
    master: DocumentProfile, child: DocumentProfile
) -> Tuple[List[ChangeItem], float]:
    changes: List[ChangeItem] = []
    penalties: List[float] = []
    m, c = master.formatting, child.formatting

    if m.heading_numbering and not c.heading_numbering:
        penalties.append(15)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="formatting",
                section="Heading numbering",
                master="Numbered headings",
                document="Unnumbered headings",
                action="modify",
                change="Apply numbering to all headings (1, 1.1, 1.2 …)",
                severity="medium",
                reason="Master numbers every heading",
                confidence=0.9,
            )
        )
    if not m.heading_numbering and c.heading_numbering:
        penalties.append(8)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="formatting",
                section="Heading numbering",
                master="Unnumbered headings",
                document="Numbered headings",
                action="modify",
                change="Remove numbering from headings",
                severity="low",
                reason="Master headings are not numbered",
                confidence=0.85,
            )
        )

    if m.caption_position and c.caption_position and m.caption_position != c.caption_position:
        penalties.append(10)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="formatting",
                section="Captions",
                master=f"Caption {m.caption_position} figures",
                document=f"Caption {c.caption_position} figures",
                action="move",
                change=f"Move captions {m.caption_position} their figures",
                severity="low",
                reason="Caption placement differs from the Master",
                confidence=0.8,
            )
        )

    if m.table_count and not c.table_count:
        penalties.append(10)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="formatting",
                section="Tables",
                master=f"{m.table_count} table(s)",
                document="No tables",
                action="add",
                change="Add the tabular content the Master pattern expects",
                severity="low",
                reason="Master presents data in tables",
                confidence=0.6,
            )
        )

    return changes, _score(penalties)


def compare_visual(
    master: DocumentProfile, child: DocumentProfile
) -> Tuple[List[ChangeItem], float]:
    changes: List[ChangeItem] = []
    penalties: List[float] = []
    m, c = master.visual, child.visual

    if m.image_count and not c.image_count:
        penalties.append(18)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="visual",
                section="Figures",
                master=f"{m.image_count} figure(s)",
                document="No figures",
                action="add",
                change="Add the supporting figures the Master pattern expects",
                severity="low",
                reason="Master illustrates its content with figures",
                confidence=0.6,
            )
        )

    if (
        m.image_alignment
        and c.image_alignment
        and m.image_alignment != c.image_alignment
    ):
        penalties.append(12)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="visual",
                section="Figure alignment",
                master=m.image_alignment,
                document=c.image_alignment,
                action="move",
                change=f"Move figures to {m.image_alignment} alignment",
                severity="low",
                reason="Figure placement differs from the Master",
                confidence=0.75,
            )
        )

    if m.heading_color and c.heading_color and m.heading_color != c.heading_color:
        penalties.append(10)
        changes.append(
            ChangeItem(
                id=_next_id(),
                category="visual",
                section="Heading color",
                master=m.heading_color,
                document=c.heading_color,
                action="modify",
                change=f"Change heading color to {m.heading_color}",
                severity="low",
                reason="Heading color differs from the Master palette",
                confidence=0.88,
            )
        )

    return changes, _score(penalties)


def _describe_body(profile: DocumentProfile) -> str:
    parts = [
        profile.typography.body_font,
        f"{profile.typography.body_size_pt:g} pt"
        if profile.typography.body_size_pt
        else None,
        profile.layout.body_alignment,
    ]
    return ", ".join(part for part in parts if part) or "—"


def _describe_margins(margins: Dict[str, float]) -> str:
    values = {round(value, 2) for value in margins.values()}
    if len(values) == 1:
        return f'{values.pop():g}-inch margins'
    return ", ".join(f"{side} {value:g}\"" for side, value in margins.items())


def run_deterministic(
    master: DocumentProfile, child: DocumentProfile
) -> Tuple[List[ChangeItem], Dict[str, float]]:
    reset_ids()
    changes: List[ChangeItem] = []
    scores: Dict[str, float] = {}

    for key, fn in (
        ("structure", compare_structure),
        ("typography", compare_typography),
        ("layout", compare_layout),
        ("formatting", compare_formatting),
        ("visual", compare_visual),
    ):
        items, score = fn(master, child)
        changes.extend(items)
        scores[key] = score

    return changes, scores


def next_id() -> str:
    return _next_id()
