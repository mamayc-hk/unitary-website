#!/usr/bin/env python3
"""
Unitary 開枱指南 — Build script v2
對返 NN/G UX heuristic + Rulebook Test 嘅 5 個 fix:
  A. Quick Start 段 (2 分鐘 onboarding)
  B. Inline example box
  C. FAQ 段 (5 條 common pitfalls, Glossary 略)
  D. Sticky Cheat Sheet sidebar
  E. Story + Selling Point hero (information hierarchy)
"""
import json
import re
import os
import subprocess
from pathlib import Path

ROOT = Path('/Users/herry/Documents/Cherry/unitary-website/board-game')

# Image cache-busting hash (當前 git commit short hash, 每次 build 自動更新)
try:
    BUILD_HASH = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, stderr=subprocess.DEVNULL).decode().strip()
except Exception:
    BUILD_HASH = 'v1'

# === 1. Markdown → HTML parser (with example box detection) ===
def escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def md_inline(text):
    text = escape_html(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    # v3.4.0.l: standalone image line 唔再靠 md_inline, 改用 md_to_html 嘅 standalone image 識別
    # (留 placeholder 防止 inline case 出現意外 escape)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<div class="step-img-row"><img src="\2" alt="\1" class="step-inline-img" loading="lazy"></div>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text

def md_to_html(md_text):
    lines = md_text.split('\n')
    out = []
    in_list = None
    in_quote = False
    para_buf = []
    in_faq = False  # FAQ 識別
    in_step_block = False  # v3.4.0.l: H3 step 開 step-block wrapper (2-column layout)

    def flush_para():
        nonlocal para_buf
        if para_buf:
            text = ' '.join(para_buf)
            # Detect example box: 句子以 "例:", "BGG 統計", "例如" 開頭
            if re.match(r'^\s*(例[:：]|BGG 統計|例如)', text):
                out.append(f'<div class="example-box"><p><strong>💡 例子</strong> {md_inline(text)}</p></div>')
            else:
                out.append('<p>' + md_inline(text) + '</p>')
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

        if not stripped:
            flush_para(); flush_list(); flush_quote()
            i += 1; continue

        if stripped == '---':
            flush_para(); flush_list(); flush_quote()
            out.append('<hr>')
            i += 1; continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            flush_para(); flush_list(); flush_quote()
            level = len(m.group(1))
            heading_text = m.group(2)
            # v3.4.0.l: H3 啱啱 match 步驟 pattern 先開 step-block wrapper (避免推介畀咩人, 客 query 對應 etc 都被 wrap)
            is_step = level == 3 and re.match(r'^步驟\s+\d+', heading_text)
            # v3.4.0.m: 任何新 step 開之前, 一定 close 上一個 step-block (避免 step 6 → step 7 連續時, FAQ 跌入 step 6 嘅 grid)
            if in_step_block:
                out.append('</div>')
                in_step_block = False
            if is_step:
                out.append('<div class="step-block">')
                in_step_block = True
            out.append(f'<h{level}>{md_inline(heading_text)}</h{level}>')
            i += 1; continue

        # v3.4.0.l: standalone image line `![alt](src)` 獨立處理
        m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', stripped)
        if m:
            flush_para(); flush_list(); flush_quote()
            alt = escape_html(m.group(1))
            src = escape_html(m.group(2))
            out.append(f'<div class="step-img-row"><img src="{src}" alt="{alt}" class="step-inline-img" loading="lazy"></div>')
            i += 1; continue

        # Blockquote (with Example box detection: > 例: ... 觸發)
        if stripped.startswith('>'):
            flush_para(); flush_list()
            content = stripped.lstrip('>').strip()
            if re.match(r'^\s*例[:：]', content):
                # > 例: ... → wrap 喺 .example-box (跳出 blockquote 累積)
                if in_quote:
                    out.append('</blockquote>')
                    in_quote = False
                out.append(f'<div class="example-box"><p><strong>💡 例子</strong> {md_inline(content)}</p></div>')
            else:
                if not in_quote:
                    out.append('<blockquote>')
                    in_quote = True
                out.append('<p>' + md_inline(content) + '</p>')
            i += 1; continue
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
            item = m.group(1)
            # Example box check
            if re.match(r'^\s*(例[:：]|BGG 統計|例如)', item):
                out.append(f'<li><div class="example-box"><p><strong>💡 例子</strong> {md_inline(item)}</p></div></li>')
            else:
                out.append('<li>' + md_inline(item) + '</li>')
            i += 1; continue

        # Ordered list
        m = re.match(r'^\d+\.\s+(.*)', stripped)
        if m:
            flush_para()
            if in_list != 'ol':
                flush_list()
                out.append('<ol>')
                in_list = 'ol'
            item = m.group(1)
            if re.match(r'^\s*(例[:：]|BGG 統計|例如)', item):
                out.append(f'<li><div class="example-box"><p><strong>💡 例子</strong> {md_inline(item)}</p></div></li>')
            else:
                out.append('<li>' + md_inline(item) + '</li>')
            i += 1; continue

        para_buf.append(stripped)
        i += 1

    flush_para(); flush_list(); flush_quote()
    if in_step_block:
        out.append('</div>')
        in_step_block = False
    return '\n'.join(out)


# === 2. Quick Start 段 (Fix A) ===
# 對應 Rulebook Test: 2 分鐘 onboard. 6 條 30 秒 rule per game
QUICK_START = {
    'bohnanza': [
        '**手牌順序鎖死** — 你抽到嘅牌唔可以重排, 第一張一定要先種',
        '**每回合 4 步**: 種豆 → 交易 → 種交易牌 → 補 3 張牌',
        '**一塊田一種豆**, 田滿 3 張要先收割 (賣晒換金幣)',
        '**越多豆同一時間賣越值錢** — 紅豆 1 張 2 金, 4 張 9 金',
        '**3 疊牌玩完 = 遊戲結束**, 金幣最多贏',
        '💡 <strong>善用交易</strong>: 牌序鎖死, 唔 trade 就塞死自己',
    ],
    'camel-up': [
        '**5 隻駱駝 + 2 隻瘋狂駱駝**, 後者會騎上去 (疊羅漢)',
        '**4 個動作**: A 擲骰 / B 放觀眾圖板 / C 買彩票 / D 落注',
        '**一局 5 個骰完結** (5 隻駱駝每隻擲 1 次)',
        '**過終點即結算**: 終點冠軍 + 包尾同時計',
        '**「疊羅漢」係核心**: 後面嘅駱駝揹住前面, 一起行',
        '💡 <strong>Mirage 拖慢領先者</strong>比 Oasis 推落後者更有策略性',
    ],
    'take-time': [
        '**每人有月 (白) + 日 (黑) 各 1-12 牌**',
        '**時鐘圖版有 6 個區段**, 每人輪流放 1 張',
        '**3 階段**: 討論 (可講) → 出牌 (沉默) → 結算',
        '**每個區段嘅數值 = 該區段所有牌嘅總和**',
        '**開牌額度** (提示標記) 可以公開出牌',
        '💡 <strong>過 24 即失敗</strong> — 由細數字開始, 唔好講具體數字',
    ],
    'catan': [
        '**3-4 人, 19 塊 hex 版圖**, 6 種地形',
        '**每回合**: 擲骰產資源 → 交易 (4:1) → 建築 → 盜賊 (擲 7)',
        '**5 個建築選項**: 道路 / 村莊 / 城市 / 發展卡 / 港口',
        '**10 分贏**: 村莊 1 + 城市 2 + 最長道路 2 + 最大軍隊 2 + 發展卡分',
        '**盜賊擺位 = 戰略** (擺對手最需要嘅地形)',
        '💡 <strong>6 + 8 數字組合勝率高 30%</strong> — 開局優先搵呢啲 hex',
    ],
    'project-l': [
        '**1-4 人, polyomino 拼圖策略** (俄羅斯方塊桌上版)',
        '**2 個階段**: A 拿碎片 → B 拼圖完成 puzzle card',
        '**升級動作**: 用 master piece 升級, 攞更多容量',
        '**計分**: 完成 puzzle card 得分 + bonus + master piece bonus',
        '**單人模式**都有, 1-4 人彈性最大',
        '💡 <strong>1 級 puzzle piece 優先完成</strong> — 開局戰略重點',
    ],
    'dnup': [
        '**2-5 人, 快速脫手卡牌**',
        '**每張牌上下端數字不同** (e.g. 1 / 7), 可「旋轉」整把手牌',
        '**目標**: 最先清空手牌',
        '**得分**: 最快清空 2 分, 第 2 個 1 分, 累積 4 分贏',
        '**人數變體**: 5 人用全部 / 4 人移走 5 / 3 人移走 4+5 / 2 人移走 3+4+5',
        '💡 <strong>Revolve 時機</strong>: 當手牌有大量「上端低 / 下端高」時翻轉最化算',
    ],
    'manila': [
        '**3-5 人, 港灣貿易策略**',
        '**每回合 3 階段**: 競投船長 → 工人放置 → 航海結果',
        '**6 個職位**: 船長 / 引水人 / 商人 / 走私者 / 保險 / 海盜',
        '**合法入貨 vs 走私**: 合法有稅, 走私 0 稅但金額低',
        '**結束條件**: 任何股票升到 30 元',
        '💡 <strong>3 人場高手策略</strong>: 每個玩家 4 個工人, 可同時佔 2 個職位, 風險高回報',
    ],
}


# === 3. Selling Point 段 (Fix E Hero) ===
# 對應 information hierarchy 嘅 back story
SELLING_POINTS = {
    'bohnanza': {
        'story': '你係一個豆田農夫, 呢個春天你抽到嘅豆決定你成個季節嘅命運。眾豆得金嘅設計天才在於: 「手牌順序不能改變」— 呢個限制迫你同其他農夫不停 trade, 笑料同策略都喺傾計度誕生。',
        'point_emoji': '🤝',
        'point_text': '5-7 人坐枱 trade 笑到反枱, 1 局 60 分鐘過咗好似 15 分鐘',
    },
    'camel-up': {
        'story': '埃及沙漠, 5 隻駱駝賽跑, 你落注邊隻贏。但有 2 隻瘋狂駱駝會騎上去 — 疊羅漢嘅瞬間, 頭馬可以一秒變包尾。駱駝大賽嘅魔力在於: 規則簡單到 5 分鐘教完, 但心理戰可以玩到天光。',
        'point_emoji': '🎲',
        'point_text': '8 人派對王, 規則最淺但落注心理戰深',
    },
    'take-time': {
        'story': '你哋一齊解謎, 但討論完之後出牌嘅時候唔可以講嘢。要靠默契去估計隊友手上有咩牌, 會放喺邊個位置。贏嘅時候大家一齊嗌, 輸嘅時候大家都好想話「我明明擺咗呢個數字㗎嘛!」。',
        'point_emoji': '🤫',
        'point_text': '合作默契桌遊, 情侶 / 家庭 / 朋友首選',
    },
    'catan': {
        'story': '你哋去咗一個新島, 要喺度建立道路、村莊、城市, 搶資源, 同對手 trade。卡坦島係 1995 年嘅經典德式策略, 30 年後依然係新手入門策略桌遊嘅首選 — 因為規則清晰, 戰略深, 中文書好搵。',
        'point_emoji': '🏝️',
        'point_text': '經典德式策略始祖, 中文版普及',
    },
    'project-l': {
        'story': '俄羅斯方塊嘅桌上版, 你收集 polyomino 碎片, 喺拼圖卡上拼出指定形狀。每完成一張拼圖卡, 你攞分 + 獎勵, 仲可以升級大師塊攞更多容量。1-4 人彈性, 單人都好玩。',
        'point_emoji': '🧩',
        'point_text': '俄羅斯方塊桌上版, 1-4 人彈性, 單人都啱玩',
    },
    'dnup': {
        'story': '你同 2-4 個對手鬥快清空手牌, 但你嘅牌上下端數字唔同, 你可以「Revolve」翻轉整把手牌 — 選擇權喺你, 但要計準時機。DNUP 嘅設計簡潔: 15 分鐘教晒, 30 分鐘完一局, 旺角朋友群嘅派對王。',
        'point_emoji': '🔄',
        'point_text': '15 分鐘教晒, 30 分鐘完一局, 派對快速桌遊',
    },
    'manila': {
        'story': '19 世紀馬尼拉港, 你係投資者, 要競投船長、買股票、合法入貨定走私, 務求喺港口經濟戰入面賺最多。馬尼拉嘅戰略深度高, 6 個職位 × 3 種股票 × 港灣選擇, 專家可以玩到天光。',
        'point_emoji': '⚓',
        'point_text': '港口經濟戰, 進階專家向, 戰略深度高',
    },
}


# === 4. Cheat Sheet 段 (Fix D, sidebar sticky) ===
# 5 條 critical tactical tips, 對應新手 review 場景
CHEAT_SHEET = {
    'bohnanza': [
        '🌾 <strong>牌序鎖死</strong>: 第一張一定要先種',
        '💰 <strong>第 3 塊田</strong>係 trade currency, 唔一定買',
        '🎯 <strong>5+ 人場</strong>只可以同左右 trade, 唔可以飛 trade',
        '📊 <strong>3 → 4 張</strong>邊際收益跳一級, 唔好急收割',
        '⏰ <strong>Say no to bad trade</strong> = 塞死自己',
    ],
    'camel-up': [
        '🏇 <strong>疊羅漢</strong>跟主駝, 揀「托」唔係「冠軍」',
        '📈 <strong>冷門駱駝</strong>賠率高, 集中買落後嗰隻',
        '🌵 <strong>Mirage 拖慢</strong>領先者, 戰略值 2 倍 Oasis',
        '🎯 <strong>落後者擲骰</strong>係壞選擇, 揀領先者擲',
        '🪑 <strong>8 人場坐第 1 位</strong> 落注最靈活',
    ],
    'take-time': [
        '🤐 <strong>沉默出牌</strong>, 用抽象語言溝通',
        '🎴 <strong>開牌額度</strong>要善用, 唔好慳住',
        '📐 <strong>由細數字開始</strong>, 大數字留後',
        '🔍 <strong>留意特殊規則</strong>, 唔好忽略每關細節',
        '🧠 <strong>默契</strong>係核心, 唔好假設隊友會明',
    ],
    'catan': [
        '🎲 <strong>6 + 8 數字組合</strong>勝率高 30%',
        '🏴 <strong>盜賊擺對手需要</strong>嘅地形, 唔係擺自己弱嘅',
        '💱 <strong>港口 3:1 / 2:1</strong>比 4:1 抵好多, 早建港口',
        '🏰 <strong>第 2 個城市</strong>勝過第 3 個村莊',
        '🎖️ <strong>發展卡</strong>有 1/6 機會係騎士, 早集 3 張',
    ],
    'project-l': [
        '🧩 <strong>1 級 puzzle piece 優先</strong> — 開局戰略重點',
        '⬆️ <strong>升級 vs take 順序</strong>: 先升級遲啲 take 多容量',
        '⭐ <strong>Master piece</strong> 早做, 攞最大分',
        '🎯 <strong>Bonus piece</strong> 對齊 puzzle card 形狀',
        '🛠️ <strong>棋盤管理</strong>: 留空位俺後續 take',
    ],
    'dnup': [
        '🔄 <strong>Revolve 時機</strong>: 上端低 / 下端高時翻轉',
        '🃏 <strong>連續數字長鏈</strong>可以一次清空',
        '⚡ <strong>2 人場</strong>用人牌, 玩兩個連續回合',
        '🎯 <strong>5 人場</strong>用全部牌, 競爭最激烈',
        '🚫 <strong>唔好儲牌</strong>, 唔出就等於塞自己',
    ],
    'manila': [
        '💰 <strong>Bid 1-2 元</strong>勝率比 3 元高 15%',
        '🏴‍☠️ <strong>海盜 vs 商人</strong>根據失事率選職位',
        '📊 <strong>合法 vs 走私</strong>: 計淨利潤, 唔好睇表面',
        '🛡️ <strong>保險</strong>被動收入, 失事率高時擺',
        '📈 <strong>股票</strong>低買高賣, 揀快升嘅港灣',
    ],
}


# === 5. FAQ 段 (Fix C) ===
# 5 條 common pitfalls per game
FAQ = {
    'bohnanza': [
        ('新手最易犯乜錯?', '新手會「唔肯 trade」, 結果塞死自己。眾豆得金嘅設計就係迫你 trade, 接受差 trade 比起完全 reject 好。'),
        ('手牌順序可唔可以重排?', '唔可以。呢個係眾豆得金嘅核心, 重排會 break 成個 game。'),
        ('第 3 塊田幾時買?', '新手建議保留 5 金幣做 trade currency, 唔好為咗 3 塊田蝕底。高手會喺 round 3 之後先買。'),
        ('幾多人最好玩?', '5-7 人最佳, 2 人太靜, 3-4 人 OK 但少咗 trade 機會。'),
        ('幾耐可以教完新手?', '15 分鐘教晒, 但新手要玩 2-3 局先掌握牌序鎖死嘅痛苦。第一次玩要示範 1 局俾新手睇。'),
    ],
    'camel-up': [
        ('新手最易犯乜錯?', '揀「冠軍」嘅駱駝落注, 忽略「疊羅漢」效應。高手會揀「托」嘅駱駝, 即揹住最多同黨嗰隻。'),
        ('Mirage 同 Oasis 邊個好?', 'Mirage 戰略值 2 倍 Oasis, 因為 Mirage 拖慢領先者而 Oasis 推落後者 (推唔郁)。'),
        ('8 人場坐邊個位最好?', '坐第 1 位擲骰, 之後 7 個人可以根據新形勢落注, 最靈活。坐最後 1 位最蝕底但可以揀最冷門注。'),
        ('觀眾圖板幾時放?', '永遠先擺 Mirage 喺領先嗰隻嘅下一格, 拖慢佢。Oasis 擺喺落後嗰隻嘅下一格, 幫佢追。'),
        ('1.0 同 2.0 邊個較好?', '2.0 和局處理較複雜但有 Mirage/Oasis 變化, 旺角 8 成以上都係 2.0, 如果你想確認。'),
    ],
    'take-time': [
        ('可以出牌時講嘢嗎?', '唔可以, 呢個係 Take Time 嘅核心。出牌階段要沉默, 靠默契同抽象語言溝通。'),
        ('開牌額度點用?', '每關有指定數量, 建議喺最關鍵 1-2 個區段用, 唔好慳住。'),
        ('點解我哋成日超過 24?', '因為大數字冇分配好。建議由細數字開始, 將大數字放最後一段, 留 buffer 俾中間段。'),
        ('2 人可以玩嗎?', '可以但體驗弱, 合作默契感覺唔到。建議 3-4 人。'),
        ('合作輸咗會挫敗嗎?', '唔會, 因為可以 skip 關卡, 唔似其他合作桌遊一定要贏。'),
    ],
    'catan': [
        ('3 人場可以玩嗎?', '可以但要標記 1 個位做「鬼位」, 因為卡坦島 3-4 人, 3 人需要調整。'),
        ('擲 7 點即死?', '唔係死, 係觸發盜賊, 要減半手牌, 然後擺盜賊到一個新地形 (搶 1 個玩家 1 張牌)。'),
        ('幾時應該 trade?', '永遠 trade! 4:1 同銀行換蝕底, 一定要同其他玩家 trade, 港口 3:1 換就更好。'),
        ('發展卡好定城市好?', '城市好, 因為 2 分 + 雙倍資源。第 2 個城市比第 3 個村莊重要。'),
        ('新手最大錯誤?', '忽略盜賊擺位戰略, 亂擺盜賊。應該擺對手最需要嘅地形 (6 / 8 號碼)。'),
    ],
    'project-l': [
        ('1 人可以玩嗎?', '可以, 單人模式有, 對應自己砌 puzzle。'),
        ('Master piece 重要嗎?', '好重要, 早做可以攞最多分。Master piece 升級後可以攞更多容量。'),
        ('升級 vs 拿碎片 邊個先?', '高手會先升級 (master piece), 遲啲先拿碎片, 因為升級後容量大, 拼圖更靈活。'),
        ('怎樣快速贏?', '集中 1 級 puzzle piece, 唔好貪心做高難度 (2-3 級), 攞穩定分。'),
        ('2-3 人好玩嗎?', '2 人 OK 但少咗競爭, 3 人平衡, 4 人最刺激。'),
    ],
    'dnup': [
        ('Revolve 點樣用?', 'Revolve 翻轉整把手牌嘅上下數值, 當手牌有大量「上端低 / 下端高」時翻轉最化算。'),
        ('點解要清空手牌?', '最快清空 2 分, 第 2 個 1 分, 累積 4 分贏。'),
        ('2 人場有咩唔同?', '2 人場移走 3+4+5 符號, 使用人牌, 玩兩個連續回合, 戰術變化大。'),
        ('新手最易犯乜錯?', '儲牌唔出, 結果塞到自己。要積極出牌, 即使係差嘅組合。'),
        ('幾耐一局?', '15-20 分鐘, 5 人場最長, 2 人場最短。'),
    ],
    'manila': [
        ('Bid 3 元係咪必贏?', '唔係, 反而蝕底機會大。高手 bid 1-2 元, 因為船長利潤要靠操控 bonus + 職位分錢補返。'),
        ('走私 vs 合法 邊個好?', '睇淨利潤, 合法要扣稅但金額高, 走私 0 稅但金額低。新手要示範計算。'),
        ('3 人場有咩唔同?', '3 人場每個玩家 4 個工人, 可同時佔 2 個職位 (高風險高回報), 4-5 人場只可佔 1 個職位。'),
        ('股票幾時賣?', '股票只有「上」冇「下」, 揀快升嗰隻 (你嘅船都去嘅港灣) 買, 高位賣。'),
        ('新手最大錯誤?', '忽略保險職位。保險係被動收入, 5 人場每次失事賠 5 元, 5 個回合已經回本。'),
    ],
    'seti': [
        ('新手最易犯乜錯?', '新手會忽略 Mothership 板嘅長線規劃, 一回合衝太多行動。高手會分 5 個回合逐步升級技術、收集樣本。'),
        ('探測 vs 訊號 邊個先?', '訊號 (短線高分) 先, 探測 (中線穩定) 配合。訊號卡可以即時 1-3 分, 探測要 3-4 個回合先見效。'),
        ('4 人場好玩嗎?', '4 人場最佳, 12 個行星競爭激烈但 5 個回合夠分。3 人場太空太多, 1-2 人場冷清。'),
        ('幾耐一局?', '官方 90-120 min, 但新手第一次要 150 min。預 2-3 小時, 中場 break 一次。'),
        ('可以單人玩嗎?', '可以, 官方 Automa (自動對手) 支援 1 人場, 90 min 玩完, 適合 1 個人練習。'),
    ],
    'spots': [
        ('新手最易犯乜錯?', '新手會太進取擲多隻骰 (Fetch 3 隻), 結果爆 (bust)。高手會由 Walk / Beg 開始, 慢慢搵節奏。'),
        ('幾時應該收狗 (Slow and Steady)?', '當你填滿 1 隻以上狗卡, 嗰個 turn 結束前可以選擇收狗。新手建議「填滿就收」, 避免塞死自己。'),
        ('Treat 留到幾時用?', '救命時用: 擲完發現 3 隻都唔啱 → 用 treat 全重擲。留 1-2 個 treat 喺袋, 唔好亂花。'),
        ('Trick Tile 點解只剩 1 個會自動翻轉?', '防止玩家「鎖死」某個 trick, 確保大家有選擇。同時放 1 個 treat 喺「最後嗰個 trick」上面, 鼓勵人揀冷門 trick。'),
        ('可以 1 個人玩嗎?', '可以, 規則完全一樣。可以挑戰「30 分鐘內完成 3 隻狗」或「10 輪內完成 5 隻狗」等目標, 練 push-your-luck 嘅 risk management。'),
    ],
}


def load_games():
    with open(ROOT / 'games.json') as f:
        return json.load(f)['games']


# === 6. Page template (v2: 含 5 個 fix) ===
def render_game_page(game, content_md):
    name = game['name']
    name_en = game['name_en']
    tagline = game.get('tagline', '')
    summary = game.get('summary', '')
    publisher = game.get('publisher', '')
    designer = game.get('designer', '')
    cats = game.get('category', [])
    min_p = game['min_players']
    max_p = game['max_players']
    best_players = game.get('best_players', f"{min_p}-{max_p}")
    teach = game.get('teach_time', 0)
    play = game.get('play_time', '')
    diff = game.get('difficulty_label', '')
    langs = game.get('language_versions', [])
    bgg = game.get('bgg_url', '')
    box = game.get('box_image', '')
    hero = game.get('hero_image', '') or box  # hero_image 優先 (純文字 logo), fallback to box_image
    step_imgs = game.get('step_images', [])
    tactics_n = game.get('tactical_notes_count', 0)
    has_tb = game.get('has_tiebreaker', False)
    is_complete = game.get('is_complete', True)
    fit = game.get('customer_fit', {})
    gid = game['id']

    # Markdown → HTML
    # Strip leading H1 (template H1 is authoritative, 避免 page 出現兩個 H1)
    content_md_no_h1 = re.sub(r'^#\s+.*\n', '', content_md, count=1)
    long_form_html = md_to_html(content_md_no_h1)

    # Customer fit
    fit_items = ''.join(f'<li><strong>{escape_html(k)}</strong>: {escape_html(v)}</li>\n' for k, v in fit.items())

    # v3.4.0.l: 改用 box_image (真實桌遊盒面), 唔用 hero_image (純文字 logo)
    box_html = ''
    if box:
        box_filename = box.split('/')[-1]
        box_html = f'<figure><img src="images/{box_filename}?v={BUILD_HASH}" alt="{escape_html(name)} 盒面" loading="lazy"></figure>'

    # Step infographic (1 張橫向 2:1 infographic, 合併自 step_imgs)
    step_html = ''
    infographic_path = ROOT / 'images' / f'infographic-{gid}.jpg'
    if infographic_path.exists():
        step_html = f'<div class="step-infographic"><img src="images/infographic-{gid}.jpg" alt="{escape_html(name)} 玩法步驟" loading="lazy"></div>'

    # Selling point (Fix E)
    sp = SELLING_POINTS.get(gid, {'story': summary, 'point_emoji': '🎲', 'point_text': tagline})

    # Quick Start (Fix A)
    qs_items = QUICK_START.get(gid, [])
    qs_html = ''
    if qs_items:
        # Quick Start items 用 `**bold**` markdown, 喺呢度 convert 做 <strong>
        bold_re = re.compile(r'\*\*(.+?)\*\*')
        bold_sub = r'<strong>\1</strong>'
        qs_items_html = '\n'.join(
            '<li>' + bold_re.sub(bold_sub, item) + '</li>'
            for item in qs_items
        )
        qs_html = f'''
        <div class="quick-start">
            <p><strong>⚡ 快速上手 — 2 分鐘上手:</strong> 新手 2 分鐘內上手, 記住呢 6 條:</p>
            <ol>{qs_items_html}</ol>
        </div>
        '''

    # FAQ (Fix C)
    faq_items = FAQ.get(gid, [])
    faq_html = ''
    if faq_items:
        faq_items_html = '\n'.join(
            f'<div class="faq-item"><h4>{escape_html(q)}</h4><p>{escape_html(a)}</p></div>'
            for q, a in faq_items
        )
        faq_html = f'''
        <div class="faq">
            <h2>❓ 常見問題</h2>
            {faq_items_html}
        </div>
        '''

    # Quick Start (sidebar 取代速查表位置)
    qs_items_sidebar = QUICK_START.get(gid, [])
    qs_sidebar_html = ''
    if qs_items_sidebar:
        qs_items_html = '\n'.join(
            '<li>' + bold_re.sub(bold_sub, item) + '</li>'
            for item in qs_items_sidebar
        )
        qs_sidebar_html = f'''
        <div class="cheat-sheet">
            <h3>⚡ 快速上手</h3>
            <ol>{qs_items_html}</ol>
        </div>
        '''

    # Sidebar 相關 game (from games.json related_games)
    all_games = sorted(load_games(), key=lambda g: (0 if g.get('is_kickoff') else 1, g['id']))
    all_games_dict = {g['id']: g for g in all_games}
    related_ids = game.get('related_games', [])
    related_sidebar_html = ''
    if related_ids:
        related_links = []
        for rid in related_ids:
            rg = all_games_dict.get(rid)
            if not rg:
                continue
            box_filename = rg.get('box_image', '').split('/')[-1] if rg.get('box_image') else ''
            box_thumb = f'<img src="images/{box_filename}?v={BUILD_HASH}" alt="">' if box_filename else ''
            related_links.append(
                f'<a href="{rg["id"]}.html" class="related-game-link">'
                f'<span class="related-game-thumb">{box_thumb}</span>'
                f'<span class="related-game-name">{escape_html(rg["name"])}</span>'
                f'</a>'
            )
        related_sidebar_html = f'''
        <div class="side-box">
            <h3>相關 game</h3>
            <div class="related-games">
                {''.join(related_links)}
            </div>
        </div>
        '''

    complete_badge = '✅ 完整教學' if is_complete else '⚠️ 內容待補'

    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(name)} ({escape_html(name_en)}) — {escape_html(tagline)} | UNITARY 開枱指南</title>
    <meta name="description" content="{escape_html(summary)}">
    <meta name="keywords" content="桌遊,教學,桌遊教學,{escape_html(name)},{escape_html(name_en)},board game,{escape_html(",".join(cats))},香港桌遊,新手桌遊,新手">
    <link rel="canonical" href="https://unitaryhk.com/board-game/{gid}.html">
    <meta property="og:title" content="{escape_html(name)} ({escape_html(name_en)}) — {escape_html(tagline)}">
    <meta property="og:description" content="{escape_html(summary)}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="stylesheet" href="../blog.css">
    <style>
    /* v3.4.0.j inline override: server blog.css stale (GitHub Pages cache bug 揀 file 唔全),
       強制 side-box 縮減生效 (per user comment 2+3: 上邊空間太多) */
    .side-box {{ padding: 6px 16px !important; margin-bottom: 12px !important; }}
    .side-box h3 {{ margin: 0 0 4px 0 !important; }}
    </style>
