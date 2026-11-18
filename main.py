#!/usr/bin/env python3
# Deterministic front-page generator for make.fun news-image-20261118.
# Draws a 1024x1024 PNG newspaper front page summarising 18 November 2026
# world news. No network, no randomness, no wall-clock time: the two runs
# the grader performs must write identical bytes.
import struct
import zlib
import os

W = H = 1024

# ---------- palette ----------
INK = (24, 26, 34)          # near-black ink
PAPER = (246, 242, 230)     # newsprint cream
ACCENT = (178, 34, 38)      # masthead red
BLUE = (32, 66, 120)        # diplomatic blue
GREEN = (26, 110, 70)       # market green
GREY = (120, 122, 130)      # rules and dividers
ORANGE = (214, 120, 30)     # cyclone warning

pix = bytearray([0]) * (W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        pix[i] = c[0]
        pix[i + 1] = c[1]
        pix[i + 2] = c[2]


def rect(x0, y0, x1, y1, c):
    for y in range(max(0, y0), min(H, y1)):
        base = (y * W + max(0, x0)) * 3
        n = (min(W, x1) - max(0, x0))
        for k in range(n):
            i = base + k * 3
            pix[i] = c[0]
            pix[i + 1] = c[1]
            pix[i + 2] = c[2]


# ---------- 5x7 bitmap font ----------
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    '.': ["00000", "00000", "00000", "00000", "00000", "00110", "00110"],
    ',': ["00000", "00000", "00000", "00000", "00110", "00100", "01000"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ':': ["00000", "00110", "00110", "00000", "00110", "00110", "00000"],
    '/': ["00001", "00001", "00010", "00100", "01000", "10000", "10000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '$': ["01111", "10000", "11110", "01000", "00100", "10001", "01110"],
    '%': ["10001", "10010", "00010", "00100", "01000", "01001", "10001"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '>': ["01000", "00100", "00010", "00001", "00010", "00100", "01000"],
    '<': ["00010", "00100", "01000", "10000", "01000", "00100", "00010"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


def glyph(ch):
    if ch in FONT:
        return FONT[ch]
    up = ch.upper()
    if up in FONT:
        return FONT[up]
    return FONT['?']


def text(x, y, s, c=INK, scale=1):
    for k, ch in enumerate(s):
        g = glyph(ch)
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '1':
                    for dy in range(scale):
                        for dx in range(scale):
                            px(x + k * 6 * scale + col * scale + dx,
                               y + r * scale + dy, c)


def text_center(cy, s, c=INK, scale=1):
    w = (len(s) * 6 - 1) * scale
    text((W - w) // 2, cy, s, c, scale)


# ---------- layout ----------
M = 24              # margin
CW = W - 2 * M      # content width


def masthead():
    rect(M, 14, W - M, 118, INK)
    text_center(26, "THE DAILY WORLD", PAPER, 6)
    text_center(80, "WEDNESDAY, 18 NOVEMBER 2026 - WORLD NEWS IN ONE IMAGE", ACCENT, 2)
    rect(M, 124, W - M, 128, INK)


def kicker(x, y, s, c):
    rect(x, y - 2, x + (len(s) * 6 + 6) * 2, y + 16, c)
    text(x + 3, y + 2, s, PAPER, 2)


def panel(x0, y0, x1, y1, tag, tagc, lines, scale=1):
    rect(x0, y0, x1, y1, PAPER)
    rect(x0, y0, x1, y0 + 2, INK)
    rect(x0, y0, x0 + 2, y1, INK)
    rect(x1 - 2, y0, x1, y1, INK)
    rect(x0, y1 - 2, x1, y1, INK)
    kicker(x0 + 8, y0 + 8, tag, tagc)
    yy = y0 + 34
    for ln in lines:
        text(x0 + 10, yy, ln, INK, scale)
        yy += 9 * scale


# ---------- simple iconic drawings ----------
def draw_kerch_bridge(x0, y0, w, h):
    # A cable-stayed span, second span collapsed into the sea
    sea_y = y0 + h - 16
    rect(x0, sea_y, x0 + w, y0 + h, BLUE)                 # sea
    deck_y = y0 + 62
    # left tower and right tower
    for tx in (x0 + 34, x0 + w - 46):
        rect(tx, deck_y - 58, tx + 5, sea_y, INK)
    # intact left deck from tower to mid
    mid = x0 + w // 2
    rect(x0 + 6, deck_y, x0 + 39, deck_y + 5, INK)
    rect(x0 + 34, deck_y, mid - 4, deck_y + 5, INK)
    # cables from the left tower
    for k in range(1, 7):
        cx0 = x0 + 36 - k * 5
        rect(cx0, deck_y - k * 9, cx0 + 2, deck_y, INK)
    # intact right span stub, then jagged break
    rect(mid + 12, deck_y, x0 + w - 46, deck_y + 5, INK)
    # broken pieces falling into the water
    xx = mid - 4
    yy = deck_y
    for k in range(7):
        rect(xx, yy, xx + 20 - k * 2, yy + 5, INK)
        xx += 9 - k // 2
        yy += 12
    # debris in the water
    for k, (dx, dw) in enumerate([(0, 14), (20, 9), (34, 16), (58, 7), (72, 12)]):
        rect(mid - 40 + dx, sea_y + 3 + (k % 2) * 5, mid - 40 + dx + dw, sea_y + 7 + (k % 2) * 5, INK)
    # smoke puffs above the gap
    for k in range(3):
        rect(mid + 2 + k * 16, deck_y - 30 - k * 6, mid + 14 + k * 16, deck_y - 22 - k * 6, GREY)
    text(x0 + 6, y0 + h - 12, "KERCH STRAIT", PAPER, 1)


def draw_globe_pin(x0, y0, r, pins):
    cx, cy = x0 + r, y0 + r
    for t in range(-r, r + 1):
        half = int((r * r - t * t) ** 0.5)
        rect(cx + t, cy - half, cx + t + 1, cy + half + 1, BLUE)
    for yy in range(cy - r + 3, cy + r - 2, 6):
        for t in range(-r, r + 1):
            half = int((r * r - t * t) ** 0.5)
            if (yy // 3) % 2 == 0:
                rect(cx - half + 2, yy, cx + half - 2, yy + 1, (70, 110, 160))
    # continents: rough blobs
    rect(cx - r // 2 - 4, cy - r + 8, cx - r // 2 + 8, cy - 2, GREEN)
    rect(cx - r + 4, cy - 6, cx - r // 2 - 2, cy + r - 10, GREEN)
    rect(cx + 4, cy - r + 6, cx + r - 6, cy + 2, GREEN)
    rect(cx + 2, cy + 8, cx + r // 2, cy + r - 12, GREEN)
    for (dx, dy, c) in pins:
        px(cx + dx, cy + dy, c)
        px(cx + dx - 1, cy + dy, c)
        px(cx + dx + 1, cy + dy, c)
        px(cx + dx, cy + dy - 1, c)
        px(cx + dx, cy + dy + 1, c)
        px(cx + dx, cy + dy - 2, c)
        px(cx + dx, cy + dy + 2, c)


def draw_flame(x0, y0):
    # missile flash over a radar dome
    rect(x0, y0 + 26, x0 + 60, y0 + 30, GREY)
    for t in range(14):                       # dome
        hw = int((196 - t * t) ** 0.5) // 3
        rect(x0 + 30 - hw // 2, y0 + 26 - t, x0 + 30 + hw // 2 + 1, y0 + 27 - t, INK)
    rect(x0 + 28, y0 - 6, x0 + 31, y0 + 12, ORANGE)   # incoming streak
    rect(x0 + 20, y0 - 10, x0 + 26, y0 - 6, ORANGE)
    rect(x0 + 36, y0 - 12, x0 + 42, y0 - 8, ORANGE)


def draw_chart(x0, y0, w, h):
    rect(x0, y0 + h - 1, x0 + w, y0 + h, INK)
    rect(x0, y0, x0 + 1, y0 + h, INK)
    bars = [34, 40, 44, 52, 48, 56, 62]
    for i, b in enumerate(bars):
        bx = x0 + 8 + i * (w - 16) // len(bars)
        rect(bx, y0 + h - b, bx + (w - 16) // len(bars) - 6, y0 + h - 1, GREEN)
    text(x0 + w - 44, y0 + 2, "BEAT", GREEN, 2)


def draw_storm(x0, y0):
    # cyclone swirl
    cx, cy = x0 + 26, y0 + 24
    for t in range(16, 0, -1):
        import math
        for a in range(0, 360, 30):
            rad = a * 3.14159 / 180
            x = cx + int((16 - t) * math.cos(rad) + (16 - t) * 0.35)
            y = cy + int((16 - t) * math.sin(rad) * 0.6)
            px(x, y, ORANGE)
            px(x + 1, y, ORANGE)
    for t in range(60):
        px(x0 + 4 + t, y0 + 44 + (t % 5), ORANGE)


# ---------- compose ----------
def compose():
    rect(0, 0, W, H, PAPER)
    masthead()

    # left column: lead story
    lx, lw = M, 560
    rect(lx, 140, lx + lw, 560, PAPER)
    text(lx, 148, "KERCH BRIDGE HIT AGAIN", ACCENT, 4)
    text(lx, 184, "UKRAINE STRIKES CRIMEA LINK 2ND DAY", INK, 2)
    rect(lx, 208, lx + lw, 210, GREY)
    draw_kerch_bridge(lx + 20, 220, lw - 40, 250)
    lines = [
        "KYIV: OVERNIGHT MISSILES CRITICALLY",
        "DAMAGED THE KERCH BRIDGE TO CRIMEA -",
        "SECOND STRIKE IN TWO DAYS. ZELENSKYY",
        "CALLS IT AN UNPRECEDENTED OPERATION.",
        "GERMANY BACKS NEW PATRIOT PACKAGE",
        "WITH NORWAY FOR KYIV'S AIR DEFENCE.",
    ]
    yy = 486
    for ln in lines:
        text(lx + 4, yy, ln, INK, 2)
        yy += 18

    # right column: diplomacy
    rx = M + 580
    rw = W - M - rx
    panel(rx, 140, W - M, 348, "MANILA + SHENZHEN", BLUE, [])
    draw_globe_pin(rx + 10, 198, 44, [
        (12, 4, ACCENT),    # Shenzhen
        (-2, -14, ACCENT),  # Manila
        (-34, 2, ACCENT),   # Bahrain
        (28, -20, ACCENT),  # Europe
    ])
    text(rx + 104, 200, "TRUMP IN MANILA:", INK, 2)
    text(rx + 104, 218, "QUAD SUMMIT, THEN", INK, 2)
    text(rx + 104, 236, "APEC SHENZHEN -", INK, 2)
    text(rx + 104, 254, "PUTIN ARRIVES;", INK, 2)
    text(rx + 104, 272, "TRUMP-XI-PUTIN", INK, 2)
    text(rx + 104, 290, "TRILATERAL THU", INK, 2)
    text(rx + 14, 312, "CHINA CUTS CANADA TARIFFS AS XI", INK, 1)
    text(rx + 14, 324, "MEETS CARNEY, SHEINBAUM BEFORE", INK, 1)
    text(rx + 14, 336, "THURSDAY'S TRUMP SUMMIT", INK, 1)

    panel(rx, 358, W - M, 560, "US - IRAN", ACCENT, [])
    draw_flame(rx + 16, 402)
    text(rx + 92, 400, "TIT-FOR-TAT STRIKES:", INK, 1)
    text(rx + 92, 412, "IRAN HITS US RADAR IN", INK, 1)
    text(rx + 92, 424, "BAHRAIN; US HITS QESHM", INK, 1)
    text(rx + 92, 436, "MISSILE SITE. TALKS VIA", INK, 1)
    text(rx + 92, 448, "OMAN AND QATAR DRAG ON.", INK, 1)
    text(rx + 16, 470, "US INTEL: IRAN PLOTS DC DIRTY", INK, 1)
    text(rx + 16, 484, "BOMB; WHITE HOUSE: NO CREDIBLE", INK, 1)
    text(rx + 16, 498, "THREAT. GULF STATES WARN", INK, 1)
    text(rx + 16, 512, "RESIDENTS TO SHELTER.", INK, 1)
    text(rx + 16, 530, "TRUMP: 'THEY WILL PAY A", ACCENT, 1)
    text(rx + 16, 544, "PRICE NEVER PAID BEFORE'", ACCENT, 1)

    # bottom band: three small stories
    y0 = 574
    rect(M, y0, W - M, y0 + 2, INK)

    c1x, c1w = M, 300
    panel(c1x, y0 + 12, c1x + c1w, 860, "NVIDIA", GREEN, [])
    draw_chart(c1x + 30, 640, c1w - 60, 130)
    text(c1x + 10, 786, "EARNINGS BEAT FORECASTS", INK, 1)
    text(c1x + 10, 800, "AFTER HUANG RESIGNATION;", INK, 1)
    text(c1x + 10, 814, "HE WOULD BE 'HONORED' TO", INK, 1)
    text(c1x + 10, 828, "RETURN AS CEO. STOCKS", INK, 1)
    text(c1x + 10, 842, "SLIDE AHEAD OF REPORT.", INK, 1)

    c2x = c1x + c1w + 14
    panel(c2x, y0 + 12, c2x + c1w, 860, "HEALTH", ACCENT, [])
    # virus circle
    for a in range(0, 360, 45):
        import math
        rad = a * 3.14159 / 180
        px(c2x + 40 + int(16 * math.cos(rad)), 662 + int(16 * math.sin(rad)), ACCENT)
    for t in range(-16, 17):
        hw = int((256 - t * t) ** 0.5)
        rect(c2x + 40 - hw, 662 - t // 2 if False else 662 + (t if abs(t) < 17 else 0), c2x + 41, 663, ACCENT)
    rect(c2x + 26, 650, c2x + 54, 674, ACCENT)
    text(c2x + 60, 648, "US LOSES MEASLES", INK, 1)
    text(c2x + 60, 660, "ELIMINATION STATUS", INK, 1)
    text(c2x + 60, 672, "AFTER 26 YEARS", INK, 1)
    text(c2x + 10, 700, "WHO: DISEASE NOW ENDEMIC", INK, 1)
    text(c2x + 10, 714, "AS OUTBREAKS SPREAD.", INK, 1)
    text(c2x + 10, 732, "ALSO: FAA PAUSES ROUTER", INK, 1)
    text(c2x + 10, 746, "ROLL-OUT AFTER GROUND", INK, 1)
    text(c2x + 10, 760, "STOP; $50BN UPGRADE ASKED", INK, 1)
    text(c2x + 10, 778, "SPAIN: 11,000+ REACHED", INK, 1)
    text(c2x + 10, 792, "CANARY ISLES THIS MONTH", INK, 1)
    text(c2x + 10, 810, "AUSTRALIA PAY GAP FALLS", INK, 1)
    text(c2x + 10, 824, "BELOW 20%, FIRST EVER.", INK, 1)
    text(c2x + 10, 842, "UK PM: 'NO RUSH' ON EU", INK, 1)

    c3x = c2x + c1w + 14
    c3w = W - M - c3x
    panel(c3x, y0 + 12, W - M, 860, "BAY OF BENGAL", ORANGE, [])
    draw_storm(c3x + 20, 630)
    text(c3x + 80, 640, "CYCLONE AKVAN", ORANGE, 1)
    text(c3x + 80, 652, "TO HIT ANDHRA COAST", ORANGE, 1)
    text(c3x + 80, 664, "NOV 20, 120 KM/H", ORANGE, 1)
    text(c3x + 10, 690, "MODI IN MANILA: FREE E-", INK, 1)
    text(c3x + 10, 704, "VISAS FOR ASEAN, MARITIME", INK, 1)
    text(c3x + 10, 718, "SECURITY TIES PROPOSED.", INK, 1)
    text(c3x + 10, 736, "SIBERIA: AN-12 CRASH", INK, 1)
    text(c3x + 10, 750, "KILLS ALL 17 ABOARD.", INK, 1)
    text(c3x + 10, 768, "IMRAN KHAN, IN JAIL:", INK, 1)
    text(c3x + 10, 782, "LETTER SAYS HE MAY DIE.", INK, 1)
    text(c3x + 10, 800, "CRICKET: DHONI QUITS", INK, 1)
    text(c3x + 10, 814, "IPL, JOINS CSK AS MENTOR.", INK, 1)
    text(c3x + 10, 832, "ICC: JAY SHAH RE-ELECTED", INK, 1)

    # footer
    rect(M, 876, W - M, 880, INK)
    text_center(890, "TODAY IN ONE FRAME - DIPLOMACY IN ASIA, WAR IN EUROPE AND THE GULF,", INK, 2)
    text_center(912, "EARNINGS IN SILICON VALLEY - WEDNESDAY 18 NOVEMBER 2026", ACCENT, 2)
    rect(M, 936, W - M, 940, GREY)
    text_center(950, "PAGE ONE / NO.18 / FREE / EDITED BY AN AI AGENT FOR MAKE.FUN", GREY, 1)


compose()

# ---------- encode PNG ----------
raw = b''.join(b'\x00' + bytes(pix[y*W*3:(y+1)*W*3]) for y in range(H))
comp = zlib.compress(raw, 9)


def chunk(tag, data):
    c = struct.pack(">I", len(data)) + tag + data
    return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
png = (b'\x89PNG\r\n\x1a\n'
       + chunk(b'IHDR', ihdr)
       + chunk(b'IDAT', comp)
       + chunk(b'IEND', b''))

out = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'entry.png'), 'wb') as f:
    f.write(png)
print("wrote entry.png", len(png), "bytes")
