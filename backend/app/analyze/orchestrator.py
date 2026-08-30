"""Runs the full DocAlign pipeline."""

from __future__ import annotations

import asyncio
from typing import Tuple

from ..extract import extract_docx, extract_pdf
from ..models import (
    CATEGORY_LABELS,
    CATEGORY_WEIGHTS,
    AlignmentReport,
    CategoryScore,
    DocumentProfile,
    MasterProfile,
)
from . import alignment_engine, ai_reasoner
from .child_analyzer import analyze_child
from .master_analyzer import build_master_profile


def extract_master(data: bytes, file_name: str) -> DocumentProfile:
    lower = file_name.lower()
    if lower.endswith(".pdf"):
        return extract_pdf(data, file_name)
    if lower.endswith(".docx"):
        return extract_docx(data, file_name)
    raise ValueError("Master document must be a .pdf or .docx file")


async def analyze_master_only(data: bytes, file_name: str) -> MasterProfile:
    raw = await asyncio.to_thread(extract_master, data, file_name)
    return await build_master_profile(raw)


async def run_pipeline(
    master_data: bytes,
    master_name: str,
    child_data: bytes,
    child_name: str,
) -> AlignmentReport:
    master_raw, child_raw = await asyncio.gather(
        asyncio.to_thread(extract_master, master_data, master_name),
        asyncio.to_thread(analyze_child, child_data, child_name),
    )

    # Master profile summarisation and semantic comparison run on separate keys.
    changes, scores = alignment_engine.run_deterministic(master_raw, child_raw)

    master_profile, (semantic_changes, semantic_score) = await asyncio.gather(
        build_master_profile(master_raw),
        ai_reasoner.semantic_alignment(master_raw, child_raw, alignment_engine.next_id),
    )

    changes.extend(semantic_changes)
    scores["semantic"] = semantic_score

    changes = await ai_reasoner.phrase_changes(changes)
    changes = _sort(changes)

    overall = sum(scores[key] * weight for key, weight in CATEGORY_WEIGHTS.items()) / sum(
        CATEGORY_WEIGHTS.values()
    )

    return AlignmentReport(
        overall_score=round(overall, 1),
        verdict=_verdict(overall),
        master_file=master_name,
        document_file=child_name,
        categories=[
            CategoryScore(key=key, label=CATEGORY_LABELS[key], score=round(scores[key], 1))
            for key in ("structure", "typography", "layout", "formatting", "visual", "semantic")
        ],
        master_profile=master_profile,
        changes=changes,
    )


SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "none": 3}
CATEGORY_ORDER = {
    "structure": 0,
    "semantic": 1,
    "typography": 2,
    "layout": 3,
    "formatting": 4,
    "visual": 5,
}


def _sort(changes) -> list:
    return sorted(
        changes,
        key=lambda item: (
            SEVERITY_ORDER.get(item.severity, 4),
            CATEGORY_ORDER.get(item.category, 9),
            item.section.lower(),
        ),
    )


def _verdict(score: float) -> str:
    if score >= 90:
        return "Aligned"
    if score >= 75:
        return "Mostly aligned"
    if score >= 55:
        return "Partially aligned"
    return "Not aligned"
