#!/usr/bin/env python3
"""Renderer for make.fun news-image-20261119.

Draws a single 1024x1024 PNG front page ("THE WORLD IN ONE IMAGE",
Thursday 19 November 2026) from embedded copy. Deterministic: no
randomness, no time, no network. Output: assets/entry.png
"""
import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REPO, "assets", "entry.png")

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN  # 952

PAPER = (247, 243, 234)
INK = (20, 20, 20)
RED = (176, 30, 36)
MUTED = (90, 86, 76)
USA_BLUE = (60, 59, 110)
USA_RED = (178, 34, 52)
CHINA_RED = (222, 41, 16)
CHINA_YELLOW = (255, 222, 0)
RUSSIA_BLUE = (0, 57, 166)
RUSSIA_RED = (213, 43, 30)
FLAME = (232, 89, 12)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w):
    """Word-wrap `text` so every line fits `max_w` (font.getlength)."""
    lines = []
    cur = ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_size(text, path, start, max_w, minimum):
    """Largest size <= start at which `text` fits `max_w`."""
    size = start
    while size > minimum and font(path, size).getlength(text) > max_w:
        size -= 1
    return size


def text_h(fnt):
    """Line height (ascent + descent) for a font."""
    return fnt.getbbox("Ay")[3] - fnt.getbbox("Ay")[1]


def draw_centered(draw, cx, y, text, fnt, fill):
    w = fnt.getlength(text)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def star_points(cx, cy, r_out, r_in, rot=-90.0):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------- flags
def draw_usa(draw, x, y, w, h):
    stripe_h = h / 13.0
    for i in range(13):
        if i % 2 == 0:
            draw.rectangle([x, y + i * stripe_h, x + w, y + (i + 1) * stripe_h],
                           fill=USA_RED)
        else:
            draw.rectangle([x, y + i * stripe_h, x + w, y + (i + 1) * stripe_h],
                           fill=(255, 255, 255))
    cw, ch = w * 0.40, stripe_h * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=USA_BLUE)
    for r in range(4):
        for c in range(5):
            sx = x + cw * (0.12 + 0.19 * c)
            sy = y + ch * (0.16 + 0.23 * r)
            draw.ellipse([sx - 1.6, sy - 1.6, sx + 1.6, sy + 1.6],
                         fill=(255, 255, 255))


def draw_china(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=CHINA_RED)
    bx, by = x + w * 0.16, y + h * 0.30
    draw.polygon(star_points(bx, by, h * 0.26, h * 0.10), fill=CHINA_YELLOW)
    small = [(0.34, 0.12), (0.40, 0.30), (0.37, 0.50), (0.28, 0.62)]
    for fx, fy in small:
        draw.polygon(
            star_points(x + w * fx, y + h * fy, h * 0.09, h * 0.035),
            fill=CHINA_YELLOW)


def draw_russia(draw, x, y, w, h):
    third = h / 3.0
    draw.rectangle([x, y, x + w, y + third], fill=(255, 255, 255))
    draw.rectangle([x, y + third, x + w, y + 2 * third], fill=RUSSIA_BLUE)
    draw.rectangle([x, y + 2 * third, x + w, y + h], fill=RUSSIA_RED)


# ---------------------------------------------------------------- icons
def draw_bridge(draw, x, y, w, h):
    """Two towers, a deck line, red blast star. Box (x, y, w, h)."""
    deck_y = y + h - 6
    draw.line([x, deck_y, x + w, deck_y], fill=INK, width=3)
    for tx in (x + 6, x + w - 10):
        draw.rectangle([tx, y + 4, tx + 4, deck_y], fill=INK)
    draw.line([x + 8, y + 4, x + w / 2, deck_y - 2], fill=INK, width=1)
    draw.line([x + w - 8, y + 4, x + w / 2, deck_y - 2], fill=INK, width=1)
    cx, cy = x + w / 2, y + 7
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        draw.line([cx, cy, cx + 9 * math.cos(a), cy + 9 * math.sin(a)],
                  fill=RED, width=2)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)


def draw_tanker(draw, x, y, w, h):
    """Oil tanker silhouette with a small flame. Box (x, y, w, h)."""
    hull_y = y + h - 12
    draw.polygon([(x, hull_y), (x + w, hull_y), (x + w - 8, y + h),
                  (x + 4, y + h)], fill=INK)
    draw.rectangle([x + w * 0.62, hull_y - 12, x + w * 0.80, hull_y],
                   fill=INK)
    draw.line([x + w * 0.62, hull_y - 12, x + w * 0.80, hull_y - 12],
              fill=INK, width=2)
    fx, fy = x + w * 0.30, y + 8
    draw.polygon([(fx, fy + 8), (fx - 5, fy + 14), (fx - 1, fy + 4),
                  (fx + 2, fy), (fx + 5, fy + 6), (fx + 6, fy + 14)],
                 fill=FLAME)
    draw.ellipse([fx - 2, fy + 10, fx + 3, fy + 15], fill=RED)


