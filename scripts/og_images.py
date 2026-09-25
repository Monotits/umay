#!/usr/bin/env python3
"""Render 1200x630 social preview images (assets/og/<slug>.png) from the product catalogue. Requires Pillow."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / 'content/seo/products.json').read_text())
COLORS = {'violet': (139, 92, 246), 'orange': (249, 115, 22), 'pink': (236, 72, 153), 'green': (34, 197, 94),
          'amber': (245, 158, 11), 'cyan': (6, 182, 212)}
FONTS = ['/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', '/System/Library/Fonts/SFNS.ttf',
         '/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
         '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
FONTS_REG = ['/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf', '/System/Library/Fonts/SFNS.ttf',
             '/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']


def font(paths, size):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def rounded(img, radius):
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    img.putalpha(mask)
    return img


def wrap(draw, text, fnt, width):
    lines, line = [], ''
    for word in text.split():
        test = (line + ' ' + word).strip()
        if draw.textlength(test, font=fnt) <= width:
            line = test
        else:
            lines.append(line)
            line = word
    return lines + [line]


def render(p):
    W, H = 1200, 630
    accent = COLORS.get(p.get('color'), (37, 99, 235))
    img = Image.new('RGB', (W, H), (11, 15, 25))
    glow = Image.new('RGB', (W, H), accent)
    grad = Image.linear_gradient('L').rotate(90).resize((W, H))
    img = Image.composite(glow, img, grad.point(lambda v: int(v * 0.28)))
    d = ImageDraw.Draw(img)
    mac = p['platform'] == 'macOS'
    text_w = 560 if not mac else 520
    icon = rounded(Image.open(ROOT / p['icon']).convert('RGBA').resize((132, 132)), 30)
    img.paste(icon, (64, 70), icon)
    d.text((64, 232), p['name'], font=font(FONTS, 68), fill='white')
    y = 330
    for line in wrap(d, p['heading'], font(FONTS_REG, 34), text_w)[:3]:
        d.text((64, y), line, font=font(FONTS_REG, 34), fill=(210, 214, 225))
        y += 46
    d.text((64, 548), 'umay.dev', font=font(FONTS, 28), fill=accent)
    d.text((64 + d.textlength('umay.dev', font=font(FONTS, 28)) + 16, 552),
           'Download on the ' + ('Mac ' if mac else '') + 'App Store', font=font(FONTS_REG, 24), fill=(160, 166, 180))
    shot = Image.open(ROOT / p['screenshots'][0]['src']).convert('RGBA')
    if mac:
        shot.thumbnail((560, 440))
        x, y0 = W - shot.width - 40, (H - shot.height) // 2
        shot = rounded(shot, 14)
    else:
        shot.thumbnail((290, 580))
        x, y0 = W - shot.width - 120, 70
        shot = rounded(shot, 28)
    img.paste(shot, (x, y0), shot)
    out = ROOT / 'assets/og' / (p['slug'] + '.png')
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


if __name__ == '__main__':
    for product in PRODUCTS:
        print(render(product).relative_to(ROOT))
