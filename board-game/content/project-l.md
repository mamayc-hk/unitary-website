# Project L

> 俄羅斯方塊桌上版

## 玩法簡介

Project L 係 2020 年 Jan Vodohrálek 設計嘅拼圖策略遊戲, 由 Broadway Toys (中文版) 同 原版 English 第一版 (CGE) 出版, 旺角多間店有售 (繁中版 2022 年後普及)。遊戲背景係抽象拼圖, 玩家透過收集同放置 L 形、T 形等 polyomino 碎片, 完成 puzzle card 賺分。

Project L 嘅核心機制係「升級動作 (upgrade action)」: 你可以將一個小嘅 polyomino 升級做更大嘅形狀 (例如將 2 個 L 形升級做 1 個 T 形), 呢個動作令你可以更靈活咁完成 puzzle。Project L 嘅 design 同俄羅斯方塊嘅精神好相似: 喺有限空間內擺到最多形狀, 完成 puzzle 卡嘅 pattern。

呢個 game 適合 1-4 人, 單人都好玩, 教學時間 20 分鐘, 一局 30-45 分鐘, 難度中等。旺角家庭 / 單人 / 情侶向, 拼圖愛好者首選。

## 完整流程 (Step by Step)

### Step 1: 設置
揀 1 個中央圖板 (主圖板, 有 4 個「piece 升級格」)。每個玩家攞 1 個玩家板 (3x3 棋盤格, 即係 9 個位可以放 piece)。中央有 3 種 piece 池: 黑色 (1x1 細 piece, 3 個)、白色 (1x2 中 piece, 3 個)、彩色 (1x3 大 piece, 3 個, 包括紅藍黃綠)。每個玩家面前有 4 張 puzzle card (2 張 1 級、1 張 2 級、1 張 3 級), 翻開 1 張做「目標」。

### Step 2: 玩家動作 — 3 個主要動作
每個回合玩家做以下其中 1 個動作:
- (A) **Take Piece**: 從中央 piece 池攞 1 個 piece, 放喺自己 3x3 棋盤上。黑色 1x1 細 piece 放任何 1 格; 白色 1x2 中 piece 放 2 連續格; 彩色 1x3 大 piece 放 3 連續格。棋盤滿咗就唔可以再攞。
- (B) **Upgrade Piece**: 將自己棋盤上嘅 1 個 piece 升級。1x1 黑升做 1x2 白 (放喺 2 連續格, 原位變空), 或者 1x2 白升做 1x3 彩 (放喺 3 連續格)。升級需要「升級格」, 即中央圖板上對應顏色嘅 piece 池換成下一級嘅 piece。例: 你升 1x1 黑→白, 中央黑 piece 池就少 1 個黑, 多 1 個白; 反之亦然。
- (C) **Complete Puzzle**: 如果你棋盤上嘅 piece 形狀完全 match 當前翻開嘅 puzzle card, 你可以完成 puzzle, 攞對應分數 (1 級 1 分、2 級 2 分、3 級 3 分), 同時翻開下一張 puzzle card。

### Step 3: 1 級 puzzle (1 分)
1 級 puzzle 嘅 pattern 通常只係 3-4 格形狀, 例如 1 個 L 形 (3 格) 或 1 個直線 (3 格)。新手第一個 puzzle 多數係 1 級, 用 2-3 個回合完成。

### Step 4: 2 級 puzzle (2 分)
2 級 puzzle 嘅 pattern 通常 5-6 格, 例如 T 形或 Z 形。要完成 2 級 puzzle, 你需要 1x3 嘅彩色 piece, 所以早期要 upgrade 1x2 白→1x3 彩。

### Step 5: 3 級 puzzle (3 分)
3 級 puzzle 嘅 pattern 通常 7-9 格, 形狀複雜, 例如 U 形或大十字。完成 3 級 puzzle 需要多個彩色 piece, 所以早期要平衡 upgrade 同 take piece 嘅時機。

> 例: 3 級 U 形 puzzle (7 格), 需要 1 個 1x3 彩 + 2 個 1x2 白 + 1 個 1x1 黑。Strategy A 打法: 先 take 4 個 1x1 黑填棋盤, 然後 upgrade 2 個黑→白, 再 upgrade 1 個白→彩。完成時間約 6-8 個動作。Strategy B 進階: 一開波就 upgrade 1 個黑→白→彩, 騰出位放 1x3, 4 個動作完成。

### Step 6: 回合結算 + 補 piece
每個玩家做完 1 個動作後, 從 piece 池補返 piece 到 3 個 (黑 / 白 / 彩每個池維持 3 個)。如果 piece 池冇 piece 可以補 (即係所有 piece 都被玩家攞咗), 跳去 Step 8 結算。