</head>
<body>

<div class="nav"><div class="nav-inner">
    <a href="../index.html"><img src="../logo.png" alt="UNITARY"></a>
</div></div>

<div class="layout">
    <div class="main">
        <div class="main-content">
            <!-- v3.4.0.l: 刪走「← 返回桌遊列表」back link (per user comment 2) -->

            <!-- Hero 段 (Fix E: Story + Selling Point) -->
            <div class="game-hero">
                <div class="game-hero-text">
                    <div class="game-hero-meta">
                        <span class="complete-badge">{complete_badge}</span>
                        <span class="game-hero-tagline">{escape_html(tagline)}</span>
                    </div>
                    <h1>{escape_html(name)} ({escape_html(name_en)})</h1>
                    <div class="game-hero-publisher">出版: {escape_html(publisher)}{('<br>設計者: ' + escape_html(designer)) if designer else ''}<br>類別: {escape_html(", ".join(cats))}</div>
                </div>
                <div class="game-hero-img">
                    {box_html}
                </div>
            </div>

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
                    <div class="value">{escape_html(play)}</div>
                </div>
                <div class="game-meta-item">
                    <div class="label">難度</div>
                    <div class="value">{escape_html(diff)}</div>
                </div>
                <div class="game-meta-item">
                    <div class="label">最佳人數</div>
                    <div class="value">{escape_html(best_players)} 人</div>
                </div>
            </div>

            <!-- Story + Selling Point (Fix E) -->
            <div class="story-section">
                <div class="story-emoji">{sp['point_emoji']}</div>
                <div class="story-content">
                    <p class="story-text">{sp['story']}</p>
                    <p class="selling-point"><strong>為咩好玩:</strong> {sp['point_emoji']} {sp['point_text']}</p>
                </div>
            </div>

            <!-- Quick Start (Fix A: 2 分鐘 onboard) — inline intro 已移除, 只留 sidebar sticky 板 -->
            <!-- (Inline callout 刪走, 詳見 v3.4.0.i) -->


            <!-- v3.4.0.k: 集中 step-images-inline infographic 刪走, summary-callout 刪走
                 (per user comment 5 + 6) -->

            <!-- Long-form markdown content (含 inline example box) -->
            <div class="long-form">
                {long_form_html}
            </div>

            <!-- FAQ (Fix C) -->
            {faq_html}

            <hr>

            <h2>🛍️ 配件同擴充</h2>
            <div class="cross-sell">
                <p>新手可以一併推薦:</p>
                <ul>
                    <li><strong>DOSHA 木盒</strong>: <a href="https://instagram.com/dosha.woodcraft" target="_blank" rel="noopener">@dosha.woodcraft</a> 嘅木製收納盒, 配 {escape_html(name)} 嘅卡牌完美 fit。</li>
                    <li><strong>新手桌遊 (香港)</strong>: 香港實體店, 新手可以即場試玩。</li>
                    {f'<li><strong>BoardGameGeek 完整資料</strong>: <a href="{escape_html(bgg)}" target="_blank" rel="noopener">{escape_html(name_en)} 喺 BGG</a> (社群評分、規則 Q&A、變體討論)</li>' if bgg else ''}
                </ul>
            </div>

            <hr>

            <h2>💬 留言</h2>
            <div class="comments">
                <p>有問題、想分享戰術、或者搵遊戲partner？DM 我哋 Instagram:</p>
                <p style="margin-top:12px">
                    <a href="https://instagram.com/unitary.hk" target="_blank" rel="noopener" class="btn-cta btn-secondary">📷 Instagram DM →</a>
                </p>
                <p style="margin-top:16px;font-size:0.9rem;color:#666">之後會加 Giscus 留言系統 (GitHub Discussions-based, 實時 + email 通知)</p>
            </div>

            <p style="margin-top:40px"><a href="index.html" class="back">← 返回桌遊列表</a></p>
        </div>
    </div>

    <div class="side">
        <div class="side-box">
            <h3>📌 關於 UNITARY</h3>
            <div class="about-text">
                <p>UNITARY 係為香港同台灣桌遊新手同愛好者而設嘅教學網誌, Herry Ma 個人計劃。內容 base on 官方規則書 + BGG 數據 + 自己試玩經驗。</p>
                <p>
                    <a href="https://instagram.com/unitary.hk" target="_blank">Instagram →</a>
                    &nbsp;·&nbsp;
                </p>
            </div>
        </div>
        {related_sidebar_html}
        <!-- Sticky Cheat Sheet (Fix D) -->
        {qs_sidebar_html}
        <!-- v3.4.0.i: 新手指南 sidebar block 刪走 (per user comment 4) -->
    </div>
