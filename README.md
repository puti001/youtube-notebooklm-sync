# YouTube Channel Sync & Lecture Generator

一個自動化 YouTube 頻道影片同步與操作講義生成工作流。

## 🌟 核心特色
1. **本機極速字幕下載優先**：預設利用 `yt-dlp` 下載影片的 `zh-TW` 高清字幕，在 1 秒內完成下載與本機文字清洗去重，極速產出逐字稿，不需等待雲端語音轉譯。
2. **NotebookLM 雲端轉譯備援 (Fallback)**：若 YouTube 影片完全無字幕，則會自動將影片 URL 上傳至 NotebookLM 筆記本進行後台語音轉譯，轉譯完成後再行下載逐字稿。
3. **【課程技術紀錄官】講義生成**：搭配 AI Agent 將逐字稿轉換成「拒絕摘要、細節極大化、還原現場互動」的超詳細操作說明書。
4. **雙端同步**：講義檔案自動儲存於本機 Obsidian 知識庫中（檔名與影片標題 100% 一致），並自動將乾淨無 Frontmatter 的講義內容上傳至 NotebookLM 筆記本當作文字來源。
5. **動態版權標記**：自動從影片 Metadata 取得上傳者 (Uploader) 與影片網址，動態加在講義結尾，避免版權混淆。

---

## 🛠️ 環境需求與安裝

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 安裝 NotebookLM 命令行工具 (nlm)
請確保本機已安裝 NotebookLM 官方 CLI 工具：
```bash
pip install notebooklm-tools
```
安裝完畢後，執行登入以取得授權：
```bash
nlm login
```

---

## 🚀 執行同步腳本

```bash
python youtube_channel_sync.py --channel-url "<CHANNEL_URL>" --notebook-id "<NOTEBOOK_ID>" --start-date "<YYYY-MM-DD>"
```

### 參數說明：
- `--channel-url`：YouTube 頻道的 videos 網址（例如：`https://www.youtube.com/@sensebar/videos`）。
- `--notebook-id`：Google NotebookLM 筆記本的 ID。
- `--start-date`：只同步此日期之後的影片，格式為 `YYYY-MM-DD`（例如：`2026-06-28`）。
- `--days`：（選填）同步最近幾天內的影片。
- `--max-results`：（選填）每次最多處理影片數（預設 10 部）。
- `--min-duration`：（選填）最低影片片長限制（預設 600 秒）。
- `--output-dir`：（選填）逐字稿本機儲存目錄。

---

## 🤖 搭配 AI Agent 執行 SOP
若你使用 `Antigravity`、`OpenCode` 或其他支援 Agent，可直接在對話中啟用本工作流：
1. 輸入觸發詞：**`同步頻道講義`**。
2. 提供頻道 URL、筆記本 ID、日期範圍。
3. Agent 會自動執行 `youtube_channel_sync.py` 獲取逐字稿，然後自動套用【課程技術紀錄官】Prompt 進行講義轉換，並同步寫入本地 Obsidian 與 NotebookLM 筆記本中。
