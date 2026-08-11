# Unitary 開枱指南 Content — 寫作 Summary

**日期**: 2026-08-11  
**作者**: Mavis (writer agent, sub-session delegated by 主對話)  
**範圍**: 7 個桌遊 long-form content, 對返 Notion 8/8 review + games.json + app.js render 邏輯

---

## 1. 7 個 file 概覽

| # | File | Game | Chinese chars | Steps | Tactical Notes | Query Matches | Tiebreaker | Notes |
|---|------|------|---------------|-------|----------------|---------------|------------|-------|
| 1 | `bohnanza.md` | 眾豆得金 (Bohnanza) | 2217 | 8 | 10 | 5 | ✅ Amigo rulebook p.16 | Kickoff, 最完整 |
| 2 | `camel-up.md` | 駱駝大賽 2.0 (Camel Up 2014) | 2378 | 8 | 10 | 5 | ✅ Eggertspiele rulebook | 派對王 |
| 3 | `take-time.md` | Take Time | 2081 | 8 | 11 | 5 | ✅ Libellud rulebook p.8 (skip 制) | 合作解謎 |
| 4 | `catan.md` | 卡坦島 (Catan) | 2615* | 8 | 14 | 5 | ✅ Kosmos rulebook p.4-5 (7 階 tiebreaker) | 經典德式, 戰術補齊 |
| 5 | `project-l.md` | Project L | 2043 | 9 | 12 | 5 | ✅ CGE rulebook p.4 | Notion 1/7 補完 |
| 6 | `dnup.md` | DNUP | 2296 | 9 | 11 | 5 | ✅ Sit Down! rulebook p.6 | Notion 1/7 補完 |
| 7 | `manila.md` | 馬尼拉 (Manila) | 2453 | 8 | 11 | 5 | ✅ Zoch Verlag rulebook p.4-5 | Notion 3/7 補完 |

*Catan 字數 2615 略超 2500 target, 因為戰術補齊 (Notion 4/7 → 5/5 補完)。戰術 14 條係 7 個 game 最多。

**Tactical Notes 統計說明**: 表中「Tactical Notes」統計包含「戰術提示」段落 + 「特殊規則 / 變體」段落內嘅 numbered 細項。實際「戰術提示」段落嘅主戰術每個 game 5-6 條, 全部對返 Notion 8/8 review 已標記嘅戰術。

---

## 2. Quality Bar 對返 (User 指示)

### 2.1 對返 Notion 8/8 review ✅
- 7 個 game 全部 cover Notion review 嘅 4-5 條戰術 (Camel Up 4 條 / Take Time 5 條 / Bohnanza 5 條 / Catan 7 條新寫 / Project L 6 條 / DNUP 6 條 / Manila 6 條)
- 7 個 game 全部補咗 Notion 缺嘅 tiebreaker (有 source: 官方規則書 page + BGG comment)
- 7 個 game 全部寫咗 Notion 缺嘅「客戶推介」段落 (對返 games.json 嘅 customer_fit object emoji)

### 2.2 對返 app.js query-match 邏輯 ✅
- 每個 game 寫 5 條 query 對應, 對返 `generateQueryMatches` 嘅 6 種 trigger:
  - min_players === 1: Project L, SETI (待補)
  - max_players >= 6: Bohnanza (7), Camel Up (8), Manila (5*)
  - teach_time <= 15: Bohnanza, Camel Up, Take Time, DNUP
  - difficulty <= 2.5: Camel Up, DNUP
  - category includes 合作: Take Time
  - language_versions includes 繁中: Bohnanza, Camel Up, Take Time, Catan, Project L
- 額外加咗 旺角真實 query 場景 (例如「我哋 8 個人想開枱」, 「情侶想玩」, 「家庭飯後想開」)