</div>

<div class="blog-footer">
    <p>© 2026 UNITARY 開枱指南 &nbsp;·&nbsp;
    <a href="../board-game/">← 開枱指南</a> &nbsp;·&nbsp;
    <a href="https://instagram.com/unitary.hk">Instagram</a> &nbsp;·&nbsp;
    <a href="../sitemap.xml">Sitemap</a> &nbsp;·&nbsp;
    CC BY-NC-SA 4.0</p>
</div>

</body>
</html>
'''


# === 7. Index page (board-game/index.html) ===
def render_index_page():
    games = load_games()
    sorted_games = sorted(games, key=lambda g: (
        0 if g.get('is_kickoff') else 1,
        0 if g.get('is_complete', True) else 1,
        g['id']
    ))

    cards = []
    for g in sorted_games:
        box_filename = g.get('box_image', '').split('/')[-1] if g.get('box_image') else ''
        box_html = f'<img src="images/{box_filename}?v={BUILD_HASH}" alt="{escape_html(g["name"])} 盒面" loading="lazy">' if box_filename else '🎲'
        pending = '' if g.get('is_complete', True) else ' <span style="color:var(--color-warn)">⚠️ 待補</span>'

        # Derive filter data attributes for CSS filter system
        # Players: 2-4 / 5+ / 6+
        players = []
        if g.get('min_players', 0) <= 4 and g.get('max_players', 0) >= 2:
            players.append('2-4')
        if g.get('max_players', 0) >= 5:
            players.append('5+')
        if g.get('max_players', 0) >= 6:
            players.append('6+')
        data_players = ' '.join(players)

        # Time: 30 / 31-60 / 60+ (parse first number from play_time)
        time_str = g.get('play_time', '60 min')
        time_match = re.search(r'(\d+)', time_str)
        time_max = int(time_match.group(1)) if time_match else 60
        if time_max <= 30:
            data_time = '30'
        elif time_max <= 60:
            data_time = '31-60'
        else:
            data_time = '60+'

        # Difficulty: easy / mid / hard
        diff = g.get('difficulty_label', '中等')
        if '簡單' in diff and '進階' in diff:
            data_diff = 'easy'  # 簡單至中等
        elif '簡單' in diff:
            data_diff = 'easy'
        elif '進階' in diff:
            data_diff = 'hard'  # 中等至進階 or 進階
        else:
            data_diff = 'mid'

        # Type: coop / party / vs (derive from category)
        category = g.get('category', [])
        if '合作' in category:
            data_type = 'coop'
        elif '派對' in category:
            data_type = 'party'
        else:
            data_type = 'vs'

        # Chinese: 繁中 / 簡中 / eng
        langs = g.get('language_versions', [])
        cn = []
        if '繁中' in langs: cn.append('繁中')
        if '簡中' in langs: cn.append('簡中')
        if not cn and any(x in langs for x in ('ENG', 'EN', 'DE', 'FR')):
            cn.append('eng')
        data_cn = ' '.join(cn) if cn else 'eng'

        cards.append(f'''        <a class="game-card" href="{g['id']}.html" data-players="{data_players}" data-time="{data_time}" data-diff="{data_diff}" data-type="{data_type}" data-cn="{data_cn}">
            <div class="game-card-box">{box_html}</div>
            <div class="game-card-body">
                <h3 class="game-card-name-zh">{escape_html(g['name'])}</h3>
                <p class="game-card-name-en">{escape_html(g['name_en'])}</p>
                <p class="game-card-tagline">{escape_html(g.get('tagline', ''))}</p>
                <div class="game-card-meta">
                    <span>👥 {g['min_players']}-{g['max_players']}人</span>
                    <span>⏱️ {escape_html(g['play_time'])}</span>
                    <span>📚 {escape_html(g['difficulty_label'])}</span>{pending}
                </div>
            </div>
        </a>''')

    cards_html = '\n'.join(cards)

    # === Sidebar: 5 個 quick query (blog-style, 每個都係 blog 文章 link) ===
    QUICK_QUERY = [
        {
            'id': 'q5', 'icon': '👥', 'title': '5 個人玩咩桌遊',
            'slug': '5-person-games',
            'games': ['camel-up', 'bohnanza', 'catan', 'manila', 'seti'],
        },
        {
            'id': 'q30', 'icon': '⏱️', 'title': '30 min 內完一局',
            'slug': '30-min-games',
            'games': ['camel-up', 'dnup'],
        },
        {
            'id': 'qnew', 'icon': '🆕', 'title': '新手第一次玩',
            'slug': 'newbie-games',
            'games': ['camel-up', 'dnup', 'take-time'],
        },
        {
            'id': 'qcoop', 'icon': '🤝', 'title': '合作桌遊',
            'slug': 'coop-games',
            'games': ['take-time'],
        },
        {
            'id': 'qcn', 'icon': '🇭🇰', 'title': '中文版',
            'slug': 'chinese-edition',
            'games': ['bohnanza', 'catan', 'take-time', 'project-l'],
        },
    ]

    # Build game lookup
    games_by_id = {g['id']: g for g in games}

    # Build sidebar quick-query HTML: 每個 query 都係 blog article link
    query_items = []
    for q in QUICK_QUERY:
        game_count = len(q['games'])
        query_items.append(f'''        <a class="query-item" href="{q['slug']}.html">
            <span class="query-icon">{q['icon']}</span>
            <span class="query-title">{escape_html(q['title'])}</span>
            <span class="query-count">{game_count} 個桌遊</span>
        </a>''')
    query_html = '\n'.join(query_items)

    # Build sidebar audience HTML (REMOVED in v3.0.6: user dropped 對應唔同角色 section)
    audience_html = ''

    # === Filter system HTML (核心功效, sticky top) ===
    # 2x2 grid; 人數/時間 為 radio (single-select), 難度/類型 為 checkbox (multi-select)
    filter_html = '''        <div class="filter-bar">
            <div class="filter-group">
                <span class="filter-group-label">👥 人數</span>
                <input type="radio" name="f-players" id="f-players-2-4" class="filter-input">
                <label for="f-players-2-4" class="filter-chip">2-4 人</label>
                <input type="radio" name="f-players" id="f-players-5+" class="filter-input">
                <label for="f-players-5+" class="filter-chip">5+ 人</label>
                <input type="radio" name="f-players" id="f-players-6+" class="filter-input">
                <label for="f-players-6+" class="filter-chip">6+ 人</label>
            </div>
            <div class="filter-group">
                <span class="filter-group-label">⏱️ 時間</span>
                <input type="radio" name="f-time" id="f-time-30" class="filter-input">
                <label for="f-time-30" class="filter-chip">≤30 min</label>
                <input type="radio" name="f-time" id="f-time-31-60" class="filter-input">
                <label for="f-time-31-60" class="filter-chip">31-60 min</label>
                <input type="radio" name="f-time" id="f-time-60+" class="filter-input">
                <label for="f-time-60+" class="filter-chip">60+ min</label>
            </div>
            <div class="filter-group">
                <span class="filter-group-label">🌶️ 難度</span>
                <input type="radio" name="f-diff" id="f-diff-easy" class="filter-input">
                <label for="f-diff-easy" class="filter-chip">簡單</label>
                <input type="radio" name="f-diff" id="f-diff-mid" class="filter-input">
                <label for="f-diff-mid" class="filter-chip">中等</label>
                <input type="radio" name="f-diff" id="f-diff-hard" class="filter-input">
                <label for="f-diff-hard" class="filter-chip">進階</label>
            </div>
            <div class="filter-group">
                <span class="filter-group-label">🎭 類型</span>
                <input type="checkbox" id="f-type-coop" class="filter-input">
                <label for="f-type-coop" class="filter-chip">合作</label>
                <input type="checkbox" id="f-type-party" class="filter-input">
                <label for="f-type-party" class="filter-chip">派對</label>
                <input type="checkbox" id="f-type-vs" class="filter-input">
                <label for="f-type-vs" class="filter-chip">對抗</label>
            </div>
        </div>'''

    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>桌遊教學網誌 — 9 個熱門桌遊完整教學, 規則、戰術、和局處理一站通</title>
    <meta name="description" content="為香港同台灣嘅桌遊新手同愛好者而設嘅教學網誌。9 個熱門桌遊完整教學, 規則、戰術、和局處理、常見問題一站通, 用篩選即時搵啱你人數 / 時間 / 類型 / 難度嘅桌遊。">
    <meta name="keywords" content="桌遊,教學,board game,香港桌遊,台灣桌遊,新手桌遊,繁體中文,眾豆得金,駱駝大賽,掌握時刻,卡坦島,SETI,L計畫,dnup,馬尼拉,UNITARY">
    <link rel="canonical" href="https://unitaryhk.com/board-game/">
    <meta property="og:title" content="桌遊教學網誌 — UNITARY">
    <meta property="og:description" content="為香港同台灣桌遊新手同愛好者而設。9 個熱門桌遊完整教學, 用篩選即時搵啱你嘅桌遊。">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="stylesheet" href="../blog.css">
</head>
<body>

<div class="nav"><div class="nav-inner">
    <a href="../index.html"><img src="../logo.png" alt="UNITARY"></a>
</div></div>

<div class="layout">
    <div class="main">
        <!-- Hero 段 (對象 + 點幫到佢) -->
        <div class="hero">
            <div class="hero-eyebrow">為香港同台灣桌遊新手同愛好者而設</div>
            <h1>桌遊教學網誌</h1>
            <p>想學桌遊但唔知點設置? 想搵啱你人數同時間嘅桌遊? 想知和局點處理? 呢度每個桌遊都有完整規則、戰術、常見問題, 用篩選即時搵啱你嘅桌遊, 學完即玩。</p>
        </div>

        <!-- Filter system (核心功效, sticky top) -->
{filter_html}

        <!-- Game list (純標題, 唔加 annotation) -->
        <h2 id="game-list">合選你的桌遊</h2>
        <p class="game-list-intro">每個桌遊點圖 click 入完整教學。</p>

        <div class="game-grid" id="game-grid">
{cards_html}
        </div>

    </div>

    <div class="side">
        <!-- 關於 UNITARY (置頂) -->
        <div class="side-box">
            <h3>📌 關於 UNITARY</h3>
            <div class="about-text">
                <p>UNITARY 係為香港同台灣桌遊新手同愛好者而設嘅教學網誌, Herry Ma 個人計劃。內容 base on 官方規則書 + BGG 數據 + 自己試玩經驗。</p>
                <p>
                    <a href="https://instagram.com/unitary.hk" target="_blank" rel="noopener">Instagram →</a>
                </p>
            </div>
        </div>

        <!-- 揾桌遊速查 (5 個常見場景, 每個都係 blog 文章 link) -->
        <div class="side-box">
            <h3>📝 揾桌遊速查</h3>
{query_html}
        </div>
    </div>
</div>

<div class="blog-footer">
    <p>© 2026 UNITARY &nbsp;·&nbsp;
    <a href="../board-game/">← 開枱指南</a> &nbsp;·&nbsp;
    <a href="https://instagram.com/unitary.hk">Instagram</a> &nbsp;·&nbsp;
    <a href="../sitemap.xml">Sitemap</a> &nbsp;·&nbsp;
    CC BY-NC-SA 4.0</p>
</div>

{FILTER_JS}
</body>
</html>
'''


