"""Render an animated countdown GIF (60 one-second frames) in the Digital-7 font.

Built to be fast on small servers: the labels and colons are drawn once,
and each frame only redraws the digits.
"""
import io
import os
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

_HERE = os.path.dirname(os.path.abspath(__file__))
# Works whether the font sits next to this file or inside a "fonts" folder
FONT_PATH = next(
    (p for p in (os.path.join(_HERE, "digital-7.ttf"), os.path.join(_HERE, "fonts", "digital-7.ttf"))
     if os.path.exists(p)),
    os.path.join(_HERE, "digital-7.ttf"),
)

# Countdown target: 10:00 AM Pacific (PST), November 27, 2026
END = datetime(2026, 11, 27, 10, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))

W, H = 600, 170
LABELS = ("DAYS", "HOURS", "MINUTES", "SECONDS")
DIGIT_TOP = 22
GAP = 4


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


@lru_cache(maxsize=1)
def _fonts():
    return ImageFont.truetype(FONT_PATH, 96), ImageFont.truetype(FONT_PATH, 24)


@lru_cache(maxsize=16)
def _base(bg, fg, label):
    """Background with labels and colons; drawn once per color scheme."""
    big, small = _fonts()
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    col_w = W // 4
    for i, text in enumerate(LABELS):
        cx = col_w * i + col_w // 2
        d.text((cx - small.getlength(text) / 2, 122), text, font=small, fill=label)
        if i < 3:
            d.text((col_w * (i + 1) - big.getlength(":") / 2, DIGIT_TOP), ":", font=big, fill=fg)
    return img


def _frame(seconds_left, bg, fg, label):
    big, _ = _fonts()
    img = _base(bg, fg, label).copy()
    d = ImageDraw.Draw(img)
    total = max(0, seconds_left)
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    col_w = W // 4
    cell = big.getlength("0")  # fixed cell so "1" doesn't make numbers jump
    for i, num in enumerate((f"{days:02d}", f"{hours:02d}", f"{mins:02d}", f"{secs:02d}")):
        cx = col_w * i + col_w // 2
        x = cx - (cell * len(num) + GAP * (len(num) - 1)) / 2
        for ch in num:
            d.text((x + cell - big.getlength(ch), DIGIT_TOP), ch, font=big, fill=fg)
            x += cell + GAP
    return img


def render_gif(now=None, end=END, bg="#000000", fg="#ff2b2b", label="#bbbbbb", frames=60):
    now = now or datetime.now(timezone.utc)
    bg, fg, label = _hex(bg), _hex(fg), _hex(label)
    start = int((end - now).total_seconds())
    imgs = []
    for i in range(frames):
        left = start - i
        imgs.append(_frame(left, bg, fg, label))
        if left <= 0:
            break  # stop at 00:00:00:00
    pal = imgs[0].quantize(colors=32, method=Image.MEDIANCUT)  # one shared palette = small file
    imgs = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
    buf = io.BytesIO()
    imgs[0].save(buf, format="GIF", save_all=True, append_images=imgs[1:],
                 duration=1000, loop=0, optimize=False, disposal=1)
    return buf.getvalue()


if __name__ == "__main__":
    with open("countdown-preview.gif", "wb") as f:
        f.write(render_gif())
    print("wrote countdown-preview.gif")
