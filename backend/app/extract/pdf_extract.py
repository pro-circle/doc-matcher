"""PDF extraction: fonts, sizes, margins, headings and figure heuristics."""

from __future__ import annotations

import io
import re
from collections import Counter
from typing import Dict, List

import pdfplumber

from ..models import (
    DocumentProfile,
    Formatting,
    Heading,
    Layout,
    Typography,
    Visual,
)

PAGE_SIZES_IN = {"A4": (8.27, 11.69), "Letter": (8.5, 11.0), "Legal": (8.5, 14.0)}
NUMBERED_HEADING = re.compile(r"^\s*\d+(\.\d+)*[.)]?\s+\S")
CAPTION = re.compile(r"^\s*(figure|fig\.|table)\s*\d+", re.I)
MAX_PAGES = 60


def _page_size(width_pt: float, height_pt: float) -> str:
    width_in, height_in = width_pt / 72, height_pt / 72
    for name, (width, height) in PAGE_SIZES_IN.items():
        if abs(width - width_in) < 0.2 and abs(height - height_in) < 0.3:
            return name
    return f"{width_in:.2f}\" x {height_in:.2f}\""


def _clean_font(name: str) -> str:
    return re.sub(r"^[A-Z]{6}\+", "", name).split(",")[0].replace("-", " ").strip()


def extract_pdf(data: bytes, file_name: str) -> DocumentProfile:
    headings: List[Heading] = []
    body_fonts: Counter[str] = Counter()
    body_sizes: Counter[float] = Counter()
    heading_fonts: Dict[str, str] = {}
    heading_sizes: Dict[str, float] = {}
    alignments: Counter[str] = Counter()
    line_gaps: List[float] = []
    caption_positions: List[str] = []
    sections: Dict[str, List[str]] = {}
    current_section = "Preamble"
    all_text: List[str] = []
    image_count = 0
    numbered_headings = 0
    page_size = None
    margins = {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
    order = 0
    bold_headings: List[bool] = []
    previous_line_had_image = False

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        pages = pdf.pages[:MAX_PAGES]
        if pages:
            page_size = _page_size(pages[0].width, pages[0].height)

        min_x0, max_x1, min_top, max_bottom = [], [], [], []

        for page in pages:
            image_count += len(page.images)
            image_tops = [image["top"] for image in page.images]
            lines = page.extract_text_lines(extra_attrs=["fontname", "size"]) or []
            if lines:
                min_x0.append(min(line["x0"] for line in lines))
                max_x1.append(max(line["x1"] for line in lines))
                min_top.append(min(line["top"] for line in lines))
                max_bottom.append(max(line["bottom"] for line in lines))

            body_size = Counter(
                round(char["size"], 1)
                for line in lines
                for char in line.get("chars", [])
            ).most_common(1)
            common_size = body_size[0][0] if body_size else 11.0

            previous_bottom = None
            for line in lines:
                text = (line.get("text") or "").strip()
                if not text:
                    continue
                all_text.append(text)
                chars = line.get("chars", [])
                size = round(
                    sum(char["size"] for char in chars) / max(len(chars), 1), 1
                )
                font = _clean_font(chars[0]["fontname"]) if chars else "Unknown"
                is_bold = "bold" in (chars[0]["fontname"].lower() if chars else "")

                if previous_bottom is not None:
                    gap = line["top"] - previous_bottom
                    if 0 <= gap < 40:
                        line_gaps.append(gap)
                previous_bottom = line["bottom"]

                is_heading = size >= common_size + 1.2 or (
                    is_bold and len(text) < 90 and not text.endswith(".")
                )
                if is_heading and len(text) < 120:
                    order += 1
                    level = 1 if size >= common_size + 3 else 2
                    headings.append(Heading(text=text, level=level, order=order))
                    heading_fonts.setdefault(f"Heading {level}", font)
                    heading_sizes.setdefault(f"Heading {level}", size)
                    bold_headings.append(is_bold)
                    if NUMBERED_HEADING.match(text):
                        numbered_headings += 1
                    current_section = text
                    sections.setdefault(current_section, [])
                    previous_line_had_image = any(
                        abs(top - line["top"]) < 120 for top in image_tops
                    )
                    continue

                body_fonts[font] += 1
                body_sizes[size] += 1
                sections.setdefault(current_section, []).append(text)

                if CAPTION.match(text):
                    caption_positions.append(
                        "below"
                        if any(top < line["top"] for top in image_tops)
                        else "above"
                    )

                left_gap = line["x0"] - page.bbox[0]
                right_gap = page.bbox[2] - line["x1"]
                center_offset = abs(left_gap - right_gap)
                if center_offset < 12 and left_gap > 40:
                    alignments["center"] += 1
                elif right_gap < 12:
                    alignments["justified"] += 1
                else:
                    alignments["left"] += 1
                previous_line_had_image = False

        if min_x0 and pages:
            page = pages[0]
            margins = {
                "left": round(sum(min_x0) / len(min_x0) / 72, 2),
                "right": round(
                    (page.width - sum(max_x1) / len(max_x1)) / 72, 2
                ),
                "top": round(sum(min_top) / len(min_top) / 72, 2),
                "bottom": round(
                    (page.height - sum(max_bottom) / len(max_bottom)) / 72, 2
                ),
            }

    body_size_pt = body_sizes.most_common(1)[0][0] if body_sizes else None
    line_spacing = None
    if line_gaps and body_size_pt:
        average_gap = sum(line_gaps) / len(line_gaps)
        line_spacing = round(max(1.0, average_gap / body_size_pt), 2)

    return DocumentProfile(
        file_name=file_name,
        source_type="pdf",
        headings=headings,
        typography=Typography(
            body_font=body_fonts.most_common(1)[0][0] if body_fonts else None,
            body_size_pt=body_size_pt,
            heading_fonts=heading_fonts,
            heading_sizes_pt=heading_sizes,
            bold_headings=(sum(bold_headings) > len(bold_headings) / 2)
            if bold_headings
            else None,
        ),
        layout=Layout(
            page_size=page_size,
            margins_in=margins,
            body_alignment=alignments.most_common(1)[0][0] if alignments else None,
            line_spacing=line_spacing,
        ),
        formatting=Formatting(
            heading_numbering=numbered_headings > max(1, len(headings) // 2),
            list_styles=[],
            table_count=0,
            caption_position=Counter(caption_positions).most_common(1)[0][0]
            if caption_positions
            else None,
        ),
        visual=Visual(image_count=image_count),
        sections={
            name: "\n".join(lines)[:4000] for name, lines in sections.items() if lines
        },
        terminology=_terminology(all_text),
        word_count=sum(len(line.split()) for line in all_text),
        text_excerpt="\n".join(all_text)[:12000],
    )


def _terminology(lines: List[str]) -> List[str]:
    counter: Counter[str] = Counter()
    pattern = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b")
    for line in lines:
        for match in pattern.findall(line):
            counter[match] += 1
    return [term for term, count in counter.most_common(20) if count > 1]