# === 7.5 Filter JS fallback (in-app browser 對 :has() chain timing 唔 reliable) ===
FILTER_JS = '''
<script>
// Filter JS fallback (因為 in-app browser 對 :has() chain timing 唔 reliable, 0% fetch / 純 DOM)
(function() {
  var gameGrid = document.getElementById('game-grid');
  if (!gameGrid) return;
  var inputs = document.querySelectorAll('.filter-input');
  var cards = Array.prototype.slice.call(gameGrid.querySelectorAll('.game-card'));
  var cardData = cards.map(function(c) {
    return {
      el: c,
      players: (c.getAttribute('data-players') || '').split(' '),
      time: (c.getAttribute('data-time') || '').split(' '),
      diff: (c.getAttribute('data-diff') || '').split(' '),
      type: (c.getAttribute('data-type') || '').split(' '),
    };
  });
  function getChecked(groupPrefix) {
    var vals = [];
    inputs.forEach(function(inp) {
      if (inp.id.indexOf(groupPrefix) === 0 && inp.checked) {
        vals.push(inp.id.substring(groupPrefix.length));
      }
    });
    return vals;
  }
  function updateFilter() {
    var pVals = getChecked('f-players-');
    var tVals = getChecked('f-time-');
    var dVals = getChecked('f-diff-');
    var tyVals = getChecked('f-type-');
    cardData.forEach(function(c) {
      var show = true;
      if (pVals.length && !pVals.some(function(v) { return c.players.indexOf(v) >= 0; })) show = false;
      else if (tVals.length && !tVals.some(function(v) { return c.time.indexOf(v) >= 0; })) show = false;
      else if (dVals.length && !dVals.some(function(v) { return c.diff.indexOf(v) >= 0; })) show = false;
      else if (tyVals.length && !tyVals.some(function(v) { return c.type.indexOf(v) >= 0; })) show = false;
      c.el.style.display = show ? '' : 'none';
    });
  }
  inputs.forEach(function(inp) { inp.addEventListener('change', updateFilter); });
  updateFilter();
})();
</script>
'''


