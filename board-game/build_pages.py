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
from pathlib import Path

ROOT = Path('/Users/herry/Documents/Cherry/unitary-website/board-game')

# === 1. Markdown → HTML parser (with example box detection) ===
def escape_html(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def md_inline(text):
    text = escape_html(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    return text

def md_to_html(md_text):
    lines = md_text.split('\n')
    out = []
    in_list = None
    in_quote = False
    para_buf = []
    in_faq = False  # FAQ 識別

    def flush_para():
        nonlocal para_buf
        if para_buf:
            text = ' '.join(para_buf)
            # Detect example box: 句子以 "例:", "BGG 統計", "例如" 開頭
            if re.match(r'^\s*(例[:：]|BGG 統計|例如)', text):
                out.append(f'<div class="example-box"><p><strong>💡 Example</strong> {md_inline(text)}</p></div>')
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
            out.append(f'<h{level}>{md_inline(heading_text)}</h{level}>')
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
                out.append(f'<div class="example-box"><p><strong>💡 Example</strong> {md_inline(content)}</p></div>')
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
                out.append(f'<li><div class="example-box"><p><strong>💡 Example</strong> {md_inline(item)}</p></div></li>')
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
                out.append(f'<li><div class="example-box"><p><strong>💡 Example</strong> {md_inline(item)}</p></div></li>')
            else:
                out.append('<li>' + md_inline(item) + '</li>')
            i += 1; continue

        para_buf.append(stripped)
        i += 1

    flush_para(); flush_list(); flush_quote()
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
        '💡 <strong>Mirage 拖慢領先者</strong>比 Oasis 推落後者更 strategic',
    ],
    'take-time': [
        '**每人有 Lunar (白) + Solar (黑) 各 1-12 牌**',
        '**時鐘圖版有 6 個 segments**, 每人輪流放 1 張',
        '**3 階段**: 討論 (可講) → 出牌 (沉默) → 結算',
        '**每 segment 嘅數值 = 該 segment 所有牌嘅總和**',
        '**開牌額度** (Reminder Token) 可以公開出牌',
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
        'point_text': '7 人滿場, 旺角夜場吹水 trade 嘅派對首選',
    },
    'camel-up': {
        'story': '埃及沙漠, 5 隻駱駝賽跑, 你落注邊隻贏。但有 2 隻瘋狂駱駝會騎上去 — 疊羅漢嘅瞬間, 頭馬可以一秒變包尾。駱駝大賽嘅魔力在於: 規則簡單到 5 分鐘教完, 但心理戰可以玩到天光。',
        'point_emoji': '🎲',
        'point_text': '8 人派對王, 規則最淺但落注心理戰深',
    },
    'take-time': {
        'story': '你哋一齊解謎, 但討論完之後出牌嘅時候唔可以講嘢。要靠默契去估計隊友手上有咩牌, 會放喺邊個位置。贏嘅時候大家一齊嗌, 輸嘅時候大家都好想話「我明明擺咗呢個數字㗎嘛!」。',
        'point_emoji': '🤫',
        'point_text': '合作默契 game, 情侶 / 家庭 / 朋友首選',
    },
    'catan': {
        'story': '你哋去咗一個新島, 要喺度建立道路、村莊、城市, 搶資源, 同對手 trade。卡坦島係 1995 年嘅經典德式策略, 30 年後依然係新手入門策略 game 嘅 first choice — 因為規則清晰, 戰略深, 中文書好搵。',
        'point_emoji': '🏝️',
        'point_text': '經典德式策略始祖, 中文版普及',
    },
    'project-l': {
        'story': '俄羅斯方塊嘅桌上版, 你收集 polyomino 碎片, 喺 puzzle card 上拼出指定形狀。每完成一個 puzzle, 你攞分 + bonus, 仲可以升級 master piece 攞更多容量。1-4 人彈性, 單人都好玩。',
        'point_emoji': '🧩',
        'point_text': '俄羅斯方塊桌上版, 1-4 人彈性, 單人都 work',
    },
    'dnup': {
        'story': '你同 2-4 個對手鬥快清空手牌, 但你嘅牌上下端數字唔同, 你可以「Revolve」翻轉整把手牌 — 選擇權喺你, 但要計準時機。DNUP 嘅設計簡潔: 15 分鐘教晒, 30 分鐘完一局, 旺角朋友群嘅派對王。',
        'point_emoji': '🔄',
        'point_text': '15 分鐘教晒, 30 分鐘完一局, 派對快速 game',
    },
    'manila': {
        'story': '19 世紀馬尼拉港, 你係投資者, 要競投船長、買股票、合法入貨定走私, 務求喺港口經濟戰入面賺最多。馬尼拉嘅戰略深度高, 6 個職位 × 3 種股票 × 港灣選擇, 專家可以玩到天光。',
        'point_emoji': '⚓',
        'point_text': '港口經濟戰, 進階專家向, 戰略深度高',
    },
}


