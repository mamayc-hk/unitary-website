#!/usr/bin/env python3
"""合併每個 game 嘅 step images 做 1 張 2:1 (1600x800) infographic。

Layout policy:
- 8 step → 2x4 (rows=2, cols=4)
- 4 step → 2x2 (rows=2, cols=2)
- 2 step → 1x2 (rows=1, cols=2)
- 1 step → 1x1 (full canvas)
- 0 step → skip

每個 step 圖:round corners 8px + white gap 10px + step number badge
(white circle 32px + black 1-2-3... number 20px) 喺 cell 左上角。
"""
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
IMG_DIR = ROOT / 'images'
TARGET_W, TARGET_H = 1600, 800  # 2:1 landscape
GAP = 10  # white gap between panels
RADIUS = 8  # rounded corners
BG = (255, 255, 255)
BADGE_DIAM = 32  # step number badge circle diameter
BADGE_FONT = 20  # badge number font size (pt)
BADGE_BORDER = 1.5  # subtle dark border for contrast on light step imgs


def compute_grid(n):
    """決定 rows x cols layout。8→2x4, 4→2x2, 2→1x2, 1→1x1。"""
    if n <= 1:
        return (1, 1)
    if n == 2:
        return (1, 2)
    if n <= 4:
        return (2, 2)
    if n <= 6:
        return (2, 3)
    if n <= 8:
        return (2, 4)
    if n <= 9:
        return (3, 3)
    # fallback: ceiling cols, ≤2 rows
    cols = (n + 1) // 2
    return (2, cols)


def round_corners(img, radius):
    """將圖嘅 4 角做 rounded corners。Return RGBA,角位 transparent。"""
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), img.size], radius=radius, fill=255
    )
    img.putalpha(mask)
    return img


def get_badge_font():
    """Load font (size 20). Try system fonts, fallback to PIL default."""
    candidates = [
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/SFNSMono.ttf',
        '/Library/Fonts/Arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, BADGE_FONT)
            except OSError:
                continue
    return ImageFont.load_default()


def draw_step_badge(canvas, cell_x, cell_y, cell_w, cell_h, number):
    """喺 cell 左上角畫 white circle + 黑色 number badge。
    位置:距 cell 左 + 上 8px 內 margin。
    """
    draw = ImageDraw.Draw(canvas)
    margin = 8
    cx = cell_x + margin + BADGE_DIAM // 2
    cy = cell_y + margin + BADGE_DIAM // 2
    r = BADGE_DIAM // 2
    bbox = (cx - r, cy - r, cx + r, cy + r)

    # White fill + dark border for visibility
    draw.ellipse(bbox, fill=(255, 255, 255, 255),
                 outline=(40, 40, 40, 220), width=int(BADGE_BORDER))

    # Center the number text
    font = get_badge_font()
    text = str(number)
    tbbox = draw.textbbox((0, 0), text, font=font)
    tw = tbbox[2] - tbbox[0]
    th = tbbox[3] - tbbox[1]
    tx = cx - tw / 2 - tbbox[0]
    ty = cy - th / 2 - tbbox[1]
    draw.text((tx, ty), text, fill=(20, 20, 20, 255), font=font)


def merge_step_images(game_id, step_imgs, box_image):
    """合併 step images 做 1 張 2:1 infographic。

    過濾掉 box image (已經喺 hero render)。
    Layout: 2xN grid 配 step number badge + rounded corners。
    """
    # Filter out box image
    box_filename = box_image.split('/')[-1] if box_image else ''
    filtered = [
        img for img in step_imgs
        if img.split('/')[-1] != box_filename and 'box' not in img.split('/')[-1].lower()
    ]

    if not filtered:
        return None

    # Open all images
    images = []
    for img_path in filtered:
        full_path = ROOT / img_path if not img_path.startswith(str(ROOT)) else Path(img_path)
        if not full_path.exists():
            alt = IMG_DIR / Path(img_path).name
            if alt.exists():
                full_path = alt
        if not full_path.exists():
            print(f"  ⚠️  Missing: {img_path}")
            continue
        images.append(Image.open(full_path).convert('RGB'))

    if not images:
        return None

    n = len(images)
    rows, cols = compute_grid(n)

    # Cell size (with gaps between cells, no outer margin so canvas = 2:1)
    cell_w = (TARGET_W - GAP * (cols - 1)) // cols
    cell_h = (TARGET_H - GAP * (rows - 1)) // rows

    canvas = Image.new('RGB', (TARGET_W, TARGET_H), BG)

    for i, img in enumerate(images):
        row = i // cols
        col = i % cols
        cell_x = col * (cell_w + GAP)
        cell_y = row * (cell_h + GAP)

        # Resize keeping aspect, fit inside cell
        iw, ih = img.size
        scale = min(cell_w / iw, cell_h / ih)
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Center inside cell
        ox = cell_x + (cell_w - new_w) // 2
        oy = cell_y + (cell_h - new_h) // 2

        # Round corners then paste
        rgba = round_corners(resized, RADIUS)
        canvas.paste(rgba, (ox, oy), mask=rgba)

        # Step number badge (top-left of cell, 1-indexed)
        draw_step_badge(canvas, cell_x, cell_y, cell_w, cell_h, i + 1)

    output = IMG_DIR / f'infographic-{game_id}.jpg'
    # Quality 82: bohnanza 8-panel dense layout stays < 200KB without
    # visibly hurting 1200x896 step 圖 detail
    canvas.save(output, 'JPEG', quality=82, optimize=True)
    return output


def main():
    with open(ROOT / 'games.json') as f:
        data = json.load(f)

    print(f"Merging infographics for {len(data['games'])} games...\n")
    for g in data['games']:
        gid = g['id']
        step_imgs = g.get('step_images', [])
        box = g.get('box_image', '')
        n_raw = len(step_imgs)
        result = merge_step_images(gid, step_imgs, box)
        if result:
            size = Image.open(result).size
            fsize = result.stat().st_size / 1024
            print(f"  ✅ {gid:15s} {n_raw} raw → {result.name} {size}  {fsize:.0f}KB")
        else:
            print(f"  ⏭️  {gid:15s} 0 step images, skip")


if __name__ == '__main__':
    main()
