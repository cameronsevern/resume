#!/usr/bin/env python3
"""Render a small, ATS-friendly Markdown subset into a polished PDF resume."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


DASH_TRANSLATION = str.maketrans(
    {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",
    }
)


def normalize(value: str) -> str:
    return value.translate(DASH_TRANSLATION).strip()


def inline_markup(value: str) -> str:
    value = html.escape(normalize(value), quote=True)
    value = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<link href="\2" color="#174A68">\1</link>',
        value,
    )
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", value)
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    return value


def register_fonts() -> tuple[str, str]:
    candidates = [
        (
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ),
        (
            Path("/Library/Fonts/Arial.ttf"),
            Path("/Library/Fonts/Arial Bold.ttf"),
        ),
    ]
    for regular, bold in candidates:
        if regular.exists() and bold.exists():
            pdfmetrics.registerFont(TTFont("ResumeSans", str(regular)))
            pdfmetrics.registerFont(TTFont("ResumeSans-Bold", str(bold)))
            return "ResumeSans", "ResumeSans-Bold"
    return "Helvetica", "Helvetica-Bold"


def build_styles() -> dict[str, ParagraphStyle]:
    regular, bold = register_fonts()
    base = getSampleStyleSheet()
    ink = colors.HexColor("#17242D")
    accent = colors.HexColor("#174A68")
    muted = colors.HexColor("#52636F")
    return {
        "name": ParagraphStyle(
            "ResumeName",
            parent=base["Normal"],
            fontName=bold,
            fontSize=20.5,
            leading=22.5,
            textColor=ink,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
        "headline": ParagraphStyle(
            "ResumeHeadline",
            parent=base["Normal"],
            fontName=bold,
            fontSize=9.7,
            leading=11.8,
            textColor=accent,
            alignment=TA_CENTER,
            tracking=0.5,
            spaceAfter=3,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8.7,
            leading=10.5,
            textColor=muted,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "section": ParagraphStyle(
            "ResumeSection",
            parent=base["Normal"],
            fontName=bold,
            fontSize=10.6,
            leading=12.1,
            textColor=accent,
            spaceBefore=6.5,
            spaceAfter=2.5,
        ),
        "entry": ParagraphStyle(
            "ResumeEntry",
            parent=base["Normal"],
            fontName=bold,
            fontSize=9.7,
            leading=11.5,
            textColor=ink,
            spaceBefore=4,
            spaceAfter=1.4,
        ),
        "meta": ParagraphStyle(
            "ResumeMeta",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8.65,
            leading=10.3,
            textColor=muted,
            spaceAfter=2.5,
        ),
        "body": ParagraphStyle(
            "ResumeBody",
            parent=base["Normal"],
            fontName=regular,
            fontSize=9.15,
            leading=11.55,
            textColor=ink,
            alignment=TA_LEFT,
            spaceAfter=3,
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet",
            parent=base["Normal"],
            fontName=regular,
            fontSize=8.9,
            leading=11.15,
            textColor=ink,
            leftIndent=0,
            firstLineIndent=0,
            spaceAfter=1.8,
        ),
    }


def parse_markdown(markdown: str, styles: dict[str, ParagraphStyle]):
    lines = [normalize(line.rstrip()) for line in markdown.splitlines()]
    story = []
    index = 0
    name_seen = False
    headline_seen = False
    contact_seen = False

    while index < len(lines):
        line = lines[index]
        if not line:
            index += 1
            continue

        if line == "<!-- pagebreak -->":
            story.append(PageBreak())
            index += 1
            continue

        if line == "---":
            story.append(HRFlowable(width="100%", thickness=0.45, color=colors.HexColor("#9EABB3")))
            index += 1
            continue

        if line.startswith("# "):
            story.append(Paragraph(inline_markup(line[2:]), styles["name"]))
            name_seen = True
            index += 1
            continue

        if line.startswith("## "):
            story.append(Paragraph(inline_markup(line[3:].upper()), styles["section"]))
            story.append(HRFlowable(width="100%", thickness=0.55, color=colors.HexColor("#9EB4C0"), spaceAfter=2.5))
            index += 1
            continue

        if line.startswith("### "):
            story.append(Paragraph(inline_markup(line[4:]), styles["entry"]))
            index += 1
            continue

        if line.startswith("- "):
            items = []
            while index < len(lines) and lines[index].startswith("- "):
                items.append(
                    ListItem(
                        Paragraph(inline_markup(lines[index][2:]), styles["bullet"]),
                        leftIndent=0,
                    )
                )
                index += 1
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    start="circle",
                    leftIndent=10,
                    bulletFontName="Helvetica",
                    bulletFontSize=4.5,
                    bulletOffsetY=1.2,
                    spaceAfter=2,
                )
            )
            continue

        if line.startswith("*") and line.endswith("*"):
            story.append(Paragraph(inline_markup(line), styles["meta"]))
            index += 1
            continue

        if name_seen and not headline_seen:
            story.append(Paragraph(inline_markup(line), styles["headline"]))
            headline_seen = True
            index += 1
            continue

        if name_seen and headline_seen and not contact_seen:
            story.append(Paragraph(inline_markup(line), styles["contact"]))
            contact_seen = True
            index += 1
            continue

        story.append(Paragraph(inline_markup(line), styles["body"]))
        index += 1

    return story


def draw_continuation_footer(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#52636F"))
    canvas.drawRightString(
        LETTER[0] - 0.58 * inch,
        0.22 * inch,
        f"Cameron Severn | Page {document.page}",
    )
    canvas.restoreState()


def render(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    markdown = source.read_text(encoding="utf-8")
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=LETTER,
        rightMargin=0.58 * inch,
        leftMargin=0.58 * inch,
        topMargin=0.48 * inch,
        bottomMargin=0.48 * inch,
        title="Cameron Severn - Resume",
        author="Cameron Severn",
        subject="Resume",
        creator="Markdown resume workspace",
    )
    story = parse_markdown(markdown, styles)
    doc.build(story, onLaterPages=draw_continuation_footer)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    render(args.source, args.destination)
    print(args.destination)


if __name__ == "__main__":
    main()