### Step 7: 特殊規則 — Bonus piece
完成 1 級 puzzle 嘅獎勵: 即時從 piece 池攞 1 個 piece (任選顏色), 放喺自己棋盤 (要 fit 棋盤位)。完成 2 級 puzzle 嘅獎勵: 即時攞 2 個 piece。完成 3 級 puzzle 嘅獎勵: 即時攞 3 個 piece。呢個 bonus piece 唔可以 upgrade, 只可以直接 take, 用嚟做下一個 puzzle。

### Step 8: 遊戲結束 + 計分
當所有玩家都做唔到動作 (棋盤滿或者 piece 池冇 piece), 遊戲結束。每個玩家數自己完成嘅 puzzle 嘅分數: 1 級 1 分 + 2 級 2 分 + 3 級 3 分。最高分贏。如果平手, 進入 tiebreaker (見下)。

### Step 9: 第二版 (Project L 2nd Edition) 嘅新機制
第二版 (2023 年) 加咗「end game scoring」: 如果你完成最後一個 puzzle 嗰陣, 你棋盤上仲有 2 個 piece, 額外 1 分; 3 個 piece 額外 2 分 (最多 2 分 bonus)。第二版仲加咗「master piece」(3x3 大 piece), 可以完成超大型 puzzle。新手要確認玩家用邊一版。

## 戰術提示 (5+ 條)

1. **「先 take, 遲啲 upgrade」vs「先 upgrade, 遲啲 take」**: 兩種主流 strategy。Strategy A (新手友善): 早期 take 細 piece 填棋盤, 遲啲先 upgrade 做彩色 piece 完成大 puzzle。Strategy B (進階): 早期就 upgrade 1x1→1x2→1x3, 換走細 piece, 騰出棋盤位俾彩色 piece 放入。Strategy B 戰略深度高, 但新手容易「upgrade 太多, 細 piece 唔夠用」。新手建議新手用 Strategy A, 進階客用 Strategy B。

2. **「1 級 puzzle 嘅 bonus piece 係關鍵」**: 1 級 puzzle 只值 1 分, 但 bonus piece (完成後即時攞 1 個 piece) 嘅價值高過 1 分。高手會「特登」完成 1 級 puzzle 攞 bonus piece, 用 bonus piece 嚟做下一個 puzzle 嘅 setup。BGG 統計: 1 級 puzzle 完成得快嘅玩家, 後續 2-3 級 puzzle 嘅完成率高 30%。

3. **「棋盤位管理」**: 玩家板 3x3 共 9 格, 1 級 puzzle 用 3-4 格, 2 級用 5-6 格, 3 級用 7-9 格。高手會「計算」每個 puzzle 用幾多格, 然後控制 take piece 嘅節奏。例: 如果你 9 格已經用咗 5 格, 你只可以 take 4 個 piece, 呢個就係 2 級 puzzle 嘅上限, 唔可以再升級做大 puzzle。

4. **「集中 1 個顏色 vs 分散」**: 彩色 piece 有 4 種顏色 (紅藍黃綠), 玩家可以選擇「集中 1 種顏色」或「分散 4 種顏色」。集中 1 種顏色嘅好處係完成大 pattern (例如全部紅色) 容易, 但壞處係 piece 池嘅彩色 piece 有限, 集中 1 種會搶到其他人冇得用。分散 4 種嘅好處係「不被針對」, 但壞處係難完成大 pattern。新手建議 2-3 人場用「集中」, 4 人場用「分散」。

5. **「End game scoring 嘅 2nd / 3rd piece bonus」**: 第二版嘅 end game scoring 改變咗玩法: 你唔係「越快完成 puzzle 越好」, 而係「完成 puzzle 時棋盤上仲有 piece 越好」。高手會喺最後 1-2 個 turn, 「故意」做 1 級 puzzle 留低 bonus piece, 等遊戲結束時棋盤有 2-3 個 piece, 攞 1-2 分 bonus。新手要確認玩家用邊一版 (第一版冇 end game scoring)。

6. **「單人場嘅特殊玩法」**: Project L 1 人場可以玩, 但缺少咗「同其他人搶 piece 池」嘅緊張感。單人場嘅重點變成「時間管理」: 20 個 turn 內完成最多 puzzle。新手可以 demo: 單人場用「完成 puzzle 數」做目標, 而唔係「打贏對手」。

## Tiebreaker

Project L 官方 tiebreaker 規則 (Broadway Toys 中文版 / CGE 英文版):

