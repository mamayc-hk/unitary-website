# UNITARY 網站

香港原創桌遊配件品牌官方網站

## 📁 文件結構

```
website/
├── index.html      # 首頁
├── products.html   # 產品頁
├── devlog.html     # 開發日誌
├── preorder.html   # 預售登記
├── about.html      # 關於我們
├── style.css       # 樣式文件
└── README.md       # 說明文件
```

## 🚀 部署到 GitHub Pages

### Step 1：創建 GitHub Repository

1. 登入 GitHub
2. 點擊「New repository」
3. Repository name: `unitary-hk` (或其他名稱)
4. 選擇 Public
5. 點擊「Create repository」

### Step 2：上傳文件

**方法 A：網頁界面**

1. 在 repository 頁面點擊「uploading an existing file」
2. 將所有文件拖曳上傳
3. 點擊「Commit changes」

**方法 B：Git 命令**

```bash
cd /Users/herryma/Documents/unitary/網站/website
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/unitary-hk.git
git push -u origin main
```

### Step 3：啟用 GitHub Pages

1. 進入 repository 設定（Settings）
2. 左側選單點擊「Pages」
3. Source 選擇「Deploy from a branch」
4. Branch 選擇「main」
5. Folder 選擇「/ (root)」
6. 點擊「Save」

### Step 4：等待部署

- 通常 1-3 分鐘
- 網址會是：`https://YOUR_USERNAME.github.io/unitary-hk/`

---

## 🎨 自定義域名（可選）

### 使用自定義域名

1. 在 GitHub Pages 設定中輸入你的域名
2. 在域名提供商設定 DNS：

```
CNAME record: YOUR_USERNAME.github.io
```

---

## 📝 需要更新的內容

### 產品照片
- 在 `products.html` 中替換產品照片
- 建議尺寸：1200px × 800px
- 格式：JPG 或 PNG

### Google Form
- 創建 Google Form（參考 `preorder.html` 中的問題）
- 複製嵌入代碼
- 替換 `preorder.html` 中的 `<div class="form-placeholder">` 區域

### 聯絡資訊
- 更新 Email 地址（目前是 `enquiries@unitary.hk`）

---

## 🔧 本地預覽

直接在瀏覽器打開 `index.html` 文件即可預覽。

或使用本地伺服器：

```bash
cd /Users/herryma/Documents/unitary/網站/website
python -m http.server 8000
```

然後瀏覽器打開：`http://localhost:8000`

---

## 📱 響應式設計

網站已支援：
- 桌面版
- 平板版
- 手機版

---

## 🎯 SEO 優化

已包含：
- Meta description
- 標題標籤
- 語義化 HTML

---

## 📄 License

© 2026 UNITARY. All rights reserved.