# === 4. Cheat Sheet 段 (Fix D, sidebar sticky) ===
# 5 條 critical tactical tips, 對應教客 review 場景
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
        '⚡ <strong>2 人場</strong>用隻人牌, 玩兩個連續回合',
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
        ('幾耐可以教完新手?', '15 分鐘教晒, 但新手要玩 2-3 局先掌握牌序鎖死嘅痛苦。第一次玩要 demo 1 局俾客睇。'),
    ],
    'camel-up': [
        ('新手最易犯乜錯?', '揀「冠軍」嘅駱駝落注, 忽略「疊羅漢」效應。高手會揀「托」嘅駱駝, 即揹住最多同黨嗰隻。'),
        ('Mirage 同 Oasis 邊個好?', 'Mirage 戰略值 2 倍 Oasis, 因為 Mirage 拖慢領先者而 Oasis 推落後者 (推唔郁)。'),
        ('8 人場坐邊個位最好?', '坐第 1 位擲骰, 之後 7 個人可以根據新形勢落注, 最靈活。坐最後 1 位最蝕底但可以揀最冷門注。'),
        ('觀眾圖板幾時放?', '永遠先擺 Mirage 喺領先嗰隻嘅下一格, 拖慢佢。Oasis 擺喺落後嗰隻嘅下一格, 幫佢追。'),
        ('1.0 同 2.0 邊個較好?', '2.0 tiebreaker 較複雜但有 Mirage/Oasis 變化, 旺角 8 成以上都係 2.0, 教客前要確認。'),
    ],
    'take-time': [
        ('可以出牌時講嘢嗎?', '唔可以, 呢個係 Take Time 嘅核心。出牌階段要沉默, 靠默契同抽象語言溝通。'),
        ('開牌額度點用?', '每關有指定數量, 建議喺最 critical 嘅 1-2 個 segment 用, 唔好慳住。'),
        ('點解我哋成日超過 24?', '因為大數字冇分配好。建議由細數字開始, 將大數字放最後一段, 留 buffer 俾中間段。'),
        ('2 人可以玩嗎?', '可以但體驗弱, 合作默契感覺唔到。建議 3-4 人。'),
        ('合作輸咗會挫敗嗎?', '唔會, 因為可以 skip 關卡, 唔似其他合作 game 一定要贏。'),
    ],
    'catan': [
        ('3 人場可以玩嗎?', '可以但要 mark 1 個位做「鬼位」, 因為卡坦島 3-4 人, 3 人需要調整。'),
        ('擲 7 點即死?', '唔係死, 係觸發盜賊, 要 half hand, 然後擺盜賊到一個新地形 (搶 1 個玩家 1 張牌)。'),
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
        ('2 人場有咩唔同?', '2 人場移走 3+4+5 符號, 使用隻人牌, 玩兩個連續回合, 戰術變化大。'),
        ('新手最易犯乜錯?', '儲牌唔出, 結果塞到自己。要積極出牌, 即使係差嘅組合。'),
        ('幾耐一局?', '15-20 分鐘, 5 人場最長, 2 人場最短。'),
    ],
    'manila': [
        ('Bid 3 元係咪必贏?', '唔係, 反而蝕底機會大。高手 bid 1-2 元, 因為船長利潤要靠操控 bonus + 職位分錢補返。'),
        ('走私 vs 合法 邊個好?', '睇淨利潤, 合法要扣稅但金額高, 走私 0 稅但金額低。教客時要 demo 計算。'),
        ('3 人場有咩唔同?', '3 人場每個玩家 4 個工人, 可同時佔 2 個職位 (高風險高回報), 4-5 人場只可佔 1 個職位。'),
        ('股票幾時賣?', '股票只有「上」冇「下」, 揀快升嗰隻 (你嘅船都去嘅港灣) 買, 高位賣。'),
        ('新手最大錯誤?', '忽略保險職位。保險係被動收入, 5 人場每次失事賠 5 元, 5 個回合已經回本。'),
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
    gid = game['id']

    # Markdown → HTML
    long_form_html = md_to_html(content_md)

    # Customer fit
    fit_items = ''.join(f'<li><strong>{escape_html(k)}</strong>: {escape_html(v)}</li>\n' for k, v in fit.items())

    # Box image
    box_html = ''
    if box:
        box_filename = box.split('/')[-1]
        box_html = f'<figure><img src="images/{box_filename}" alt="{escape_html(name)} 盒面" loading="lazy"><figcaption>{escape_html(name)} ({escape_html(name_en)}) — {escape_html(publisher)}</figcaption></figure>'

    # Step images
    step_html = ''
    if step_imgs:
        step_items = ''
        for idx, img in enumerate(step_imgs):
            img_filename = img.split('/')[-1]
            step_items += f'<figure><img src="images/{img_filename}" alt="Step {idx+1}" loading="lazy"><figcaption>Step {idx+1}</figcaption></figure>\n'
        step_html = f'<div class="photo-grid">{step_items}</div>'

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
            <h2>⚡ Quick Start — 2 分鐘 onboard</h2>
            <p>新手要 2 分鐘內 make first move, 記住呢 6 條:</p>
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
            <h2>❓ FAQ — 教客常見問題</h2>
            {faq_items_html}
        </div>
        '''

    # Cheat sheet (Fix D, sidebar sticky)
    cs_items = CHEAT_SHEET.get(gid, [])
    cs_html = ''
    if cs_items:
        cs_items_html = '\n'.join(f'<li>{item}</li>' for item in cs_items)
        cs_html = f'''
        <div class="cheat-sheet">
            <h3>📋 Cheat Sheet</h3>
            <p>教客前 30 秒掃一眼:</p>
            <ul>{cs_items_html}</ul>
        </div>
        '''

    # Sidebar quick-jump
    all_games = sorted(load_games(), key=lambda g: (0 if g.get('is_kickoff') else 1, g['id']))
    sidebar_qj = ''
    for g in all_games:
        kickoff_marker = ' 🌟' if g.get('is_kickoff') else ''
        sidebar_qj += f'<a href="{g["id"]}.html">{escape_html(g["name"])}{kickoff_marker}</a>\n'

    complete_badge = '✅ 完整教學' if is_complete else '⚠️ 內容待補'

    return f'''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(name)} ({escape_html(name_en)}) — {escape_html(tagline)} | UNITARY 開枱指南</title>
    <meta name="description" content="{escape_html(summary)}">
    <meta name="keywords" content="桌遊,教學,桌遊教學,{escape_html(name)},{escape_html(name_en)},board game,{escape_html(",".join(cats))},香港桌遊,新手桌遊,教客,旺角">
    <link rel="canonical" href="https://unitaryhk.com/board-game/{gid}.html">
    <meta property="og:title" content="{escape_html(name)} ({escape_html(name_en)}) — {escape_html(tagline)}">
    <meta property="og:description" content="{escape_html(summary)}">
    <meta property="og:type" content="article">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="stylesheet" href="../blog.css">
