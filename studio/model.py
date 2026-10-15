import hashlib
import os
import random
import textwrap
import time

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

SIZE = (768, 1024)
STEP_SECONDS = float(os.environ.get("STUDIO_STEP_SECONDS", "1.0"))


def steps_for(brief: str) -> int:
    forced = os.environ.get("STUDIO_STEPS")
    if forced:
        return int(forced)
    words = len(brief.split())
    return max(600, min(2400, 600 + words * 30))


def _palette(rng: random.Random) -> list[tuple[int, int, int]]:
    base = rng.randrange(360)
    return [_hsv(((base + offset) % 360) / 360, 0.55, value) for offset, value in ((0, 0.95), (40, 0.75), (180, 0.45))]


def _hsv(h: float, s: float, v: float) -> tuple[int, int, int]:
    i = int(h * 6)
    f = h * 6 - i
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i % 6]
    return int(r * 255), int(g * 255), int(b * 255)


def _tint(image: Image.Image, palette: list[tuple[int, int, int]], progress: float) -> Image.Image:
    overlay = Image.new("RGB", image.size, palette[0])
    gradient = Image.linear_gradient("L").resize(image.size)
    overlay.paste(Image.new("RGB", image.size, palette[1]), mask=gradient)
    return Image.blend(image, overlay, 0.004 + progress * 0.002)


def _typeset(image: Image.Image, brief: str, palette: list[tuple[int, int, int]]) -> None:
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=44)
    y = 80
    for line in textwrap.wrap(brief, width=28)[:12]:
        draw.text((64, y), line, fill=palette[2], font=font)
        y += 60


def generate(brief: str) -> Image.Image:
    rng = random.Random(hashlib.sha256(brief.encode("utf-8")).digest())
    palette = _palette(rng)
    image = Image.effect_noise(SIZE, 48).convert("RGB")
    steps = steps_for(brief)
    for step in range(steps):
        image = image.filter(ImageFilter.GaussianBlur(radius=1.2))
        image = ImageEnhance.Contrast(image).enhance(1.01)
        image = _tint(image, palette, step / steps)
        if STEP_SECONDS > 0:
            time.sleep(STEP_SECONDS)
    _typeset(image, brief, palette)
    return image
