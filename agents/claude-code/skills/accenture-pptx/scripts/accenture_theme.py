"""
Accenture Brand Theme for python-pptx
======================================
Reusable design system implementing Accenture's official visual identity.

Brand Identity:
  - Primary color:  Accenture Purple (#A000FF)
  - Dark purple:    #7500C1 (headings on light backgrounds)
  - Background:     White / Light Gray (#F5F5F5) or Near-Black (#1A1A1A)
  - Typography:     Graphik family (Regular, Semibold, Light, SemiboldItalic)
  - Brand mark:     ">" (greater-than symbol — Accenture's signature element)
  - Tagline:        "Engineering the Future. Transforming Business."
  - Design ethos:   Bold · Optimistic · Energetic · Dimensional · Fresh

Layout conventions:
  - Left margin: 0.42 in
  - Header zone: Title y=0.15 → Breadcrumb y=0.71 → Purple rule y=1.07
  - Content starts: y=1.35
  - Logo wordmark (white PNG): bottom-right, x=11.3, y=6.667 (1.594 × 0.421 in)
  - Chevron badge (purple PNG): bottom-left, x=0.417, y=7.089 (0.21 × 0.22 in)
  - Status bar: tagline text at bottom-right

Usage:
  from accenture_theme import Theme, SlideFactory

  prs, factory = Theme.new_presentation()
  factory.title_slide("The Future of Finance", "Digital Transformation", client="Client Name")
  factory.section_divider("Current State Assessment", "01")
  slide, zones = factory.content_slide("Key Findings")
  factory.closing_slide()
  prs.save("output.pptx")

Slide Types:
  - title_slide        Two-panel dark layout with large ">" and white headline
  - section_divider    Left dark panel + right purple panel with section title
  - content_slide      White bg, standard header (title → breadcrumb → rule)
  - closing_slide      Dark "THANK YOU" layout mirroring the title slide
"""

from __future__ import annotations

import io
import os
from typing import List, Optional, Tuple

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt, Emu

# ──────────────────────────────────────────────────────────────────────────────
# ASSETS
# ──────────────────────────────────────────────────────────────────────────────

_ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")

def _asset(name: str) -> str:
    """Return the absolute path to a bundled asset file."""
    return os.path.normpath(os.path.join(_ASSETS, name))


class Assets:
    """
    Catalog of bundled brand assets.

    Backgrounds
    -----------
    Use as full-slide image layers (place before other shapes).

    Icons
    -----
    All icons share the same visual style: Accenture-purple outline on transparent
    background, ~70–90 px native size. Place bottom-right of the content area,
    size ≈ 1.0–1.5 in.

      "analyze"      — magnifying glass          → analysis, research, search, findings
      "investigate"  — browser + magnifier        → data investigation, discovery
      "compare"      — scales / balance           → evaluation, trade-offs, comparison
      "goal"         — flag + bullseye            → objectives, KPIs, results, targets
      "intelligence" — head with circuits         → AI thinking, cognitive tasks, insights
      "ai_chip"      — CPU chip labelled "AI"     → ML models, AI processing, architecture
      "agent"        — hand with circuit dots     → agentic AI, human-AI interaction
      "metrics"      — line chart with nodes      → trends, KPIs, performance, growth
      "dashboard"    — pie chart on monitor       → reporting, analytics, dashboards
      "engineering"  — wrench + screwdriver       → technical, maintenance, tooling, fix
    """

    BACKGROUNDS = {
        "gradient_purple": "gradient_background_purple.png",
    }

    ICONS = {
        "analyze":      "analyze_icon_1.svg",      # magnifying glass
        "investigate":  "analyze_icon_2.svg",      # browser + magnifier
        "compare":      "compare_icon.svg",        # scales
        "goal":         "goal_objective_icon.png", # flag + bullseye (PNG only)
        "intelligence": "agent_icon_3.svg",        # head with circuits
        "ai_chip":      "agent_icon_2.svg",        # CPU chip (AI)
        "agent":        "agent_icon_1.svg",        # hand with circuits
        "metrics":      "chart_icon_1.svg",        # line chart
        "dashboard":    "chart_icon_2.svg",        # pie chart on monitor
        "engineering":  "fix_icon_1.svg",          # wrench + screwdriver
    }


# ──────────────────────────────────────────────────────────────────────────────
# BRAND COLORS
# ──────────────────────────────────────────────────────────────────────────────

