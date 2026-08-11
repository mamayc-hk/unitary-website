#!/usr/bin/env python3
"""
Unitary 開枱指南 — Build script
對返 unitary-website 嘅 blog.css + 兩欄 layout, server-render 8 個 game page
(解決 in-app browser JS 唔 hydrate 嘅 issue, 對返 user 嘅教客 review 痛點)
"""
import json
import re
import os
from pathlib import Path

ROOT = Path('/Users/herry/Documents/Cherry/unitary-website/board-game')
GUIDE_ROOT = Path('/Users/herry/Documents/Cherry/unitary-website')

# === 1. Markdown → HTML parser (對返我哋 content/<id>.md 嘅 syntax) ===
def escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def md_inline(text):
    """Inline: bold, italic, code, links"""
    # Escape HTML first
    text = escape_html(text)
    # Code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text

def md_to_html(md_text):
    """Convert markdown to HTML block-level + inline."""
    lines = md_text.split('\n')
    out = []
    in_list = None  # 'ul' | 'ol' | None
    in_quote = False
    para_buf = []

    def flush_para():
        nonlocal para_buf
        if para_buf:
            out.append('<p>' + md_inline(' '.join(para_buf)) + '</p>')
            para_buf = []

    def flush_list():
        nonlocal in_list
        if in_list:
            out.append(f'</{in_list}>')
            in_list = None

    def flush_quote():
        nonlocal in_quote
        if in_quote:
            out.append('</blockquote>')
            in_quote = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Empty line
        if not stripped:
            flush_para()
            flush_list()
            flush_quote()
            i += 1
            continue

        # Horizontal rule
        if stripped == '---':
            flush_para()
            flush_list()
            flush_quote()
            out.append('<hr>')
            i += 1
            continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            flush_para()
            flush_list()
            flush_quote()
            level = len(m.group(1))
            out.append(f'<h{level}>{md_inline(m.group(2))}</h{level}>')
            i += 1
            continue

        # Blockquote
        if stripped.startswith('>'):
            flush_para()
            flush_list()
            if not in_quote:
                out.append('<blockquote>')
                in_quote = True
            content = stripped.lstrip('>').strip()
            out.append('<p>' + md_inline(content) + '</p>')
            i += 1
            continue
        else:
            flush_quote()

        # Unordered list
        m = re.match(r'^[-*]\s+(.*)', stripped)
        if m:
            flush_para()
            if in_list != 'ul':
                flush_list()
                out.append('<ul>')
                in_list = 'ul'
            out.append('<li>' + md_inline(m.group(1)) + '</li>')
            i += 1
            continue

        # Ordered list
        m = re.match(r'^\d+\.\s+(.*)', stripped)
        if m:
            flush_para()
            if in_list != 'ol':
                flush_list()
                out.append('<ol>')
                in_list = 'ol'
            out.append('<li>' + md_inline(m.group(1)) + '</li>')
            i += 1
            continue

        # Paragraph
        para_buf.append(stripped)
        i += 1

    flush_para()
    flush_list()
    flush_quote()
    return '\n'.join(out)