</head>
<body>

<div class="nav"><div class="nav-inner">
    <a href="../index.html"><img src="../logo.png" alt="UNITARY"></a>
    <a href="index.html" style="margin-left:auto;color:#999;font-size:0.95rem">桌遊教學 →</a>
</div></div>

<div class="layout">
    <div class="main">
        <div class="main-content">
            <a href="index.html" class="back">← 返回桌遊列表</a>

            <!-- Hero 段 (Fix E: Story + Selling Point) -->
            <div class="game-hero">
                <div class="game-hero-meta">
                    <span class="complete-badge">{complete_badge}</span>
                    <span class="game-hero-tagline">{escape_html(tagline)}</span>
                </div>
                <h1>{escape_html(name)} ({escape_html(name_en)})</h1>
                <div class="game-hero-publisher">出版: {escape_html(publisher)} · 類別: {escape_html(", ".join(cats))}</div>

                {box_html}
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
                    <div class="label">語言</div>
                    <div class="value">{escape_html(", ".join(langs))}</div>
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

            <!-- Quick Start (Fix A: 2 分鐘 onboard) -->
            {qs_html}

            <!-- 一句話總覽 -->
            <h2>一句話總覽</h2>
            <p class="summary-block">{summary}</p>

            <h2>玩法 step 圖</h2>
            {step_html}

            <!-- Long-form markdown content (含 inline example box) -->
            <div class="long-form">
                {long_form_html}
            </div>

            <!-- FAQ (Fix C) -->
            {faq_html}

            <hr>

            <h2>🛒 配合資源 (Cross-sell)</h2>
            <div class="cross-sell">
                <p>教客時可以一併推薦:</p>
                <ul>
                    <li><strong>DOSHA 木盒</strong>: <a href="https://instagram.com/dosha.woodcraft" target="_blank" rel="noopener">@dosha.woodcraft</a> 嘅木製收納盒, 配 {escape_html(name)} 嘅 card 完美 fit。</li>
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
        <!-- Sticky Cheat Sheet (Fix D) -->
        {cs_html}
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
        box_html = f'<img src="images/{box_filename}" alt="{escape_html(g["name"])} 盒面" loading="lazy">' if box_filename else '🎲'
        pending = '' if g.get('is_complete', True) else ' <span style="color:var(--color-warn)">⚠️ 待補</span>'

        cards.append(f'''        <a class="game-card" href="{g['id']}.html">
            <div class="game-card-box">{box_html}</div>
            <div class="game-card-body">
                <h3>{escape_html(g['name'])}</h3>
                <p class="game-card-tagline">{escape_html(g.get('tagline', ''))}</p>
                <div class="game-card-meta">
                    <span>👥 {g['min_players']}-{g['max_players']}人</span>
                    <span>⏱️ {escape_html(g['play_time'])}</span>
                    <span>📚 {escape_html(g['difficulty_label'])}</span>{pending}
                </div>
            </div>
        </a>''')

    cards_html = '\n'.join(cards)

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
    <a href="../index.html" style="margin-left:auto;color:#999;font-size:0.95rem">← UNITARY 主站</a>
</div></div>

<div class="layout">
    <div class="main">
        <div class="intro">
            <div class="sub">Design once. Play forever.</div>
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


# === 8. Main build ===
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

    print(f"\n=== Done! 全部 server-rendered, 5 fix 全部 apply ===")

if __name__ == '__main__':
    main()
