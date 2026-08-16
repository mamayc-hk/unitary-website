#!/usr/bin/env python3
"""整 9 個 game hero image: 純文字 logo, 底色 + 字色跟原盒。"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path('/Users/herry/Documents/Cherry/unitary-website/board-game')
IMG_DIR = ROOT / 'images'

# Theme per game: 底色 + 字色 + 字型, 跟原盒配色
THEMES = {
    'bohnanza': {
        'name': 'Bohnanza',
        'bg': (255, 217, 61),     # 黃色 (10週年邊框)
        'text': (139, 26, 26),    # 紅色 (盒上字)
        'font': '/System/Library/Fonts/Supplemental/Arial Black.ttf',
        'font_index': 0,
    },
    'camel-up': {
        'name': 'Camel Up',
        'bg': (232, 121, 43),     # 駱駝橙
        'text': (255, 255, 255),  # 白
        'font': '/System/Library/Fonts/Supplemental/Arial Black.ttf',
        'font_index': 0,
    },
    'take-time': {
        'name': 'Take Time',
        'bg': (61, 42, 92),       # 深紫
        'text': (255, 255, 255),  # 白
        'font': '/System/Library/Fonts/HelveticaNeue.ttc',
        'font_index': 0,
    },
    'catan': {
        'name': 'CATAN',
        'bg': (139, 26, 26),      # 紅 (盒 sunset 紅橙)
        'text': (255, 255, 255),  # 白
        'font': '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
        'font_index': 0,
    },
    'project-l': {
        'name': 'PROJECT L',
        'bg': (10, 10, 10),       # 黑
        'text': (0, 180, 216),    # 鮮藍 cyan
        'font': '/System/Library/Fonts/Supplemental/Arial Black.ttf',
        'font_index': 0,
    },
    'dnup': {
        'name': 'DNUP',
        'bg': (26, 26, 26),       # 深灰
        'text': None,             # rainbow, special handling
        'font': '/System/Library/Fonts/Supplemental/Arial Black.ttf',
        'font_index': 0,
    },
    'manila': {
        'name': 'MANILA',
        'bg': (92, 58, 30),       # 木色
        'text': (255, 215, 0),    # 金
        'font': '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
        'font_index': 0,
    },
    'seti': {
        'name': 'SETI',
        'bg': (10, 14, 46),       # 深空 navy
        'text': (255, 255, 255),  # 白
        'font': '/System/Library/Fonts/HelveticaNeue.ttc',
        'font_index': 0,
    },
    'spots': {
        'name': 'SPOTS',
        'bg': (21, 101, 192),     # 卡通藍
        'text': (255, 23, 68),    # 紅
        'font': '/System/Library/Fonts/Supplemental/Arial Black.ttf',
        'font_index': 0,
    },
}

RAINBOW_COLORS = [
    (255, 60, 60),    # 紅
    (255, 140, 0),    # 橙
    (255, 215, 0),    # 黃
    (60, 200, 80),    # 綠
    (60, 130, 255),   # 藍
]

SIZE = 500
PADDING = 50


def fit_font(draw, name, font_path, font_index, max_size=SIZE - 2 * PADDING):
    """Auto-fit font size, max 200 (constraint to leave room)."""
    for sz in range(220, 30, -5):
        try:
            font = ImageFont.truetype(font_path, sz, index=font_index)
        except TypeError:
            font = ImageFont.truetype(font_path, sz)
        bbox = draw.textbbox((0, 0), name, font=font)
        text_w = bbox[2] - bbox[0]
        if text_w <= max_size:
            return font, sz
    return font, 30


def make_hero(gid, theme):
    img = Image.new('RGB', (SIZE, SIZE), theme['bg'])
    draw = ImageDraw.Draw(img)

    name = theme['name']
    try:
        font, sz = fit_font(draw, name, theme['font'], theme.get('font_index', 0))
    except TypeError:
        font, sz = fit_font(draw, name, theme['font'], 0)

    bbox = draw.textbbox((0, 0), name, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (SIZE - text_w) / 2 - bbox[0]
    y = (SIZE - text_h) / 2 - bbox[1]

    if theme['text'] is None:
        # Rainbow per character
        cur_x = x
        for i, char in enumerate(name):
            cbbox = draw.textbbox((0, 0), char, font=font)
            char_w = cbbox[2] - cbbox[0]
            color = RAINBOW_COLORS[i % len(RAINBOW_COLORS)]
            draw.text((cur_x, y), char, fill=color, font=font)
            cur_x += char_w
    else:
        draw.text((x, y), name, fill=theme['text'], font=font)

    output = IMG_DIR / f'{gid}-hero.jpg'
    img.save(output, 'JPEG', quality=92)
    return output, sz


if __name__ == '__main__':
    print(f"Generating 9 hero images (PIL, 底色 + 字色跟原盒)...\n")
    for gid, theme in THEMES.items():
        try:
            result, sz = make_hero(gid, theme)
            print(f"  ✅ {gid:15s} font_size={sz:3d} → {result.name}")
        except Exception as e:
            print(f"  ❌ {gid:15s} ERR: {e}")