# === 2. Page template (對返 unitary-website 兩欄 layout + blog.css) ===
def render_game_page(game, content_md):
    """Render 一個 game page HTML."""
    name = game['name']
    name_en = game['name_en']
    tagline = game.get('tagline', '')
    summary = game.get('summary', '')
    publisher = game.get('publisher', '')
    cats = game.get('category', [])
    min_p = game['min_players']
    max_p = game['max_players']
    teach = game.get('teach_time', 0)
    play = game.get('play_time', '')
    diff = game.get('difficulty_label', '')
    langs = game.get('language_versions', [])
    bgg = game.get('bgg_url', '')
    box = game.get('box_image', '')
    step_imgs = game.get('step_images', [])
    tactics_n = game.get('tactical_notes_count', 0)
    has_tb = game.get('has_tiebreaker', False)
    is_complete = game.get('is_complete', True)
    fit = game.get('customer_fit', {})

    # Markdown → HTML (server-render 全部 long-form content)
    long_form_html = md_to_html(content_md)

    # Customer fit list
    fit_items = ''.join(f'<li>{md_inline(k)}: {md_inline(v)}</li>\n' for k, v in fit.items())

    # Box image
    box_html = ''
    if box:
        # box path 對返 new location: images/<id>-box.jpg (relative to board-game/)
        box_filename = box.split('/')[-1]
        box_html = f'<figure><img src="images/{box_filename}" alt="{name} 盒面" loading="lazy"><figcaption>{name} ({name_en}) — {publisher}</figcaption></figure>'

    # Step images 對返新 location
    step_html = ''
    if step_imgs:
        step_items = ''
        for idx, img in enumerate(step_imgs):
            img_filename = img.split('/')[-1]
            step_items += f'<figure><img src="images/{img_filename}" alt="Step {idx+1}" loading="lazy"><figcaption>Step {idx+1}</figcaption></figure>\n'
        step_html = f'<div class="photo-grid">{step_items}</div>'

    # Complete status badge
    complete_badge = '✅ 完整教學' if is_complete else '⚠️ 內容待補'

    # Sidebar quick-jump (8 個 game)
    sidebar_qj = ''
    all_games = sorted(
        load_games(),
        key=lambda g: (0 if g.get('is_kickoff') else 1, g['id'])
    )
    for g in all_games:
        kickoff_marker = ' 🌟 (kickoff)' if g.get('is_kickoff') else ''
        sidebar_qj += f'<a href="{g["id"]}.html">{g["name"]}{kickoff_marker}</a>\n'

    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} ({name_en}) — {tagline} | UNITARY 開枱指南</title>
    <meta name="description" content="{escape_html(summary)}">
    <meta name="keywords" content="桌遊,教學,桌遊教學,{escape_html(name)},{escape_html(name_en)},board game,{escape_html(",".join(cats))},香港桌遊,新手桌遊,教客,旺角">
    <link rel="canonical" href="https://unitaryhk.com/board-game/{game['id']}.html">
    <meta property="og:title" content="{name} ({name_en}) — {tagline}">
    <meta property="og:description" content="{escape_html(summary)}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="stylesheet" href="../blog.css">
</head>
<body>

<div class="nav"><div class="nav-inner">
    <a href="../index.html"><img src="../logo.png" alt="UNITARY"></a>
    <a href="index.html" style="margin-left:auto;color:var(--color-text-soft);font-size:0.95rem">桌遊教學 →</a>
</div></div>