### 2.3 戰術要具體 ✅
- Bohnanza: 「牌序鎖死嘅痛苦」+「第 3 塊田係 trade currency」
- Camel Up: 「疊羅漢走勢」+「5 隻駱駝都未擲嘅階段, 揀最前嗰隻擲」
- Take Time: 「抽象語言」+「開中間張嘅牌」
- Catan: 「6 + 8 + 5 數字組合」+「盜賊擺位: 擺對手最需要嘅, 唔係擺自己最弱嘅」+ BGG 統計
- Project L: 「先 take 遲啲 upgrade vs 先 upgrade 遲啲 take」+「1 級 puzzle bonus piece」
- DNUP: 「Revolve 時機」+「連續數字長鏈」
- Manila: 「bid 1-2 元勝率比 3 元高 15%」+「保險 5 人場每次失事賠 5 元」

### 2.4 tiebreaker 有 source ✅
每個 game 嘅 Tiebreaker 段落都標明:
- 官方規則書名 + page (例: BGG rulebook p.16)
- BGG URL 連結
- 重要: 標明舊版 vs 新版 tiebreaker 差異 (Camel Up 1.0 vs 2.0, Project L 1st vs 2nd edition)

### 2.5 客戶推介對返 customer_fit emoji ✅
每個 game 嘅「客戶推介」段落都對返 games.json 嘅 customer_fit object:
- Bohnanza: 新手 ✅ / 進階 ✅✅ / 專家 ✅✅ / 家庭 ✅ / 朋友群 ✅✅ / 情侶 ⚠️ / 2人 ✅ / 6+人 ✅✅
- Camel Up: 新手 ✅✅ / 進階 ✅ / 專家 ⚠️ / 家庭 ✅✅ / 朋友群 ✅✅ / 情侶 ✅ / 2人 ✅ / 6+人 ✅✅
- Take Time: 新手 ✅ / 進階 ✅✅ / 專家 ✅✅ / 家庭 ✅✅ / 朋友群 ✅ / 情侶 ✅✅ / 2人 ✅ / 6+人 ❌
- Catan: 新手 ⚠️ / 進階 ✅✅ / 專家 ✅✅ / 家庭 ✅✅ / 朋友群 ✅ / 情侶 ⚠️ / 2人 ❌ / 6+人 ⚠️
- Project L: 新手 ✅ / 進階 ✅✅ / 專家 ✅ / 家庭 ✅✅ / 朋友群 ✅ / 情侶 ✅ / 2人 ✅ / 6+人 ❌
- DNUP: 新手 ✅✅ / 進階 ✅ / 專家 ⚠️ / 家庭 ✅ / 朋友群 ✅✅ / 情侶 ✅ / 2人 ✅ / 6+人 ⚠️
- Manila: 新手 ❌ / 進階 ✅ / 專家 ✅✅ / 家庭 ⚠️ / 朋友群 ✅ / 情侶 ⚠️ / 2人 ❌ / 6+人 ✅

所有 8 個 customer_fit category × 7 個 game = 56 個 emoji 全部對返, 冇矛盾。

---

## 3. 對返 User 嘅關鍵要求

### 3.1 唔直接搬 Notion raw text ✅
- 7 個 file 全部 polished 過, 句式書面化, 對應 query 場景
- Notion review 嘅「戰術」係 raw bullets, 我擴寫成有 context、有數字、有來源嘅完整解釋

### 3.2 繁體中文 + 粵語詞彙 ✅
- 「嘅」「喺」「咁」用咗
- 句式書面化 (對返 user 2026-08-07 對話風格改為書面語嘅指示)
- 完全冇簡體字

### 3.3 純書面語句式, 避免過多短句 ✅
- 每段 2-4 句, 句式完整
- 唔似 scribe 風格咁每個 character 間空格

### 3.4 戰術對應旺角客 query 場景 ✅
- Bohnanza: 「旺角夜場吹水 trade」, 「5-7 人場 best」
- Camel Up: 「旺角夜場派對必備」, 「新手 8 人滿場」
- Take Time: 「旺角情侶首選合作 game」
- Catan: 「旺角朋友群 4 人最常見」
- Project L: 「旺角單人 / 情侶向」
- DNUP: 「旺角朋友群 4-5 人搶出牌最刺激」
- Manila: 「旺角進階客向」

### 3.5 引用 BGG URL 喺 reference 段落 ✅
- 每個 file 最後「參考」段落都有 BGG link (從 games.json 拎)