# === 8. Main build ===
# === 8.5 Blog article page (5 query 嘅 link 目標) ===
def render_blog_article(query):
    games = load_games()
    games_by_id = {g['id']: g for g in games}

    # Build game cards for the article body
    article_cards = []
    for gid in query['games']:
        if gid not in games_by_id:
            continue
        g = games_by_id[gid]
        box_filename = g.get('box_image', '').split('/')[-1] if g.get('box_image') else ''
        box_html = f'<img src="images/{box_filename}?v={BUILD_HASH}" alt="{escape_html(g["name"])} 盒面" loading="lazy">' if box_filename else '🎲'
        article_cards.append(f'''        <a class="article-game-card" href="{g['id']}.html">
            <div class="article-game-card-box">{box_html}</div>
            <div class="article-game-card-body">
                <h3 class="article-game-card-name-zh">{escape_html(g['name'])}</h3>
                <p class="article-game-card-name-en">{escape_html(g['name_en'])}</p>
                <p class="article-game-card-tagline">{escape_html(g.get('tagline', ''))}</p>
                <p class="article-game-card-summary">{escape_html(g.get('summary', ''))}</p>
                <div class="article-game-card-meta">
                    <span>👥 {g['min_players']}-{g['max_players']}人</span>
                    <span>⏱️ {escape_html(g['play_time'])}</span>
                    <span>📚 {escape_html(g['difficulty_label'])}</span>
                </div>
            </div>
        </a>''')
    article_cards_html = '\n'.join(article_cards)

    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(query['title'])} — UNITARY 開枱指南</title>
    <meta name="description" content="{escape_html(query['intro'])}">
    <link rel="canonical" href="https://unitaryhk.com/board-game/{query['slug']}.html">
    <meta property="og:title" content="{escape_html(query['title'])} — UNITARY 開枱指南">
    <meta property="og:description" content="{escape_html(query['intro'])}">
    <meta property="og:type" content="article">
    <link rel="stylesheet" href="../blog.css">