class Colors:
    """Accenture official color palette."""

    # Primary
    PURPLE       = RGBColor(0xA0, 0x00, 0xFF)   # Accenture Purple (#A000FF) – innovation, ambition
    BLACK        = RGBColor(0x00, 0x00, 0x00)   # Pure Black – strength, security
    WHITE        = RGBColor(0xFF, 0xFF, 0xFF)   # White – clarity, openness

    # Neutrals
    LIGHT_GRAY   = RGBColor(0xF5, 0xF5, 0xF5)   # Slide backgrounds, subtle tones
    MID_GRAY     = RGBColor(0x80, 0x80, 0x80)   # Secondary / caption text
    DARK_GRAY    = RGBColor(0x33, 0x33, 0x33)   # Primary body text
    NEAR_BLACK   = RGBColor(0x1A, 0x1A, 0x1A)   # Dark panels, slightly softer than black

    # Purple variants
    PURPLE_LIGHT      = RGBColor(0xF9, 0xEF, 0xFF)   # Lightest purple tint (#F9EFFF) – card backgrounds
    PURPLE_EXTRA_LIGHT = RGBColor(0xF5, 0xE5, 0xFF)  # Extra-light purple tint (#F5E5FF) – subtle fills
    PURPLE_MID        = RGBColor(0x6C, 0x22, 0xDD)   # Vibrant mid-purple (#6C22DD) – accent highlights
    PURPLE_DARK       = RGBColor(0x75, 0x00, 0xC1)   # Dark purple (#7500C1) – headings on light bg
    PURPLE_DEEPER     = RGBColor(0x59, 0x0A, 0xD8)   # Deeper vibrant purple (#590AD8) – strong accents

    # Functional (used sparingly for data visualization)
    SUCCESS      = RGBColor(0x00, 0xAA, 0x55)   # Green
    WARNING      = RGBColor(0xFF, 0xA5, 0x00)   # Amber
    INFO         = RGBColor(0x00, 0x7C, 0xFF)   # Blue


# ──────────────────────────────────────────────────────────────────────────────
# TYPOGRAPHY
# ──────────────────────────────────────────────────────────────────────────────

class Typography:
    """Font configuration following Accenture brand guidelines."""

    # Font stack: Graphik is the official Accenture font.
    # Graphik font variants:
    PRIMARY          = "Graphik"                  # Regular – body text, labels
    SEMIBOLD         = "Graphik Semibold"          # Semibold – emphasized headings, callouts
    LIGHT            = "Graphik-Light"             # Light – long-form body text
    SEMIBOLD_ITALIC  = "Graphik-SemiboldItalic"    # Semibold Italic – section divider titles
    FALLBACK         = "Calibri"                   # Widely available fallback
    BODY_FALLBACK    = "Aptos"                     # Microsoft Aptos (observed as body font in template)

    # Size scale (in points) – Accenture standard type system
    SIZE = {
        "hero":      48,   # Title slide main headline
        "display":   44,   # Section divider titles
        "h1":        32,   # Slide main titles
        "h2":        24,   # Subtitle / section headings
        "h3":        18,   # Sub-section headings
        "body":      16,   # Standard body text (203200 EMU → 16pt)
        "small":     14,   # Secondary / supporting text (177800 EMU → 14pt)
        "caption":   12,   # Footnotes, captions, labels (152400 EMU → 12pt)
        "label":      9,   # Tags, metadata badges
    }

    # Brand mark ">" sizes
    MARK_HERO   = 200   # Full-page decorative mark
    MARK_LARGE  = 100   # Title slide mark
    MARK_MEDIUM =  48   # Section divider mark
    MARK_SMALL  =  28   # Inline accent mark


# ──────────────────────────────────────────────────────────────────────────────
# LAYOUT CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

class Layout:
    """Slide layout constants following Accenture grid system."""

    # Slide dimensions (16:9 widescreen)
    WIDTH  = 13.33   # inches
    HEIGHT =  7.5    # inches

    # Margins
    MARGIN_H = 0.42   # Horizontal margin (left)
    MARGIN_V = 0.29   # Vertical margin (top)

    # Content area (within margins)
    CONTENT_WIDTH  = WIDTH  - MARGIN_H - 0.29   # usable width ≈ 12.62 in
    CONTENT_LEFT   = MARGIN_H

    # ── Header zone ──────────────────────────────────────────────────────────
    # Structure: [TITLE at y=0.15] → [BREADCRUMB at y=0.71] → [RULE at y=1.07]
    TITLE_TOP      = 0.15    # y position of slide title (h1) — high enough to fit 32pt
    TITLE_HEIGHT   = 0.56    # height of title text box (= BREADCRUMB_TOP - TITLE_TOP)
    BREADCRUMB_TOP = 0.71    # y position of subtitle/breadcrumb label (small)
    BREADCRUMB_H   = 0.30    # height of breadcrumb label
    RULE_TOP       = 1.07    # y position of the horizontal divider rule
    RULE_H         = 0.025   # thickness of the rule line
    CONTENT_TOP    = 1.35    # y position where slide content begins

    # Logo wordmark — white PNG, bottom-right (used on dark slides)
    LOGO_LEFT   = 11.30   # x position
    LOGO_TOP    =  6.667  # y position
    LOGO_WIDTH  =  1.594  # width
    LOGO_HEIGHT =  0.421  # height

    # Chevron badge — small purple ">" PNG, bottom-left (used on all slides)
    CHEVRON_LEFT   = 0.417
    CHEVRON_TOP    = 7.089
    CHEVRON_SIZE   = 0.221   # square

    # Column gutters
    GUTTER = 0.20

    # Bottom status bar — minimal, tagline text only at bottom-right
    STATUS_BAR_TOP = HEIGHT - 0.35
    STATUS_BAR_H   = 0.35


