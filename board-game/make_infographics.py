#!/usr/bin/env python3
"""合併每個 game 嘅 step images 做 1 張 1:2 (landscape 2:1) infographic。"""
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
IMG_DIR = ROOT / 'images'
TARGET_W, TARGET_H = 1600, 800  # 2:1 landscape
GAP = 8  # pixels between panels
BG = (255, 255, 255)


def merge_step_images(game_id, step_imgs, box_image):
    """合併 step images 做 1 張 2:1 infographic。
    過濾掉 box image (已經喺 hero render)。
    0 個 step → return None
    1 個 step → return 該 image resized to 2:1
    N 個 step → 排成 1 row
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
        # Try images/ directory if file not found
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
    cell_w = (TARGET_W - GAP * (n - 1)) // n
    cell_h = TARGET_H

    canvas = Image.new('RGB', (TARGET_W, TARGET_H), BG)

    for i, img in enumerate(images):
        # Resize keeping aspect, fit in cell
        iw, ih = img.size
        scale = min(cell_w / iw, cell_h / ih)
        new_w = int(iw * scale)
        new_h = int(ih * scale)
        resized = img.resize((new_w, new_h), Image.LANCZOS)
        # Center in cell
        x = i * (cell_w + GAP) + (cell_w - new_w) // 2
        y = (cell_h - new_h) // 2
        canvas.paste(resized, (x, y))

    output = IMG_DIR / f'infographic-{game_id}.jpg'
    canvas.save(output, 'JPEG', quality=85, optimize=True)
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
            print(f"  ✅ {gid:15s} {n_raw} raw → {result.name} {size}")
        else:
            print(f"  ⏭️  {gid:15s} 0 step images, skip")


if __name__ == '__main__':
    main()
