"""Groq-backed semantic reasoning and change-instruction phrasing."""

from __future__ import annotations

import json
from typing import List, Tuple

from ..groq_client import GroqError, chat_json
from ..models import ChangeItem, DocumentProfile
from ..prompts import load

MAX_ITEMS_FOR_PHRASING = 40


async def semantic_alignment(
    master: DocumentProfile, child: DocumentProfile, next_id
) -> Tuple[List[ChangeItem], float]:
    payload = {
        "master": {
            "sections": _trim(master.sections),
            "terminology": master.terminology[:20],
        },
        "document": {
            "sections": _trim(child.sections),
            "terminology": child.terminology[:20],
        },
    }
    try:
        data = await chat_json(
            "semantic_compare",
            [
                {"role": "system", "content": load("semantic_alignment")},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            max_tokens=6000,
        )
    except GroqError:
        return [], 100.0

    score = float(data.get("score", 100))
    items: List[ChangeItem] = []
    for raw in data.get("changes", []) or []:
        try:
            items.append(
                ChangeItem(
                    id=next_id(),
                    category="semantic",
                    section=str(raw.get("section", "Content"))[:120],
                    master=str(raw.get("master", "—"))[:400],
                    document=str(raw.get("document", "—"))[:400],
                    action=raw.get("action", "modify"),
                    change=str(raw.get("change", "")).strip() or "Review this section",
                    severity=raw.get("severity", "medium"),
                    reason=str(raw.get("reason", ""))[:300],
                    confidence=float(raw.get("confidence", 0.8)),
                )
            )
        except Exception:  # skip malformed entries rather than fail the run
            continue

    return items, max(0.0, min(100.0, score))


async def phrase_changes(changes: List[ChangeItem]) -> List[ChangeItem]:
    """Second Groq pass: turn findings into natural, actionable instructions."""
    actionable = [item for item in changes if item.action != "none"][
        :MAX_ITEMS_FOR_PHRASING
    ]
    if not actionable:
        return changes

    payload = [
        {
            "id": item.id,
            "category": item.category,
            "section": item.section,
            "master": item.master,
            "document": item.document,
            "action": item.action,
            "change": item.change,
            "reason": item.reason,
        }
        for item in actionable
    ]

    try:
        data = await chat_json(
            "change_generation",
            [
                {"role": "system", "content": load("change_phrasing")},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            max_tokens=6000,
        )
    except GroqError:
        return changes

    if not isinstance(data, list):
        return changes

    by_id = {item.id: item for item in changes}
    for raw in data:
        item = by_id.get(str(raw.get("id")))
        if not item:
            continue
        change = str(raw.get("change", "")).strip()
        reason = str(raw.get("reason", "")).strip()
        if change:
            item.change = change[:300]
        if reason:
            item.reason = reason[:300]
    return changes


def _trim(sections: dict) -> dict:
    return {name: text[:1500] for name, text in list(sections.items())[:25]}
