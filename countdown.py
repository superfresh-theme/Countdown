"""Render an animated countdown GIF (60 one-second frames) in the Digital-7 font."""
import io
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts", "digital-7.ttf")

# Countdown target: 10:00 AM Pacific (PST), November 27, 2026
END = datetime(2026, 11, 27, 10, 0, 0, tzinfo=ZoneInfo("America/Los_Angeles"))

W, H = 600, 170
SCALE = 2  # draw at 2x, then downscale for smoother edges


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _draw_frame(remaining, bg, fg, label_color, fonts):
    big, small = fonts
    s = SCALE
    img = Image.new("RGB", (W * s, H * s), bg)
    d = ImageDraw.Draw(img)

    total = max(0, int(remaining.total_seconds()))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    units = [(f"{days:02d}", "DAYS"), (f"{hours:02d}", "HOURS"),
             (f"{mins:02d}", "MINUTES"), (f"{secs:02d}", "SECONDS")]

    col_w = W * s // 4
    cell = big.getlength("0")  # fixed digit cell so "1" doesn't make numbers jump
    digit_top = 22 * s
    for i, (num, label) in enumerate(units):
        cx = col_w * i + col_w // 2
        width = cell * len(num) + 4 * s * (len(num) - 1)
        x = cx - width / 2
        for ch in num:
            # right-align each glyph in its cell, like a real 7-segment display
            d.text((x + cell - big.getlength(ch), digit_top), ch, font=big, fill=fg)
            x += cell + 4 * s
        lw = small.getlength(label)
        d.text((cx - lw / 2, 122 * s), label, font=small, fill=label_color)
        if i < 3:  # colon separators between columns
            colon_x = col_w * (i + 1) - big.getlength(":") / 2
            d.text((colon_x, digit_top), ":", font=big, fill=fg)

    return img.resize((W, H), Image.LANCZOS)


def render_gif(now=None, end=END, bg="#000000", fg="#ff2b2b", label="#bbbbbb", frames=60):
    now = now or datetime.now(timezone.utc)
    fonts = (ImageFont.truetype(FONT_PATH, 96 * SCALE), ImageFont.truetype(FONT_PATH, 24 * SCALE))
    bg, fg, label = _hex(bg), _hex(fg), _hex(label)
    remaining = end - now
    imgs = []
    for i in range(frames):
        r = remaining - timedelta(seconds=i)
        imgs.append(_draw_frame(r, bg, fg, label, fonts))
        if r.total_seconds() <= 0:
            break  # stop at 00:00:00:00
    pal = imgs[0].quantize(colors=32, method=Image.MEDIANCUT)  # one shared palette = smaller file
    imgs = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in imgs]
    buf = io.BytesIO()
    imgs[0].save(buf, format="GIF", save_all=True, append_images=imgs[1:],
                 duration=1000, loop=0, optimize=True, disposal=1)
    return buf.getvalue()


if __name__ == "__main__":
    with open("countdown-preview.gif", "wb") as f:
        f.write(render_gif())
    print("wrote countdown-preview.gif")