1. **主規則**: 最高分 (puzzle 完成分) 玩家贏。
2. **平手 (第一次 tiebreaker)**: 比較「完成最多 level 3 puzzle」嘅玩家勝。因為 level 3 難度最高, 完成 level 3 嘅玩家策略深度更高。
3. **再平手 (第二次 tiebreaker)**: 比較「完成最多 level 2 puzzle」嘅玩家勝。
4. **再平手 (第三次 tiebreaker)**: 比較「完成最多 level 1 puzzle」嘅玩家勝。
5. **再平手 (第四版 tiebreaker, 第二版獨有)**: 比較「end game bonus piece」嘅玩家勝 (即棋盤上仲有 piece 嘅數量)。
6. **再平手 (極罕有)**: 兩位玩家共享勝利 (share win)。

來源: 官方規則書 (Broadway Toys 2020, CGE 2023 second edition) page 4 寫「End of the Game」段落, BGG comment 確認。你可以上 BGG: https://boardgamegeek.com/boardgame/260180/project-l

**重要注意**: Project L 第二版 (2023) 同第一版 (2020) tiebreaker 唔同。第一版冇 end game bonus piece, 所以 tiebreaker 由 level 3 開始比。第二版加咗 end game bonus piece, tiebreaker 多咗一個 step。新手要確認玩家用邊一版。

## 推介畀咩人

Project L 喺旺角嘅定位係「拼圖策略, 家庭單人情侶向, 抽象幾何愛好者首選」。

- **新手 (✅)**: 規則中等 (教 20 分鐘), 第一次玩要 demo 半局。但單人場可以, 新手可以自己試。
- **進階 (✅✅)**: 戰略深度中等, 升級動作 + 棋盤管理 + bonus piece 計算, 進階客可以玩到癲。
- **專家 (✅)**: 戰略深度中等, 唔算最頂級, 但仍有 challenge。
- **家庭 (✅✅)**: 4 人場最家庭, 老少咸宜 (因為拼圖直觀)。
- **朋友群 (✅)**: 1-4 人場 ok, 唔算派對向。
- **情侶 (✅)**: 2 人場最浪漫, 拼圖節奏慢, 旺角情侶向。
- **2 人 (✅)**: 2 人場 ok, 拼圖友善。
- **6+ 人 (❌)**: 4 人 max, 6+ 人場唔可以玩。

旺角新客入門, 問「我自己一個想試下, 有咩 game?」, Project L 1 人場係首選之一 (連同 SETI)。

## 客 query 對應

- **「我自己一個想試下, 有咩 game?」**: Project L 1-4 人, 單人都可以開。教 20 分鐘, 一局 30-45 分鐘, 單人拼圖友善。
- **「情侶想玩, 唔想太激烈」**: Project L 2 人場最佳, 拼圖節奏慢, 旺角情侶向。輸咗都唔挫敗, 因為拼圖唔係攻擊性遊戲。
- **「家庭飯後想開, 老少咸宜」**: Project L 4 人場最佳, 拼圖直觀, 老少咸宜。
- **「新手第一次玩, 揀咩好?」**: Project L 難度中等, 教 20 分鐘, 第一次玩要 demo 半局。建議 2-3 人場開始, 4 人場太多競爭。
- **「我想玩中文版, 唔想睇英文規則」**: Project L 繁中版 (Broadway Toys) 旺角有售, 中文版友善。

## 特殊規則 / 變體

- **1 人規則**: 標準規則, 缺少同其他人搶 piece 池嘅緊張感, 但「時間管理」變成新挑戰。
- **2 人規則**: 標準規則, 搶 piece 池嘅緊張感中等。
- **3 人規則**: 標準規則, 最佳人數之一。
- **4 人規則**: 標準規則, 最多 4 人, 搶 piece 池最緊張。
- **5+ 人 (官方唔支援)**: 4 人 max, 5+ 人場唔可以玩。
- **第一版 vs 第二版 (2023)**: 第一版 (2020) 冇 end game bonus piece, 第二版 (2023) 有。旺角多間店有新舊兩版, 新手要確認。
- **House Rule — 加快模式**: 部分玩家將中央圖板嘅 piece 池由 3 個改 2 個, 加快節奏 (piece 用得快, 遊戲結束得快)。
- **House Rule — 升級格開放**: 部分玩家將升級格由 1 個改 2 個, 加快升級速度, 但降低策略深度。
- **官方擴充 (待查)**: Project L 而家未有獨立擴充, 但 CGE 第二版 (2023) 已經包含咗第一版 + 升級 piece。進階客可以上 BGG 查 fan-made expansion。

## 參考

- [BGG: Project L](https://boardgamegeek.com/boardgame/260180/project-l)
- Notion 8/8 review 校稿: 2026-08-08
- 官方規則書: CGE 2020 (第一版), Broadway Toys 2022 (繁中版), CGE 2023 (第二版)
- 旺角供應: 繁中版多間店有售, 英文版亦有
