import sys, os
sys.path.insert(0, os.path.expanduser("~/.claude/skills/accenture-pptx/scripts"))
from accenture_theme import Theme, Colors, Typography, Layout, Draw, Card

prs, factory = Theme.new_presentation()

# Slide 1 — Title
factory.title_slide(
    headline="Presentation Title",
    subtitle="Subtitle or Project Name",
    client="Client Name",
    date="March 2026",
)

# Slide Section divider
factory.section_divider("Section Title", section_number="01", description="Brief description")

# Slide Bullet list
slide, zones = factory.content_slide("Slide Title", section_label="SECTION NAME")
Draw.bullet_list(
    slide,
    ["First key point", "Second key point", "Third key point"],
    zones["content_left"], zones["content_top"],
    zones["content_width"], zones["content_height"],
    size=Typography.SIZE["body"], color=Colors.DARK_GRAY,
)

# Slide Content with icon (flat icon bottom-right)
slide, zones = factory.content_slide("Slide Title with Icon", section_label="SECTION NAME")
icon_size = 1.2
Draw.bullet_list(
    slide,
    ["First key point", "Second key point", "Third key point"],
    zones["content_left"], zones["content_top"],
    zones["content_width"] - icon_size - Layout.GUTTER, zones["content_height"],
    size=Typography.SIZE["body"], color=Colors.DARK_GRAY,
)
Draw.icon(slide, "goal",
          left=zones["content_left"] + zones["content_width"] - icon_size,
          top=zones["content_top"] + zones["content_height"] - icon_size,
          size=icon_size)

# Slide Two-column layout
slide, zones = factory.content_slide("Two Columns")
col_w = (zones["content_width"] - Layout.GUTTER) / 2
col2_x = zones["content_left"] + col_w + Layout.GUTTER
Draw.bullet_list(slide, ["Left col point 1", "Left col point 2"],
                 zones["content_left"], zones["content_top"], col_w, zones["content_height"])
Draw.bullet_list(slide, ["Right col point 1", "Right col point 2"],
                 col2_x, zones["content_top"], col_w, zones["content_height"])

# Slide Card grid
slide, zones = factory.content_slide("Card Grid")
cards_data = [
    ("Card One",   ["Bullet A", "Bullet B"]),
    ("Card Two",   ["Bullet C", "Bullet D"]),
    ("Card Three", ["Bullet E", "Bullet F"]),
]
n_cards = len(cards_data)
card_w = (zones["content_width"] - Layout.GUTTER * (n_cards - 1)) / n_cards
# Auto-size card height from content (accounting for text wrapping), then center vertically
card_h = max(Card.auto_height(b, card_w) for _, b in cards_data)
card_top = zones["content_top"] + (zones["content_height"] - card_h) / 2
for i, (title, bullets) in enumerate(cards_data):
    cx = zones["content_left"] + i * (card_w + Layout.GUTTER)
    Card.add(slide, title, bullets, cx, card_top, card_w, card_h)

# Last slide — Closing
factory.closing_slide(subline="Next steps or key takeaway", contact="Presenter Name")

out = os.path.expanduser("~/output.pptx")
prs.save(out)
print(f"Saved: {out}")