# ──────────────────────────────────────────────────────────────────────────────
# LOW-LEVEL DRAWING HELPERS
# ──────────────────────────────────────────────────────────────────────────────

class Draw:
    """Low-level shape drawing utilities for python-pptx."""

    # ── Background ────────────────────────────────────────────────────────────

    @staticmethod
    def background(slide, color: RGBColor) -> None:
        """Fill the entire slide with a solid color."""
        bg = slide.background
        bg.fill.solid()
        bg.fill.fore_color.rgb = color

    # ── Rectangles ────────────────────────────────────────────────────────────

    @staticmethod
    def rect(slide, left: float, top: float, width: float, height: float,
             fill: RGBColor, border: Optional[RGBColor] = None,
             border_width_pt: float = 0) -> object:
        """Add a solid rectangle (dimensions in inches)."""
        shape = slide.shapes.add_shape(
            1,  # MSO_SHAPE_TYPE.RECTANGLE
            Inches(left), Inches(top), Inches(width), Inches(height)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
        if border:
            shape.line.color.rgb = border
            shape.line.width = Pt(border_width_pt) if border_width_pt else Pt(0.5)
        else:
            shape.line.color.rgb = fill   # invisible border
        return shape

    @staticmethod
    def rounded_rect(slide, left: float, top: float, width: float, height: float,
                     fill: RGBColor, radius_pt: int = 8,
                     border: Optional[RGBColor] = None) -> object:
        """Add a rounded rectangle."""
        shape = slide.shapes.add_shape(
            5,  # ROUNDED_RECTANGLE
            Inches(left), Inches(top), Inches(width), Inches(height)
        )
        shape.adjustments[0] = radius_pt / 1000.0
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
        if border:
            shape.line.color.rgb = border
        else:
            shape.line.color.rgb = fill
        return shape

    # ── Text ──────────────────────────────────────────────────────────────────

    @staticmethod
    def text(slide, content: str, left: float, top: float,
             width: float, height: float,
             size: int = 13, bold: bool = False, italic: bool = False,
             color: RGBColor = Colors.DARK_GRAY,
             align: PP_ALIGN = PP_ALIGN.LEFT,
             font: str = Typography.PRIMARY,
             wrap: bool = True,
             spacing_after_pt: int = 0) -> object:
        """Add a single-paragraph text box."""
        txb = slide.shapes.add_textbox(
            Inches(left), Inches(top), Inches(width), Inches(height)
        )
        tf = txb.text_frame
        tf.word_wrap = wrap
        p = tf.paragraphs[0]
        p.alignment = align
        if spacing_after_pt:
            p.space_after = Pt(spacing_after_pt)
        run = p.add_run()
        run.text = content
        run.font.name  = font
        run.font.size  = Pt(size)
        run.font.bold  = bold
        run.font.color.rgb = color
        if italic:
            run.font.italic = True
        return txb

    @staticmethod
    def bullet_list(slide, items: List[str], left: float, top: float,
                    width: float, height: float,
                    size: int = 12, color: RGBColor = Colors.DARK_GRAY,
                    bullet_char: str = "—",
                    indent: float = 0.15,
                    line_spacing_pt: int = 6,
                    font: str = Typography.PRIMARY) -> object:
        """Add a bulleted list text box with Accenture-style em-dash bullets."""
        txb = slide.shapes.add_textbox(
            Inches(left), Inches(top), Inches(width), Inches(height)
        )
        tf = txb.text_frame
        tf.word_wrap = True
        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.space_before = Pt(line_spacing_pt)
            run = p.add_run()
            run.text = f"{bullet_char}  {item}"
            run.font.name  = font
            run.font.size  = Pt(size)
            run.font.color.rgb = color
        return txb

    # ── Accenture Brand Mark ">" ───────────────────────────────────────────────

    @staticmethod
    def brand_mark(slide, left: float, top: float, size_pt: int = 100,
                   color: RGBColor = Colors.PURPLE,
                   alpha_fill: bool = False) -> object:
        """
        Add the Accenture ">" brand mark as a large text element.
        This is the signature visual element of Accenture's identity.

        Args:
            size_pt: Font size in points. Larger = more decorative.
            alpha_fill: If True, the mark is rendered as a faint watermark effect.
        """
        mark_color = RGBColor(0xCC, 0x80, 0xFF) if alpha_fill else color
        return Draw.text(
            slide, ">",
            left, top,
            size_pt / 72 * 1.5,  # approximate width in inches
            size_pt / 72 * 1.6,  # approximate height in inches
            size=size_pt,
            bold=True,
            color=mark_color,
            font=Typography.PRIMARY,
            align=PP_ALIGN.LEFT,
        )

    @staticmethod
    def chevron_image(slide, left: float, top: float,
                      width: float = 3.0, height: float = 3.2) -> None:
        """
        Place the large purple Accenture chevron PNG as a decorative mark.
        Used in the left dark panel of title, section divider, and closing slides.
        Falls back to brand_mark() text if the asset is missing.

        Args:
            left:   x position in inches
            top:    y position in inches
            width:  image width in inches
            height: image height in inches
        """
        path = _asset("accenture_chevron_purple.png")
        if os.path.exists(path):
            slide.shapes.add_picture(
                path,
                Inches(left), Inches(top),
                Inches(width), Inches(height),
            )
        else:
            Draw.brand_mark(slide, left=left, top=top,
                            size_pt=int(width * 72 / 1.5))

    @staticmethod
    def icon(slide, name: str, left: float, top: float, size: float = 1.2) -> None:
        """
        Place a semantic icon from the Assets.ICONS catalog.

        All icons are flat accent marks — place bottom-right of the content area
        alongside bullet text on the left.

        Recommended size: 1.0–1.5 in. Width is auto-calculated from size × aspect
        ratio. The icon is automatically clamped to stay within slide boundaries.

        Example:
            Draw.icon(slide, "goal", left=11.5, top=5.6, size=1.2)

        When using an icon, reduce the bullet_list width by ~2.5 in to leave room:
            top ≈ zones["content_top"] + zones["content_height"] - size

        Args:
            name: Semantic key from Assets.ICONS
            left: x position in inches
            top:  y position in inches
            size: height in inches (width auto-adjusted per aspect ratio)
        """
        filename = Assets.ICONS.get(name)
        if not filename:
            return
        path = _asset(filename)
        if not os.path.exists(path):
            return
        w = h = min(size,
                    Layout.WIDTH - left - 0.1,
                    Layout.HEIGHT - top - 0.4)
        if filename.endswith(".svg"):
            import cairosvg
            png_bytes = cairosvg.svg2png(url=path, output_width=512, output_height=512)
            slide.shapes.add_picture(io.BytesIO(png_bytes), Inches(left), Inches(top),
                                     Inches(w), Inches(h))
        else:
            slide.shapes.add_picture(path, Inches(left), Inches(top),
                                     Inches(w), Inches(h))

    # ── Horizontal Rule ───────────────────────────────────────────────────────

    @staticmethod
    def rule(slide, left: float, top: float, width: float,
             color: RGBColor = Colors.PURPLE, height: float = 0.04) -> None:
        """Add a thin horizontal rule line."""
        Draw.rect(slide, left, top, width, height, fill=color)

    # ── Dot Grid (decorative tech pattern) ────────────────────────────────────

    @staticmethod
    def dot_grid(slide, left: float, top: float, width: float, height: float,
                 cols: int = 8, rows: int = 5,
                 dot_size_pt: float = 3.5,
                 color: RGBColor = Colors.PURPLE,
                 opacity: float = 0.25) -> None:
        """
        Add a grid of small dots — Accenture's signature tech/data texture.
        Dots are rendered at reduced opacity by mixing color with background.

        Args:
            cols: Number of dot columns
            rows: Number of dot rows
            dot_size_pt: Dot diameter in points
            opacity: Simulated opacity (0–1). Blends dot color toward white.
        """
        dot_w = Inches(width) / cols
        dot_h = Inches(height) / rows
        dot_r = Pt(dot_size_pt)

        # Simulate opacity by blending toward white.
        # RGBColor is a subclass of str (hex "RRGGBB").
        hex_str = str(color)
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        blended = RGBColor(
            int(r + (255 - r) * (1 - opacity)),
            int(g + (255 - g) * (1 - opacity)),
            int(b + (255 - b) * (1 - opacity)),
        )

        for row in range(rows):
            for col in range(cols):
                ox = Inches(left) + col * dot_w + dot_w // 2 - dot_r // 2
                oy = Inches(top)  + row * dot_h + dot_h // 2 - dot_r // 2
                dot = slide.shapes.add_shape(
                    9,   # Oval / circle
                    int(ox), int(oy), int(dot_r), int(dot_r)
                )
                dot.fill.solid()
                dot.fill.fore_color.rgb = blended
                dot.line.color.rgb = blended

    # ── Status Bar ────────────────────────────────────────────────────────────

    @staticmethod
    def status_bar(slide, left_text: str = "",
                   right_text: str = "Engineering the Future. Transforming Business.",
                   bg: Optional[RGBColor] = None,
                   color: RGBColor = Colors.MID_GRAY) -> None:
        """
        Add a bottom footer bar.

        Accenture style: minimal — just tagline text at bottom-right, no filled rectangle.
        Pass bg=Colors.NEAR_BLACK for the dark-panel style used on title/closing slides.

        Args:
            left_text:  Optional left label (e.g. "Confidential")
            right_text: Tagline shown right-aligned
            bg:         Background fill color. None = transparent (no rect drawn).
            color:      Text color
        """
        if bg is not None:
            Draw.rect(slide, 0, Layout.STATUS_BAR_TOP,
                      Layout.WIDTH, Layout.STATUS_BAR_H, fill=bg)
        if left_text:
            Draw.text(slide, left_text, 0.42, Layout.STATUS_BAR_TOP + 0.06,
                      5, 0.22, size=Typography.SIZE["label"],
                      color=color, align=PP_ALIGN.LEFT)
        if right_text:
            Draw.text(slide, right_text,
                      Layout.WIDTH - 5.5, Layout.STATUS_BAR_TOP + 0.06,
                      5.3, 0.22, size=Typography.SIZE["label"],
                      color=color, align=PP_ALIGN.RIGHT, italic=True)

    # ── Logo images ────────────────────────────────────────────────────────────

    @staticmethod
    def logo_image(slide) -> None:
        """
        Place the Accenture white wordmark PNG at the standard bottom-right position.
        Used on dark-background slides (title, section divider, closing).
        Falls back to text if the asset is missing.
        """
        path = _asset("accenture_wordmark_white.png")
        if os.path.exists(path):
            slide.shapes.add_picture(
                path,
                Inches(Layout.LOGO_LEFT), Inches(Layout.LOGO_TOP),
                Inches(Layout.LOGO_WIDTH), Inches(Layout.LOGO_HEIGHT),
            )
        else:
            Draw.text(slide, "accenture >",
                      Layout.LOGO_LEFT, Layout.LOGO_TOP,
                      Layout.LOGO_WIDTH, Layout.LOGO_HEIGHT,
                      size=Typography.SIZE["caption"], bold=True,
                      color=Colors.WHITE, align=PP_ALIGN.RIGHT,
                      font=Typography.PRIMARY)

    @staticmethod
    def chevron_badge(slide) -> None:
        """
        Place the small purple Accenture chevron PNG at the standard bottom-left position.
        Used on every slide type (content, divider, title, closing).
        Falls back to a small ">" text if the asset is missing.
        """
        path = _asset("accenture_chevron_small.png")
        if os.path.exists(path):
            slide.shapes.add_picture(
                path,
                Inches(Layout.CHEVRON_LEFT), Inches(Layout.CHEVRON_TOP),
                Inches(Layout.CHEVRON_SIZE), Inches(Layout.CHEVRON_SIZE),
            )
        else:
            Draw.text(slide, ">",
                      Layout.CHEVRON_LEFT, Layout.CHEVRON_TOP,
                      Layout.CHEVRON_SIZE, Layout.CHEVRON_SIZE,
                      size=Typography.SIZE["caption"], bold=True,
                      color=Colors.PURPLE, align=PP_ALIGN.LEFT,
                      font=Typography.PRIMARY)

    @staticmethod
    def logo_text(slide, text: str = "accenture >",
                  color: RGBColor = Colors.WHITE) -> None:
        """Backward-compat text wordmark. Prefer logo_image() for real assets."""
        Draw.text(slide, text,
                  Layout.LOGO_LEFT, Layout.LOGO_TOP,
                  Layout.LOGO_WIDTH, Layout.LOGO_HEIGHT,
                  size=Typography.SIZE["caption"], bold=True,
                  color=color, align=PP_ALIGN.RIGHT,
                  font=Typography.PRIMARY)


# ──────────────────────────────────────────────────────────────────────────────
# CARD COMPONENT
# ──────────────────────────────────────────────────────────────────────────────

class Card:
    """Accenture-style content card with purple header bar."""

    _HEADER_H = 0.42   # header bar height in inches
    _PADDING  = 0.14   # internal body padding (top + bottom)

    @staticmethod
    def auto_height(bullets: List[str], card_width: float,
                    body_size: int = 12) -> float:
        """
        Compute card height accounting for text wrapping.

        Uses the actual bullet strings and card width to estimate how many
        visual lines each bullet will occupy, preventing text overflow.

        Usage — always take the max across all cards:
            card_h = max(Card.auto_height(b, card_w) for _, b in cards_data)

        Args:
            bullets:    List of bullet text strings for this card
            card_width: Card width in inches (used to estimate wrapping)
            body_size:  Body font size in pt (default 12)

        Returns:
            Recommended card height in inches
        """
        # Estimate chars per line: inner_width × 72pt/in ÷ avg_char_width_pt
        # Graphik avg char width ≈ 55% of font size; subtract 0.24in for inner padding
        inner_w = max(0.5, card_width - 0.24)
        chars_per_line = max(1, inner_w * 72 / (body_size * 0.55))
        total_lines = 0
        for bullet in bullets:
            # "—  " prefix adds ~3 chars of effective width
            lines = int((len(bullet) + 3) / chars_per_line) + 1
            total_lines += lines
        line_h = body_size / 72 * 1.5 + 0.07   # font height + line spacing
        return Card._HEADER_H + total_lines * line_h + Card._PADDING

    @staticmethod
    def add(slide, title: str, bullets: List[str],
            left: float, top: float, width: float, height: float,
            header_color: RGBColor = Colors.PURPLE,
            card_bg: RGBColor = Colors.WHITE,
            title_size: int = 14,
            body_size: int = 12,
            show_mark: bool = False,
            text_color: RGBColor = Colors.DARK_GRAY,
            shadow_color: Optional[RGBColor] = None) -> None:
        """
        Render a card with:
          - Colored header bar with title
          - Optional ">" mini mark
          - Bulleted body content

        Tip: use Card.auto_height(len(bullets)) to size the card to its content
        instead of stretching it to the full content area.

        Args:
            show_mark:    If True, adds a small ">" accent on the header bar
            text_color:   Body bullet text color. Use a light color (e.g. RGBColor(0xCC,0xCC,0xCC))
                          when card_bg is dark, otherwise the text will be invisible.
            shadow_color: Shadow rect fill. Pass the slide background color to hide the shadow
                          on dark slides (default draws a light-gray shadow suited for white/light bgs).
        """
        HEADER_H = Card._HEADER_H
        BORDER = RGBColor(0xE0, 0xE0, 0xE0)
        _shadow = shadow_color if shadow_color is not None else RGBColor(0xDD, 0xDD, 0xDD)

        # Card shadow (slightly larger rect beneath — match slide bg on dark slides)
        Draw.rect(slide, left + 0.03, top + 0.03, width, height, fill=_shadow)

        # Card body
        Draw.rect(slide, left, top, width, height, fill=card_bg, border=BORDER,
                  border_width_pt=0.5)

        # Header bar
        Draw.rect(slide, left, top, width, HEADER_H, fill=header_color)

        # Header title
        Draw.text(slide, title, left + 0.12, top + 0.06,
                  width - 0.3, HEADER_H - 0.1,
                  size=title_size, bold=True, color=Colors.WHITE,
                  align=PP_ALIGN.LEFT)

        # Optional mini ">" mark on header
        if show_mark:
            Draw.text(slide, ">", left + width - 0.35, top + 0.04,
                      0.3, HEADER_H - 0.06,
                      size=title_size + 2, bold=True, color=Colors.WHITE,
                      align=PP_ALIGN.RIGHT)

        # Body bullets
        Draw.bullet_list(slide, bullets,
                         left + 0.12, top + HEADER_H + 0.06,
                         width - 0.22, height - HEADER_H - 0.1,
                         size=body_size, color=text_color)


# ──────────────────────────────────────────────────────────────────────────────
# HIGH-LEVEL SLIDE FACTORIES
# ──────────────────────────────────────────────────────────────────────────────

class SlideFactory:
    """
    Factory for creating Accenture-branded slides.

    All methods return the created slide object for further customization.
    """

    def __init__(self, prs: Presentation):
        self.prs = prs
        self._blank = prs.slide_layouts[6]  # Blank layout

    def _new(self):
        return self.prs.slides.add_slide(self._blank)

    # ── 1. Title Slide ────────────────────────────────────────────────────────

    def title_slide(self,
                    headline: str,
                    subtitle: str = "",
                    client: str = "",
                    date: str = "",
                    tagline: str = "Engineering the Future. Transforming Business.") -> object:
        """
        Accenture signature title slide.

        Layout:
          - Near-black background
          - Large purple ">" brand mark (left panel, decorative)
          - Purple vertical separator between left and right panels
          - White bold headline (right panel, vertical center)
          - Purple horizontal rule under headline
          - Subtitle and optional client/date labels
          - Logo wordmark top-right (white)
          - Tagline bottom-right (italic, mid-gray)

        Args:
            headline: Main presentation title (h1 size, bold white)
            subtitle: Presentation subtitle or project name (shown in purple below rule)
            client:   Client or audience name ("Prepared for …" label)
            date:     Presentation date string
            tagline:  Footer tagline
        """
        slide = self._new()
        Draw.background(slide, Colors.NEAR_BLACK)

        # Left panel — slightly deeper black
        Draw.rect(slide, 0, 0, 4.5, Layout.HEIGHT, fill=Colors.BLACK)

        # Large decorative chevron image (left panel)
        Draw.chevron_image(slide, left=0.2, top=1.5, width=3.8, height=4.0)

        # Purple vertical separator
        Draw.rect(slide, 4.5, 0, 0.04, Layout.HEIGHT, fill=Colors.PURPLE)

        # Logo wordmark (white PNG, bottom-right) + chevron badge (bottom-left)
        Draw.logo_image(slide)
        Draw.chevron_badge(slide)

        # "Prepared for" context label
        if client:
            Draw.text(slide, f"Prepared for  {client}",
                      4.75, 1.2, 8.3, 0.35,
                      size=Typography.SIZE["small"], color=Colors.PURPLE,
                      bold=True, font=Typography.PRIMARY)

        # Headline — large, bold white
        headline_top = 1.65 if client else 1.3
        Draw.text(slide, headline,
                  4.75, headline_top, 8.3, 2.0,
                  size=Typography.SIZE["hero"], bold=True,
                  color=Colors.WHITE, align=PP_ALIGN.LEFT,
                  font=Typography.PRIMARY)

        # Purple rule under headline
        rule_y = headline_top + 2.1
        Draw.rule(slide, 4.75, rule_y, 8.3, color=Colors.PURPLE)

        # Subtitle
        if subtitle:
            Draw.text(slide, subtitle,
                      4.75, rule_y + 0.14, 8.3, 0.65,
                      size=Typography.SIZE["h3"], color=Colors.PURPLE,
                      font=Typography.PRIMARY)

        # Date label
        if date:
            Draw.text(slide, date,
                      4.75, rule_y + 0.85, 8.3, 0.35,
                      size=Typography.SIZE["small"], color=Colors.MID_GRAY)

        # Bottom bar with tagline
        Draw.rect(slide, 0, Layout.HEIGHT - 0.40, Layout.WIDTH, 0.40,
                  fill=Colors.BLACK)
        Draw.status_bar(slide, right_text=tagline,
                        bg=None, color=Colors.MID_GRAY)

        return slide

    # ── 2. Section Divider ────────────────────────────────────────────────────

    def section_divider(self,
                        section_title: str,
                        section_number: str = "",
                        description: str = "") -> object:
        """
        Accenture section divider — two-panel layout.

        Layout:
          - Near-black left panel with right purple panel (x ≥ 4.24)
          - Large ">" brand mark on left panel (dark purple)
          - Section title (SemiboldItalic, h1) on right panel, white
          - Optional section number label (top of right panel, light purple)
          - Optional description (body, light purple)
          - Logo wordmark top-right

        Args:
            section_title:  The bold section heading (rendered white on purple)
            section_number: e.g. "01", "02" — displayed above the title
            description:    Short supporting sentence (shown below the rule)
        """
        slide = self._new()

        # Right panel — gradient background (full slide, left panel overlaid on top)
        grad_path = _asset("gradient_background_purple.png")
        if os.path.exists(grad_path):
            slide.shapes.add_picture(
                grad_path, Inches(0), Inches(0),
                Inches(Layout.WIDTH), Inches(Layout.HEIGHT),
            )
        else:
            Draw.background(slide, Colors.PURPLE_DARK)

        # Left panel — near-black rectangle overlaid on gradient
        Draw.rect(slide, 0, 0, 4.24, Layout.HEIGHT, fill=Colors.NEAR_BLACK)

        # Large decorative chevron image (left panel)
        Draw.chevron_image(slide, left=0.2, top=1.3, width=3.6, height=3.8)

        # Logo wordmark (white PNG, bottom-right) + chevron badge (bottom-left)
        Draw.logo_image(slide)
        Draw.chevron_badge(slide)

        # Section number label (subtle, above title)
        if section_number:
            Draw.text(slide, section_number,
                      5.0, 1.5, 2.0, 0.55,
                      size=Typography.SIZE["display"],
                      bold=True, color=Colors.PURPLE_EXTRA_LIGHT,
                      font=Typography.PRIMARY)

        # Section title — SemiboldItalic
        title_top = 2.1 if section_number else 1.7
        Draw.text(slide, section_title,
                  5.0, title_top, 7.8, 2.2,
                  size=Typography.SIZE["display"],
                  bold=True, color=Colors.WHITE,
                  align=PP_ALIGN.LEFT,
                  font=Typography.SEMIBOLD_ITALIC)

        # Horizontal rule under title
        rule_y = title_top + 2.3
        Draw.rule(slide, 5.0, rule_y, 7.8, color=Colors.PURPLE_EXTRA_LIGHT, height=0.03)

        # Description
        if description:
            Draw.text(slide, description,
                      5.0, rule_y + 0.15, 7.8, 0.8,
                      size=Typography.SIZE["body"],
                      color=Colors.PURPLE_EXTRA_LIGHT,
                      font=Typography.LIGHT)

        # Bottom bar
        Draw.rect(slide, 0, Layout.HEIGHT - 0.35, Layout.WIDTH, 0.35,
                  fill=Colors.BLACK)
        Draw.status_bar(slide, bg=None, color=Colors.MID_GRAY)

        return slide

    # ── 3. Standard Content Slide ─────────────────────────────────────────────

    def content_slide(self,
                      title: str,
                      section_label: str = "",
                      bg: RGBColor = Colors.WHITE,
                      title_color: RGBColor = Colors.NEAR_BLACK) -> Tuple[object, dict]:
        """
        Standard Accenture content slide.

        Returns (slide, zones) where zones is a dict of layout coordinates:
          - zones["content_top"]:    float – y where content starts (after the rule)
          - zones["content_left"]:   float – x position of content area
          - zones["content_width"]:  float – usable width
          - zones["content_height"]: float – usable height to status bar

        Header structure:
          y=0.29  Title (h1, bold, NEAR_BLACK)
          y=0.71  Breadcrumb / section label (small, PURPLE_DARK)
          y=1.07  Purple horizontal rule
          y=1.35  Content area begins

        Args:
            title:         Main slide heading
            section_label: Small breadcrumb label shown below the title (e.g. "ARCHITECTURE")
            bg:            Background color (default: white)
            title_color:   Title text color — use Colors.WHITE when bg is dark
        """
        slide = self._new()
        Draw.background(slide, bg)

        # Chevron badge bottom-left (purple PNG)
        Draw.chevron_badge(slide)

        # Slide title — h1 (height capped to avoid overlapping the breadcrumb)
        Draw.text(slide, title,
                  Layout.CONTENT_LEFT, Layout.TITLE_TOP,
                  Layout.CONTENT_WIDTH, Layout.BREADCRUMB_TOP - Layout.TITLE_TOP,
                  size=Typography.SIZE["h1"], bold=True,
                  color=title_color, font=Typography.PRIMARY)

        # Breadcrumb / section label — small purple text below title
        if section_label:
            Draw.text(slide, section_label.upper(),
                      Layout.CONTENT_LEFT, Layout.BREADCRUMB_TOP,
                      Layout.CONTENT_WIDTH, Layout.BREADCRUMB_H,
                      size=Typography.SIZE["caption"], bold=True,
                      color=Colors.PURPLE_DARK, font=Typography.PRIMARY)

        # Purple horizontal rule
        Draw.rule(slide, Layout.CONTENT_LEFT, Layout.RULE_TOP,
                  Layout.CONTENT_WIDTH, color=Colors.PURPLE, height=Layout.RULE_H)

        # Bottom status bar — minimal (tagline only, no bg rect)
        Draw.status_bar(slide, bg=None, color=Colors.MID_GRAY)

        zones = {
            "content_top":    Layout.CONTENT_TOP,
            "content_left":   Layout.CONTENT_LEFT,
            "content_width":  Layout.CONTENT_WIDTH,
            "content_height": Layout.STATUS_BAR_TOP - Layout.CONTENT_TOP - 0.1,
        }
        return slide, zones

    # ── 4. Closing Slide ──────────────────────────────────────────────────────

    def closing_slide(self,
                      headline: str = "THANK YOU",
                      subline: str = "",
                      contact: str = "",
                      tagline: str = "Engineering the Future. Transforming Business.") -> object:
        """
        Accenture closing slide.

        Layout:
          - Near-black left panel with large purple ">" brand mark
          - Purple vertical separator
          - Right panel: large bold white headline (Graphik Semibold)
          - Optional subline in purple below a rule
          - Optional contact info
          - Logo wordmark top-right (white)
          - Tagline bottom-right

        Args:
            headline: Closing headline (default: "THANK YOU")
            subline:  Next steps or key takeaway
            contact:  Presenter name or contact info
            tagline:  Footer tagline
        """
        slide = self._new()
        Draw.background(slide, Colors.NEAR_BLACK)

        # Left panel
        Draw.rect(slide, 0, 0, 4.5, Layout.HEIGHT, fill=Colors.BLACK)

        # Purple vertical separator
        Draw.rect(slide, 4.5, 0, 0.04, Layout.HEIGHT, fill=Colors.PURPLE)

        # Large decorative chevron image (left panel)
        Draw.chevron_image(slide, left=0.2, top=1.5, width=3.8, height=4.0)

        # Logo wordmark (white PNG, bottom-right) + chevron badge (bottom-left)
        Draw.logo_image(slide)
        Draw.chevron_badge(slide)

        # Headline — Graphik Semibold, large white
        Draw.text(slide, headline,
                  4.75, 2.5, 8.3, 1.5,
                  size=Typography.SIZE["hero"], bold=True,
                  color=Colors.WHITE, align=PP_ALIGN.LEFT,
                  font=Typography.SEMIBOLD)

        # Purple rule
        Draw.rule(slide, 4.75, 4.2, 8.3, color=Colors.PURPLE)

        if subline:
            Draw.text(slide, subline,
                      4.75, 4.35, 8.3, 0.65,
                      size=Typography.SIZE["h3"], color=Colors.PURPLE,
                      font=Typography.PRIMARY)

        if contact:
            Draw.text(slide, contact,
                      4.75, 5.1, 8.3, 0.5,
                      size=Typography.SIZE["body"], color=Colors.MID_GRAY,
                      font=Typography.PRIMARY)

        # Bottom bar with tagline
        Draw.rect(slide, 0, Layout.HEIGHT - 0.40, Layout.WIDTH, 0.40,
                  fill=Colors.BLACK)
        Draw.status_bar(slide, right_text=tagline, bg=None, color=Colors.MID_GRAY)

        return slide


# ──────────────────────────────────────────────────────────────────────────────
# THEME CONFIGURATOR
# ──────────────────────────────────────────────────────────────────────────────

class Theme:
    """Top-level theme configurator for Accenture presentations."""

    @staticmethod
    def configure(prs: Presentation,
                  width_in: float = Layout.WIDTH,
                  height_in: float = Layout.HEIGHT) -> None:
        """
        Configure presentation dimensions for Accenture standard layout.

        Call this immediately after creating the Presentation object.

        Args:
            prs: The python-pptx Presentation instance
            width_in: Slide width in inches (default: 13.33 for 16:9)
            height_in: Slide height in inches (default: 7.5 for 16:9)
        """
        prs.slide_width  = Inches(width_in)
        prs.slide_height = Inches(height_in)

    @staticmethod
    def new_presentation() -> Tuple[Presentation, SlideFactory]:
        """
        Create a new Accenture-branded presentation.

        Returns (prs, factory) ready to use.

        Example:
            prs, factory = Theme.new_presentation()
            factory.title_slide("My Title", "My Subtitle", client="Vodafone")
            prs.save("output.pptx")
        """
        prs = Presentation()
        Theme.configure(prs)
        factory = SlideFactory(prs)
        return prs, factory