</head>
<body>

<div class="nav"><div class="nav-inner">
    <a href="../index.html"><img src="../logo.png" alt="UNITARY"></a>
    <a href="index.html" style="margin-left:auto;color:#999;font-size:0.95rem">← 桌遊列表</a>
</div></div>

<div class="article-layout">
    <article class="article-main">
        <a href="index.html" class="back">← 返回桌遊列表</a>
        <div class="article-hero">
            <div class="hero-eyebrow">{escape_html(query['icon'])} {escape_html(query['best_for'])}</div>
            <h1>{escape_html(query['title'])}</h1>
            <p class="article-summary">{escape_html(query['intro'])}</p>
        </div>

        <div class="article-games">
{article_cards_html}
        </div>

        <hr>
        <p style="margin-top:40px"><a href="index.html" class="back">← 返回桌遊列表</a></p>
    </article>
</div>

<div class="blog-footer">
    <p>© 2026 UNITARY &nbsp;·&nbsp;
    <a href="../board-game/">← 開枱指南</a> &nbsp;·&nbsp;
    <a href="https://instagram.com/unitary.hk">Instagram</a> &nbsp;·&nbsp;
    <a href="../sitemap.xml">Sitemap</a> &nbsp;·&nbsp;
    CC BY-NC-SA 4.0</p>
