"""Pydantic models shared by the pipeline and the API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

CategoryKey = Literal[
    "structure", "typography", "layout", "formatting", "visual", "semantic"
]
ChangeAction = Literal["none", "modify", "add", "move", "remove"]
Severity = Literal["none", "low", "medium", "high"]

CATEGORY_LABELS: Dict[str, str] = {
    "structure": "Structure",
    "typography": "Typography",
    "layout": "Layout",
    "formatting": "Formatting",
    "visual": "Visual",
    "semantic": "Semantic",
}

CATEGORY_WEIGHTS: Dict[str, int] = {
    "structure": 25,
    "semantic": 25,
    "typography": 15,
    "layout": 15,
    "formatting": 10,
    "visual": 10,
}


class Heading(BaseModel):
    text: str
    level: int = 1
    order: int = 0


class Typography(BaseModel):
    body_font: Optional[str] = None
    body_size_pt: Optional[float] = None
    heading_fonts: Dict[str, str] = Field(default_factory=dict)
    heading_sizes_pt: Dict[str, float] = Field(default_factory=dict)
    bold_headings: Optional[bool] = None


class Layout(BaseModel):
    page_size: Optional[str] = None
    margins_in: Dict[str, float] = Field(default_factory=dict)
    body_alignment: Optional[str] = None
    line_spacing: Optional[float] = None


class Formatting(BaseModel):
    heading_numbering: Optional[bool] = None
    list_styles: List[str] = Field(default_factory=list)
    table_count: int = 0
    caption_position: Optional[str] = None


class Visual(BaseModel):
    image_count: int = 0
    image_alignment: Optional[str] = None
    heading_color: Optional[str] = None
    accent_colors: List[str] = Field(default_factory=list)


class DocumentProfile(BaseModel):
    """Raw extraction result for either document."""

    file_name: str
    source_type: Literal["docx", "pdf"]
    headings: List[Heading] = Field(default_factory=list)
    typography: Typography = Field(default_factory=Typography)
    layout: Layout = Field(default_factory=Layout)
    formatting: Formatting = Field(default_factory=Formatting)
    visual: Visual = Field(default_factory=Visual)
    sections: Dict[str, str] = Field(default_factory=dict)
    terminology: List[str] = Field(default_factory=list)
    word_count: int = 0
    text_excerpt: str = ""


class ProfileGroup(BaseModel):
    group: str
    items: List[str]


class MasterProfile(BaseModel):
    """Human-readable master profile rendered in the UI."""

    file_name: str
    groups: List[ProfileGroup] = Field(default_factory=list)


class ChangeItem(BaseModel):
    id: str
    category: CategoryKey
    section: str
    master: str
    document: str
    action: ChangeAction
    change: str
    severity: Severity = "medium"
    reason: str = ""
    confidence: float = 0.8


class CategoryScore(BaseModel):
    key: CategoryKey
    label: str
    score: float


class AlignmentReport(BaseModel):
    overall_score: float
    verdict: str
    master_file: str
    document_file: str
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    categories: List[CategoryScore]
    master_profile: MasterProfile
    changes: List[ChangeItem]