def draw_scales(draw, x, y, w, h):
    """Scales of justice: vertical bar, beam, two pans."""
    cx = x + w / 2
    draw.line([cx, y + 2, cx, y + h - 4], fill=INK, width=3)
    draw.line([x + 2, y + 7, x + w - 2, y + 7], fill=INK, width=3)
    draw.ellipse([cx - 3, y, cx + 3, y + 6], fill=INK)
    for px in (x + 6, x + w - 6):
        draw.line([px, y + 7, px - 7, y + h - 8], fill=INK, width=2)
        draw.line([px, y + 7, px + 7, y + h - 8], fill=INK, width=2)
        draw.arc([px - 9, y + h - 12, px + 9, y + h + 2],
                 start=0, end=180, fill=INK, width=2)


ICONS = {"bridge": draw_bridge, "tanker": draw_tanker, "scales": draw_scales}

LEAD_DECK = (
    "Donald Trump, Xi Jinping and Vladimir Putin held the first three-way "
    "summit of the United States, China and Russia, on the sidelines of the "
    "APEC forum. Nuclear arms, Ukraine, Iran and trade were on the table. "
    "No breakthrough was reported."
)

COLUMNS = [
    {
        "kicker": "UKRAINE",
        "headline": ["KERCH BRIDGE", "HIT AGAIN"],
        "deck": ("Ukraine struck the bridge linking Russia to Crimea for the "
                 "third time in four days. Rail traffic halted."),
        "icon": "bridge",
    },
    {
        "kicker": "THE GULF",
        "headline": ["IRAN HITS", "KUWAIT AND", "BAHRAIN"],
        "deck": ("Tehran widened its attacks on the Gulf after US strikes on "
                 "Qeshm Island. Kuwait says it repelled the assault as the "
                 "Strait of Hormuz crisis deepens."),
        "icon": "tanker",
    },
    {
        "kicker": "JUSTICE",
        "headline": ["COURT RULES", "ON ROHINGYA"],
        "deck": ("The International Court of Justice ruled Myanmar's forces "
                 "intended to destroy a substantial part of the Rohingya "
                 "minority."),
        "icon": "scales",
    },
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    report = []

    # ---- masthead -------------------------------------------------
    masthead = "THE WORLD IN ONE IMAGE"
    m_size = fit_size(masthead, SERIF_B, 64, CONTENT_W, 48)
    m_font = font(SERIF_B, m_size)
    draw_centered(draw, W / 2, 24, masthead, m_font, INK)
    report.append(f"masthead {m_size}px w={m_font.getlength(masthead):.0f}")

    # ---- red rule / date line / black rule ------------------------
    draw.rectangle([MARGIN, 112, W - MARGIN, 114], fill=RED)
    date_text = "THURSDAY 19 NOVEMBER 2026"
    d_font = font(SANS_B, 40)
    assert d_font.getlength(date_text) <= CONTENT_W
    draw_centered(draw, W / 2, 122, date_text, d_font, RED)
    report.append(f"date 40px w={d_font.getlength(date_text):.0f}")
    draw.rectangle([MARGIN, 174, W - MARGIN, 175], fill=INK)

    # ---- lead story ----------------------------------------------
    y = 192
    k_font = font(SANS_B, 21)
    draw.text((MARGIN, y), "SHENZHEN  \u2022  THE LEAD STORY",
              font=k_font, fill=RED)
    y += 30

    head_lines = ["THREE LEADERS,", "ONE TABLE"]
    h_size = fit_size(max(head_lines, key=len), SERIF_B, 66, CONTENT_W, 56)
    h_font = font(SERIF_B, h_size)
    lh = h_size + 6
    for line in head_lines:
        assert h_font.getlength(line) <= CONTENT_W, line
        draw.text((MARGIN, y), line, font=h_font, fill=INK)
        y += lh
    report.append(f"lead headline {h_size}px lines={head_lines}")
    y += 10

    deck_font = font(SANS, 26)
    deck_lines = wrap(LEAD_DECK, deck_font, CONTENT_W)
    for line in deck_lines:
        assert deck_font.getlength(line) <= CONTENT_W, line
        draw.text((MARGIN, y), line, font=deck_font, fill=INK)
        y += 31
    report.append(f"lead deck 26px lines={len(deck_lines)}: {deck_lines}")
    y += 10

    # ---- flag strip ------------------------------------------------
    flag_w, flag_h = 290, 38
    total_w = 3 * flag_w + 2 * 20
    fx = MARGIN + (CONTENT_W - total_w) // 2
    flags = [("USA", draw_usa), ("CHINA", draw_china), ("RUSSIA", draw_russia)]
    for label, fn in flags:
        draw.rectangle([fx - 1, y - 1, fx + flag_w + 1, y + flag_h + 1],
                       outline=INK, width=1)
        fn(draw, fx, y, flag_w, flag_h)
        lab_font = font(SANS_B, 18)
        draw_centered(draw, fx + flag_w / 2, y + flag_h + 5,
                      label, lab_font, INK)
        fx += flag_w + 20
    y += flag_h + 5 + 24
    y += 10
    draw.rectangle([MARGIN, y, W - MARGIN, y + 1], fill=INK)
    report.append(f"lead ends y={y} (divider rule)")
    y += 12

    # ---- three columns ---------------------------------------------
    col_w = 304
    gutter = 20
    col_x = [MARGIN, MARGIN + col_w + gutter,
             MARGIN + 2 * (col_w + gutter)]

    # uniform column headline size: largest size fitting every line
    col_h_size = 36
    for col in COLUMNS:
        for line in col["headline"]:
            col_h_size = min(
                col_h_size,
                fit_size(line, SERIF_B, 36, col_w, 24))
    col_h_font = font(SERIF_B, col_h_size)
    col_h_lh = col_h_size + 2
    col_k_font = font(SANS_B, 20)
    col_d_font = font(SANS, 24)
    col_d_lh = 26
    report.append(f"column headline uniform size={col_h_size}px")

    col_end = y
    for col, cx in zip(COLUMNS, col_x):
        cy = y
        # kicker (left) + icon (right, same row)
        draw.text((cx, cy), col["kicker"], font=col_k_font, fill=RED)
        ICONS[col["icon"]](draw, cx + col_w - 64, cy - 2, 64, 28)
        cy += 26
        for line in col["headline"]:
            assert col_h_font.getlength(line) <= col_w, line
            draw.text((cx, cy), line, font=col_h_font, fill=INK)
            cy += col_h_lh
        cy += 6
        d_lines = wrap(col["deck"], col_d_font, col_w)
        for line in d_lines:
            assert col_d_font.getlength(line) <= col_w, line
            draw.text((cx, cy), line, font=col_d_font, fill=INK)
            cy += col_d_lh
        report.append(
            f"col {col['kicker']}: headline {len(col['headline'])} lines, "
            f"deck {len(d_lines)} lines, ends y={cy}")
        col_end = max(col_end, cy)

    # ---- footer ------------------------------------------------------
    y = col_end + 10
    draw.rectangle([MARGIN, y, W - MARGIN, y + 1], fill=INK)
    y += 10
    f_font = font(SANS, 22)
    f_bold = font(SANS_B, 22)
    label = "ALSO TODAY"
    draw.text((MARGIN, y), label, font=f_bold, fill=RED)
    lx = MARGIN + f_bold.getlength(label)
    rest = "  \u2022  COP31 ministers race to unblock climate talks in Antalya"
    assert f_font.getlength(rest) <= CONTENT_W - (lx - MARGIN), rest
    draw.text((lx, y), rest, font=f_font, fill=INK)
    y += 28
    line2 = "A Van Gogh sells for $190.4 million, a record for the artist"
    assert f_font.getlength(line2) <= CONTENT_W, line2
    draw.text((MARGIN, y), line2, font=f_font, fill=INK)
    y += 28
    s_font = font(SANS, 17)
    src = ("Sources: Associated Press, BBC News, The Wall Street Journal, "
           "Dawn  \u2022  19 November 2026")
    assert s_font.getlength(src) <= CONTENT_W, src
    draw.text((MARGIN, y), src, font=s_font, fill=MUTED)
    y += 22
    report.append(f"footer ends y={y} (canvas {H})")
    assert y <= H - 4, f"footer overflows canvas: ends y={y}"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG")
    size = os.path.getsize(OUT)
    sha = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
    print("\n".join(report))
    print(f"saved {OUT}")
    print(f"dimensions: {W}x{H}")
    print(f"bytes: {size}")
    print(f"sha256: {sha}")
    print(f"under 1 MiB: {size <= 1024 * 1024}")


if __name__ == "__main__":
    main()