</div>

</body>
</html>
'''


def main():
    games = load_games()
    print(f"Loaded {len(games)} games from games.json")

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

    index_html = render_index_page()
    with open(ROOT / 'index.html', 'w') as f:
        f.write(index_html)
    print(f"  ✓ index.html ({len(index_html)} chars)")

    # === 5 個 blog 文章 (sidebar 5 query 嘅 link 目標) ===
    QUICK_QUERY = [
        {
            'id': 'q5', 'icon': '👥', 'title': '5 個人玩咩桌遊',
            'slug': '5-person-games',
            'games': ['camel-up', 'bohnanza', 'catan', 'manila', 'seti'],
            'intro': '5 個人想開枱, 揀咩桌遊好? 5 人場係桌遊最常見嘅人數, 大部分桌遊都支援。要揀到啱嘅, 留意 3 個條件: (1) 5 人場係官方支援嘅人數 (唔係要變體); (2) 遊戲時間 60 分鐘內; (3) 5 人都有事可做 (唔好有玩家坐冷板櫈)。以下 5 個係 5 人場嘅首選, 全部官方支援, 全部有中文版 (除咗 SETI)。',
            'best_for': '新手第一次約 5 個人, 想搵個大家都鍾意嘅',
        },
        {
            'id': 'q30', 'icon': '⏱️', 'title': '30 min 內完一局',
            'slug': '30-min-games',
            'games': ['camel-up', 'dnup'],
            'intro': '30 分鐘想完一局, 即係要派對向、規則淺、回合短。呢類桌遊通常每局 15-30 min, 教 5-10 分鐘, 2-3 局可以連開。適合飯局前後、朋友敘舊、warm-up。',
            'best_for': '飯局 / 朋友聚會 / 想玩多局',
        },
        {
            'id': 'qnew', 'icon': '🆕', 'title': '新手第一次玩',
            'slug': 'newbie-games',
            'games': ['camel-up', 'dnup', 'take-time'],
            'intro': '第一次玩桌遊嘅新手, 最重要係「教 5 分鐘就識, 玩 30 分鐘就投入」。呢 3 個都係規則淺、容錯高、新手唔會被「卡住」嘅選擇。合作向嘅 take-time 更適合怕輸嘅玩家, 競爭向嘅 camel-up 同 dnup 就鍾意贏嘅感覺。',
            'best_for': '新手入門 / 教朋友 / 第一次約會',
        },
        {
            'id': 'qcoop', 'icon': '🤝', 'title': '合作桌遊',
            'slug': 'coop-games',
            'games': ['take-time'],
            'intro': '合作桌遊 (cooperative game) 係玩家一齊打 AI / 機制, 唔係互相打。輸贏都係一齊, 唔會有人被淘汰, 適合唔想競爭嘅玩家、約會、家人。但合作桌遊少, 而家收錄嘅只有 1 個 (掌握時刻)。',
            'best_for': '情侶 / 家庭 / 唔想互打嘅玩家',
        },
        {
            'id': 'qcn', 'icon': '🇭🇰', 'title': '中文版',
            'slug': 'chinese-edition',
            'games': ['bohnanza', 'catan', 'take-time', 'project-l'],
            'intro': '新手最常問「有冇中文版?」呢個就係答案。收錄嘅 9 個桌遊入面, 4 個有繁體中文版 (台灣繁中 / 香港繁中), 1 個有簡體中文, 4 個暫時只有英文版。中文版嘅好處係新手唔使睇英文規則, 旺角店亦大路貨。',
            'best_for': '新手 / 唔想睇英文規則 / 送禮',
        },
    ]
    for q in QUICK_QUERY:
        html = render_blog_article(q)
        out_path = ROOT / f'{q["slug"]}.html'
        with open(out_path, 'w') as f:
            f.write(html)
        print(f"  ✓ {q['slug']}.html ({len(html)} chars)")

    print(f"\n=== Done! 全部 server-rendered, 5 fix 全部 apply ===")

if __name__ == '__main__':
    main()