<div class="layout">
    <div class="main">
        <div class="main-content">
            <a href="index.html" class="back">← 返回桌遊列表</a>
            <div class="date">{complete_badge}</div>
            <h1>{name} ({name_en}) — {tagline}</h1>
            <p style="color:var(--color-text-soft);font-size:0.95rem">出版: {escape_html(publisher)} · 類別: {escape_html(", ".join(cats))}</p>

            {box_html}

            <div class="game-meta">
                <div class="game-meta-item">
                    <div class="label">人數</div>
                    <div class="value">{min_p}-{max_p}</div>
                </div>
                <div class="game-meta-item">
                    <div class="label">教學</div>
                    <div class="value">{teach} min</div>
                </div>
                <div class="game-meta-item">
                    <div class="label">遊戲</div>
                    <div class="value">{play}</div>
                </div>
                <div class="game-meta-item">
                    <div class="label">難度</div>
                    <div class="value">{diff}</div>
                </div>
                <div class="game-meta-item">
                    <div class="label">語言</div>
                    <div class="value">{escape_html(", ".join(langs))}</div>
                </div>
            </div>

            <h2>一句話總覽</h2>
            <p>{summary}</p>

            <h2>玩法 step 圖</h2>
            {step_html}

            <div class="long-form">
                {long_form_html}
            </div>

            <hr>

            <h2>🛒 配合資源 (Cross-sell)</h2>
            <div class="cross-sell">
                <p>教客時可以一併推薦:</p>
                <ul>
                    <li><strong>DOSHA 木盒</strong>: <a href="https://instagram.com/dosha.woodcraft" target="_blank" rel="noopener">@dosha.woodcraft</a> 嘅木製收納盒, 配 {name} 嘅 card 完美 fit。</li>
                    <li><strong>UNITARY STL</strong>: <a href="https://cults3d.com/zh/y%C3%B2ngh%C3%B9/mamayc/s%C4%81nw%C3%A8i-m%C3%B3-x%C3%ADng" target="_blank" rel="noopener">Cults3D 商店</a> 有 3D 打印配件, 對應返多個 board game。</li>
                    <li><strong>旺角新手桌遊</strong>: 旺角實體店, 教客 review 即場試玩。</li>
                </ul>
            </div>

            <hr>

            <h2>延伸閱讀</h2>
            {f'<p><a href="{bgg}" target="_blank" rel="noopener" class="btn-cta btn-secondary">📊 BoardGameGeek 詳細資料 →</a></p>' if bgg else ''}

            <p style="margin-top:40px"><a href="index.html" class="back">← 返回桌遊列表</a></p>
        </div>
    </div>

    <div class="side">
        <div class="side-box">
            <h3>關於</h3>
            <div class="about-text">
                <p><strong>Herry Ma</strong></p>
                <p>兼職 @ 旺角新手桌遊 + UNITARY 創辦人。本 blog 對應教客前 review 場景。</p>
                <p>
                    <a href="https://instagram.com/unitary.hk" target="_blank">Instagram →</a>
                    &nbsp;·&nbsp;
                    <a href="https://cults3d.com/zh/y%C3%B2ngh%C3%B9/mamayc/s%C4%81nw%C3%A8i-m%C3%B3-x%C3%ADng" target="_blank">Cults3D →</a>
                </p>
            </div>
        </div>
        <div class="side-box">
            <h3>快速跳轉 (8 個 game)</h3>
            <div class="side-rec">
                {sidebar_qj}
            </div>
        </div>
        <div class="side-box">
            <h3>教客 checklist</h3>
            <div class="about-text">
                <p>教客前 5 分鐘 review:</p>
                <ul style="padding-left:16px;font-size:0.95rem">
                    <li>✅ 玩法 + 設置</li>
                    <li>{'✅' if tactics_n > 0 else '⚠️'} 戰術提示 ({tactics_n} 條)</li>
                    <li>{'✅' if has_tb else '⚠️ 待補'} tiebreaker</li>
                    <li>✅ 客戶推介</li>
                    <li>✅ 客 query 對應</li>
                </ul>
            </div>
        </div>
    </div>
</div>

<div class="blog-footer">
    <p>© 2026 UNITARY 開枱指南 &nbsp;·&nbsp;
    <a href="../index.html">UNITARY 主站</a> &nbsp;·&nbsp;
    <a href="https://instagram.com/unitary.hk">Instagram</a> &nbsp;·&nbsp;
    <a href="../sitemap.xml">Sitemap</a> &nbsp;·&nbsp;
    CC BY-NC-SA 4.0</p>
</div>