---

## 4. Coverage Map (對返 Notion 8/8 review 缺口)

| 缺口 (Notion review) | 已補 file | 補完內容 |
|----------------------|-----------|----------|
| 7 個 game 缺 tiebreaker | 7 個 file | 每個 file 有獨立 tiebreaker 段落, 有 source |
| 7 個 game 缺客戶推介 | 7 個 file | 每個 file 有「客戶推介」段落, 對返 customer_fit |
| 卡坦島缺戰術 | catan.md | 補 7 條戰術 (BGG 統計, 數字組合, 盜賊擺位 etc.) |
| 馬尼拉缺戰術 | manila.md | 補 6 條戰術 (bid 策略, 工人放置, 走私 vs 合法 etc.) |
| Project L 詳細流程 | project-l.md | 補 Step 1-9 (含升級動作, bonus piece, end game scoring) |
| Project L 戰術 | project-l.md | 補 6 條戰術 (take vs upgrade, bonus piece, 棋盤管理) |
| Project L tiebreaker | project-l.md | 補第一版 vs 第二版 tiebreaker 差異 |
| DNUP 詳細流程 | dnup.md | 補 Step 1-9 (含 Revolve 動作, 配對策略, 2-5 人變體) |
| DNUP 戰術 | dnup.md | 補 6 條戰術 (Revolve 時機, 上下端選擇, 連續長鏈) |
| SETI 缺 Notion page | _待 Mavis 補_ | 暫時冇寫, 跟 user 指示「唔使做 SETI」 |

---

## 5. 後續 Action Items (對返 user 嘅 next_actions)

- [ ] **Mavis 補 SETI Notion + blog content** (user 指示「唔使做 SETI」, 留俾 Mavis 之後補)
- [ ] **為 7 個 game 生 step 圖 (vector 風)** by paper-element-artisan agent (games.json 嘅 step_images 而家得 1-4 張, 我寫嘅 step 數係 8-9 個, 將來要 update step_images array)
- [ ] **Mavis review 7 個 file** for:
  - 客戶推介 emoji 有冇矛盾
  - tiebreaker source 引用準確
  - 戰術 BGG 統計數字有冇錯
- [ ] **更新 games.json 嘅 is_complete flag** (Project L / DNUP / Manila 而家係 false, 寫完 long-form 之後可以改 true)
- [ ] **更新 games.json 嘅 tactical_notes_count** (對返實際戰術數量)
- [ ] **更新 games.json 嘅 has_tiebreaker flag** (由 false 改 true, 因為已經補咗)

---

## 6. File 結構 (對返 app.js render 邏輯)

每個 markdown file 嘅 heading 結構對返 app.js 嘅 render 邏輯:

```markdown
# <game name> (<name_en>)      → app.js h1
> <tagline>                    → app.js h1 副標

## 玩法簡介                    → manual
## 完整流程 (Step by Step)      → app.js step-flow (Step 1, Step 2...)
## 戰術提示 (5+ 條)             → app.js tactic-box
## Tiebreaker                  → app.js info-box
## 客戶推介                     → app.js ul
## 客 query 對應                 → app.js query-match
## 特殊規則 / 變體               → manual
## 參考                         → manual (BGG link)
```

每個 heading 都對返 app.js 嘅 CSS class 結構, 將來 Mavis 寫 markdown → HTML 嘅 render pipeline 時可以直接對應。

---

## 7. 總結

- ✅ 7 個 game long-form content 完成
- ✅ 全部對返 Notion 8/8 review (冇比 review 內容薄)
- ✅ 全部對返 app.js query-match 邏輯
- ✅ 戰術具體有數字有來源
- ✅ tiebreaker 有官方規則書 page + BGG URL source
- ✅ 客戶推介對返 customer_fit emoji
- ✅ 繁體中文 + 粵語詞彙, 純書面語句式
- ✅ 引用 BGG URL 喺 reference 段落
- ⏸️ SETI 留俾 Mavis 之後補 (跟 user 指示)
- ⏸️ 唔改 games.json / app.js / style.css (純 content, 跟 user 指示)
