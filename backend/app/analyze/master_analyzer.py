"""Turns a raw master extraction into the display-ready Master Profile."""

from __future__ import annotations

import json
from typing import List

from ..groq_client import GroqError, chat_json
from ..models import DocumentProfile, MasterProfile, ProfileGroup
from ..prompts import load


async def build_master_profile(profile: DocumentProfile) -> MasterProfile:
    facts = _facts(profile)
    try:
        data = await chat_json(
            "master_analysis",
            [
                {"role": "system", "content": load("master_profile")},
                {
                    "role": "user",
                    "content": json.dumps(facts, ensure_ascii=False)
                    + "\n\nTEXT EXCERPT:\n"
                    + profile.text_excerpt[:6000],
                },
            ],
        )
        groups = [
            ProfileGroup(group=str(group["group"]), items=[str(i) for i in group["items"]])
            for group in data.get("groups", [])
            if group.get("items")
        ]
        if groups:
            return MasterProfile(file_name=profile.file_name, groups=groups)
    except (GroqError, KeyError, TypeError, ValueError):
        pass
    return MasterProfile(file_name=profile.file_name, groups=_fallback_groups(profile))


def _facts(profile: DocumentProfile) -> dict:
    return {
        "headings": [
            {"text": heading.text, "level": heading.level} for heading in profile.headings
        ],
        "typography": profile.typography.model_dump(),
        "layout": profile.layout.model_dump(),
        "formatting": profile.formatting.model_dump(),
        "visual": profile.visual.model_dump(),
        "terminology": profile.terminology,
        "word_count": profile.word_count,
    }


def _fallback_groups(profile: DocumentProfile) -> List[ProfileGroup]:
    groups: List[ProfileGroup] = []
    if profile.headings:
        groups.append(
            ProfileGroup(
                group="Document Structure",
                items=[heading.text for heading in profile.headings[:20]],
            )
        )

    typography = []
    if profile.typography.body_font:
        typography.append(profile.typography.body_font)
    if profile.typography.body_size_pt:
        typography.append(f"Body: {profile.typography.body_size_pt:g} pt")
    for key, size in profile.typography.heading_sizes_pt.items():
        typography.append(f"{key}: {size:g} pt")
    if profile.typography.bold_headings:
        typography.append("Bold headings")
    if typography:
        groups.append(ProfileGroup(group="Typography", items=typography))

    layout = []
    if profile.layout.page_size:
        layout.append(profile.layout.page_size)
    if profile.layout.margins_in:
        values = set(round(v, 1) for v in profile.layout.margins_in.values())
        layout.append(
            f"{values.pop():g}-inch margins"
            if len(values) == 1
            else "Custom margins"
        )
    if profile.layout.body_alignment:
        layout.append(f"{profile.layout.body_alignment.capitalize()} paragraphs")
    if profile.layout.line_spacing:
        layout.append(f"{profile.layout.line_spacing:g} line spacing")
    if layout:
        groups.append(ProfileGroup(group="Layout", items=layout))

    formatting = []
    if profile.formatting.heading_numbering:
        formatting.append("Heading numbering")
    if profile.formatting.list_styles:
        formatting.append("List styles: " + ", ".join(profile.formatting.list_styles[:3]))
    if profile.formatting.caption_position:
        formatting.append(f"Caption {profile.formatting.caption_position} figures")
    if formatting:
        groups.append(ProfileGroup(group="Formatting", items=formatting))

    if profile.terminology:
        groups.append(
            ProfileGroup(group="Language", items=profile.terminology[:8])
        )

    colors = []
    if profile.visual.heading_color:
        colors.append(f"Heading color {profile.visual.heading_color}")
    colors += [f"Accent {color}" for color in profile.visual.accent_colors[:2]]
    if colors:
        groups.append(ProfileGroup(group="Colors", items=colors))

    assets = []
    if profile.visual.image_count:
        assets.append(f"{profile.visual.image_count} image(s)")
    if profile.formatting.table_count:
        assets.append(f"{profile.formatting.table_count} table(s)")
    if assets:
        groups.append(ProfileGroup(group="Assets", items=assets))

    return groups