</body>
</html>
'''


# === 3. Game list index page (board-game/index.html) ===
def load_games():
    with open(ROOT / 'games.json') as f:
        return json.load(f)['games']


def render_index_page():
    games = load_games()
    # Sort: kickoff first, then complete, then incomplete
    sorted_games = sorted(games, key=lambda g: (
        0 if g.get('is_kickoff') else 1,
        0 if g.get('is_complete', True) else 1,
        g['id']
    ))

    # 對每個 game generate 一個 card
    cards = []
    for g in sorted_games:
        box_filename = g.get('box_image', '').split('/')[-1] if g.get('box_image') else ''
        box_html = f'<img src="images/{box_filename}" alt="{escape_html(g["name"])} 盒面" loading="lazy">' if box_filename else '🎲'
        pending = '' if g.get('is_complete', True) else ' <span style="color:var(--color-warn)">⚠️ 待補</span>'

        cards.append(f'''        <a class="game-card" href="{g['id']}.html">
            <div class="game-card-box">{box_html}</div>
            <div class="game-card-body">
                <h3>{g['name']}</h3>
                <p class="game-card-tagline">{g.get('tagline', '')}</p>
                <div class="game-card-meta">
                    <span>👥 {g['min_players']}-{g['max_players']}人</span>
                    <span>⏱️ {g['play_time']}</span>
                    <span>📚 {g['difficulty_label']}</span>{pending}
                </div>
            </div>
        </a>''')

    cards_html = '\n'.join(cards)

    # Quick reference (對返旺角 query 場景, 從 index.html 對 unitary-guide copy)
    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>桌遊教學 — UNITARY 開枱指南 (board game sub-section)</title>
    <meta name="description" content="香港原創桌遊教學網誌 (sub-section of UNITARY)。對應旺角客 query 場景, 由新手到進階一站式教學。8 個 game, 完整玩法 + 戰術 + tiebreaker + 客戶推介 + 客 query 對應。">
    <meta name="keywords" content="桌遊,教學,桌遊教學,board game,香港桌遊,新手桌遊,眾豆得金,駱駝大賽,Take Time,卡坦島,SETI,教客,旺角,桌遊店,UNITARY">
    <link rel="canonical" href="https://unitaryhk.com/board-game/">
    <meta property="og:title" content="桌遊教學 — UNITARY 開枱指南">
    <meta property="og:description" content="對應旺角客 query 場景嘅桌遊教學網誌。教客前最後一次 review 就夠。">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="stylesheet" href="../blog.css">
</head>
<body>

<div class="nav"><div class="nav-inner">
    <a href="../index.html"><img src="../logo.png" alt="UNITARY"></a>
    <a href="../index.html" style="margin-left:auto;color:var(--color-text-soft);font-size:0.95rem">← UNITARY 主站</a>
</div></div>

<div class="layout">
    <div class="main">
        <div class="intro">
            <div class="tag-line">Design once. Play forever.</div>
            <h1>UNITARY 開枱指南</h1>
            <p>香港原創桌遊教學網誌。對應旺角客 query 場景, 由新手到進階一站式教學。每個 game 都有完整玩法、戰術、tiebreaker、客戶推介 — 教客前最後一次 review 就夠。</p>
            <p style="margin-top:12px;"><a href="#quick-ref" class="btn-cta">📋 揾 game 速查 (對應旺角 query) →</a></p>
        </div>

        <h2>已收錄桌遊 (8 個 game)</h2>
        <p>由最熱門嘅 <a href="bohnanza.html">眾豆得金</a> 開始。對返 <a href="https://www.notion.so/2097b25a969480c7b5ecca4ee7fd6da2" target="_blank" rel="noopener">Notion 玩過嘅桌遊 database</a>。</p>

        <div class="game-grid">
{cards_html}
        </div>

        <hr id="quick-ref">

        <h2>揾 game 速查 (對應旺角 query 場景)</h2>
        <p>客嚟到問「30 min 玩咩」「2 個人嚟」, 唔使再翻 Notion, 睇呢個 list 就得:</p>

        <h3>🆕 新手第一次玩</h3>
        <ul>
            <li><a href="camel-up.html">駱駝大賽 2.0</a> — 規則最淺, 8 人派對, 5 min 教完</li>
            <li><a href="dnup.html">DNUP</a> — 旋轉機制易明, 15 min 完一局</li>
            <li><a href="take-time.html">Take Time</a> — 合作向, 冇挫敗感</li>
        </ul>

        <h3>⏱️ 30 min 內想完一局</h3>
        <ul>
            <li><a href="camel-up.html">駱駝大賽 2.0</a> — 10 min 教, 30 min 完</li>
            <li><a href="dnup.html">DNUP</a> — 10 min 教, 15-20 min 完</li>
        </ul>

        <h3>👥 2 個人嚟</h3>
        <ul>
            <li><a href="project-l.html">Project L</a> — 1-4 人, 2 人好 work</li>
            <li><a href="bohnanza.html">眾豆得金</a> — 中文版, 2-7 人彈性</li>
            <li><a href="take-time.html">Take Time</a> — 合作默契</li>
        </ul>

        <h3>👨‍👩‍👧 家庭 / 帶小朋友</h3>
        <ul>
            <li><a href="take-time.html">Take Time</a> — 合作, 唔會有人被淘汰</li>
            <li><a href="camel-up.html">駱駝大賽 2.0</a> — 派對, 小朋友都識玩</li>
            <li><a href="project-l.html">Project L</a> — 拼圖, 1-4 人彈性</li>
        </ul>

        <h3>🧠 進階 / 燒腦</h3>
        <ul>
            <li><a href="catan.html">卡坦島</a> — 經典德式策略</li>
            <li><a href="manila.html">馬尼拉</a> — 經濟 + 走私</li>
            <li><a href="bohnanza.html">眾豆得金</a> — 談判深</li>
        </ul>

        <h3>🇭🇰 中文版 (唔想睇 ENG 規則)</h3>
        <ul>
            <li><a href="bohnanza.html">眾豆得金</a> — 新天鵝堡中文版, 旺角大路貨</li>
            <li><a href="catan.html">卡坦島</a> — 劍領中文版, 經典</li>
            <li><a href="take-time.html">Take Time</a> — Libellud 中文版</li>
        </ul>

        <h3>🚀 2024 年最新 (SETI)</h3>
        <ul>
            <li><a href="seti.html">SETI</a> — 搜尋外星文明中重歐, Kennerspiel 候選, 1-4 人</li>
        </ul>

    </div>

    <div class="side">
        <div class="side-box">
            <h3>關於</h3>
            <div class="about-text">
                <p><strong>Herry Ma</strong></p>
                <p>兼職 @ 旺角新手桌遊 + UNITARY 創辦人。本 blog 對應教客前 review 場景。</p>
                <p>
                    <a href="https://instagram.com/unitary.hk" target="_blank">Instagram →</a>
                    &nbsp;·&nbsp;
                    <a href="https://cults3d.com/zh/y%C3%B2ngh%C3%B9/mamayc/s%C4%81nw%C3%A8i-m%C3%B3-x%C3%ADng" target="_blank">UNITARY STL →</a>
                </p>
            </div>
        </div>
        <div class="side-box">
            <h3>相關 UNITARY 生態</h3>
            <div class="side-rec">
                <a href="../index.html">UNITARY 主站 (3D 打印)</a>
                <a href="../post/splendor-organizer-design.html">Splendor 收納盒</a>
                <a href="../post/carcassonne-frame.html">卡卡頌保護框</a>
                <a href="../post/board-game-organizer-comparison.html">桌遊收納比較</a>
            </div>
        </div>
        <div class="side-box">
            <h3>教客 checklist</h3>
            <div class="about-text">
                <p>教任何 game 之前, 5 分鐘 review:</p>
                <ul style="padding-left:16px;font-size:0.95rem">
                    <li>✅ 玩法 + 設置</li>
                    <li>✅ 戰術提示 (5+ 條)</li>
                    <li>✅ tiebreaker</li>
                    <li>✅ 客戶推介</li>
                    <li>✅ 客 query 對應</li>
                </ul>
            </div>
        </div>
    </div>
</div>

<div class="blog-footer">
    <p>© 2026 UNITARY 開枱指南 &nbsp;·&nbsp;
    <a href="../index.html">UNITARY 主站</a> &nbsp;·&nbsp;
    <a href="https://instagram.com/unitary.hk">Instagram</a> &nbsp;·&nbsp;
    <a href="../sitemap.xml">Sitemap</a> &nbsp;·&nbsp;
    CC BY-NC-SA 4.0</p>
</div>

</body>
</html>
'''


# === 4. Main build ===
def main():
    games = load_games()
    print(f"Loaded {len(games)} games from games.json")

    # Generate 8 個 game page
    for g in games:
        gid = g['id']
        content_path = ROOT / 'content' / f'{gid}.md'
        if not content_path.exists():
            print(f"  ⚠️  {gid}.md 唔存在, 跳過")
            continue
        with open(content_path) as f:
            content_md = f.read()
        html = render_game_page(g, content_md)
        out_path = ROOT / f'{gid}.html'
        with open(out_path, 'w') as f:
            f.write(html)
        print(f"  ✓ {gid}.html ({len(html)} chars)")

    # Generate index page
    index_html = render_index_page()
    with open(ROOT / 'index.html', 'w') as f:
        f.write(index_html)
    print(f"  ✓ index.html ({len(index_html)} chars)")

    print(f"\n=== Done! 全部 server-rendered, 無 JS 依賴 ===")

if __name__ == '__main__':
    main()
