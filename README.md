# UNITARY 網站

香港原創 3D 打印桌遊配件品牌官方網誌

🌐 **https://unitaryhk.com**

---

> **📌 桌遊教學內容已搬遷**:
> 桌遊玩法 / 戰術 / tiebreaker / 教客 review 等內容, 2026-08-11 起搬遷去 sub-brand **Unitary 開枱指南** (`unitary-guide/` repo), 唔再更新喺呢度。
> 點解? UNITARY 原有內容對應 3D printer / maker 市場, 教學內容對應桌遊新手 / 教客 query 場景, audience 唔同, 兩個 brand 分開 SEO 同 positioning 都較清。
> 詳見 [桌遊教學 blog 結構決策筆記](#) (待補) 同 `Cherry/unitary-guide/` repo。

---

## 📁 檔案結構

```
├── index.html          # 首頁（文章列表）
├── blog.css            # 全站共用樣式表
├── logo.png            # Logo
├── CNAME               # 自訂域名 (unitaryhk.com)
├── robots.txt          # SEO
├── sitemap.xml         # Sitemap
├── style.css           # 舊設計系統（未使用，保留作參考）
├── post/               # 文章（每篇一個 .html）
│   ├── board-game-organizer-comparison.html
│   ├── start-3d-printing.html
│   ├── splendor-organizer-design.html
│   ├── carcassonne-frame.html
│   ├── flip7.html
│   ├── take-time.html
│   └── unitary-launch.html
├── images/             # 文章圖片
└── .agents/            # AI agent 設定
```

---

## 🚀 新增文章

文章使用純 HTML + `blog.css`。參考現有文章格式：

1. 複製一篇現有文章作為 template
2. 修改 `<title>`、`<meta description>`、OG tags
3. 撰寫文章內容
4. 更新 `index.html` 加入新文章（最新排最頂）
5. 更新所有文章嘅 sidebar「熱門文章」區域
6. 更新 `sitemap.xml`
7. Commit + push

### 可用 CSS class
- `.info-box` — 灰色資訊框
- `.highlight-box` — 橙色重點框
- `.step-box` — 步驟說明框
- `.btn-cta` — CTA 按鈕（橙色）

---

## 📝 寫文章指引

- 目標讀者：香港桌遊玩家 + 3D 打印愛好者
- 每篇文應有明確 SEO 關鍵字
- 所有文章應有至少一個 Cults3D CTA link
- 文章長度：800-2000 字
- 語言：繁體中文（香港用語）

---

## 🔧 部署

Push 到 `main` → 同時 push 到 `gh-pages`（GitHub Pages source branch）：

```bash
git add -A
git commit -m "描述"
git push origin main
git push origin main:gh-pages
```

---

## 📱 聯絡

- Instagram: [@unitary.hk](https://instagram.com/unitary.hk)
- Cults3D: [UNITARY Store](https://cults3d.com/)

---

© 2026 UNITARY. Design once. Print & play forever.
