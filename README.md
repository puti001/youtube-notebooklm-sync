# YouTube Channel Sync & Slide Outline Generator

一個自動化 YouTube 頻道影片同步、逐字稿本地清洗、以及 IP 同台互動風格簡報大綱的完整工作流。

---

## 🌟 核心特色
1. **本機極速字幕下載優先**：預設利用 `yt-dlp` 下載影片的 `zh-TW` 字幕，在 1 秒內完成本機文字清洗去重，不需等待雲端語音轉譯。
2. **NotebookLM 雲端轉譯備援 (Fallback)**：若影片完全無字幕，自動將影片 URL 上傳至 NotebookLM 筆記本進行語音轉譯。
3. **中文一體化生圖大綱生成**：提供 SOP Prompt，將逐字稿轉換為正好 15 頁、內建 Puti 老師與 GiGi 機器人同台互動分鏡、以及極簡手繪塗鴉生圖提示詞的 Markdown 大綱。
4. **雙端命名 100% 一致**：
   - 操作講義：`[影片標題].md`
   - 簡報大綱：`簡報大綱-[影片標題].md`
   - 上傳至 NotebookLM 的標題完全相同，無 YAML Frontmatter，方便排版。
5. **獨立大綱上傳覆寫**：提供 `upload_outlines.py`，支援自動清理舊版 `_簡報大綱` 來源，並覆蓋上傳最新風格大綱 Note。

---

## 🛠️ 環境需求與安裝

### 1. 安裝 Python 套件
```bash
pip install -r requirements.txt
```

### 2. 安裝 NotebookLM 命令行工具 (nlm)
請確保本機已安裝 NotebookLM 官方 CLI 工具並完成登入：
```bash
pip install notebooklm-tools
nlm login
```

---

## 🚀 核心腳本使用指南

### 1. 影片同步與逐字稿提取 (`youtube_channel_sync.py`)
```bash
python youtube_channel_sync.py --channel-url "<CHANNEL_URL>" --notebook-id "<NOTEBOOK_ID>" --start-date "<YYYY-MM-DD>"
```
* **功能**：自動檢查指定日期後上傳的最新影片，優先下載本機字幕；無字幕時自動上傳 NotebookLM 轉譯，最終將逐字稿 text 檔儲存至 `youtube_transcripts/` 中。

### 2. Style 簡報大綱上傳 (`upload_outlines.py`)
```bash
python upload_outlines.py
```
* **功能**：掃描本地知識庫中開頭為 `簡報大綱-` 的檔案，自動清理雲端筆記本中結尾為 `_簡報大綱` 的舊來源，並覆蓋上傳最新的中文生圖大綱 Note。

---

## 🤖 AI Agent 簡報大綱生成 SOP Prompt

將提取出的講義/逐字稿轉換為 15 頁大綱時，請直接使用以下 Prompt 餵給 AI Agent（如 Antigravity / OpenCode）：

```markdown
【角色設定】你是一位專業的「AI 簡報視覺設計專家（雙 IP 分鏡大師）」。你的任務是讀取這份講義，將其轉換為一份「正好 15 頁投影片」的簡報大綱 Markdown 檔案。

【視覺風格基調】極簡手繪塗鴉風格的資訊圖表概念圖，純白背景，乾淨的黑色線稿，手繪簡報外框，使用柔和的「藍色」和「橘色」進行局部點綴，重點部分放大。
- Puti 老師：戴眼鏡、穿印有 Puti 的黑色短袖 T 恤的男老師。
- GiGi 機器人：穿有 Puti-AI 與 GiGi 字樣、面罩型螢幕大眼睛的可愛小機器人。
- 核心要求：拒絕孤立輪流出現！Puti 老師與 GiGi 機器人必須在每頁的畫面中「同台出現並互動」（如一起指大螢幕、一起扛大道具、Puti用起子設定GiGi等）。

【單頁大綱格式規範】每頁投影片必須包含以下欄位，且每頁之間使用 `---` 分隔。不要包含任何 YAML Frontmatter。

## **第 X 頁 — [簡短頁標題]**

**標題：** [簡報標題]
**副標：** [簡報副標] （僅封面頁需要）

**文案（要點式）：**
- [重點操作步驟/軟體路徑，確保讀者看懂如何操作]
- [講師經典金句，加粗]
- [地雷與警告，使用 > [!IMPORTANT] 格式]

**生圖提示詞：**
極簡手繪塗鴉風格，手繪簡報外框，純白背景，黑色線稿。Puti老師與GiGi機器人同台出現，[詳細描述Puti老師與GiGi機器人在畫面中如何彼此互動，如何與軟體畫面、按鈕、符號或巨型工具進行動態連結的中文細節]。使用柔和藍色和橘色局部點綴。乾淨排版，預留標題與文案文字空間。
```

---

## ⚠️ 開發踩坑與解決之道 (Troubleshooting & Tips)

### 1. NotebookLM API 參數順序陷阱
* **問題**：`add_text_source` 的底層 Method 定義為 `(notebook_id, text, title)`（內容在前，標題在後）。若傳反，會把整篇講義內容當作標題，網頁端內容顯示為空。
* **解決**：在呼叫 API 時，一律強制使用具名參數（Keyword Arguments）：
  ```python
  client.add_text_source(notebook_id, text=content, title=title, wait=True)
  ```

### 2. nlm CLI 憑證 (Cookie) 儲存路徑
* **問題**：`notebooklm-tools` 載入憑證的真實路徑為 `C:\Users\<Username>\.notebooklm-mcp-cli\profiles\default\cookies.json`。直接寫入 Python site-packages 目錄將無任何效果。
* **解決**：使用庫中內建的 `AuthManager` 進行寫入：
  ```python
  from notebooklm_tools.core.auth import AuthManager
  manager = AuthManager('default')
  manager.save_profile(cookies, force=True)
  ```

### 3. gh 認證被過期環境變數卡死
* **問題**：如果終端機 session 中存在一個過期的環境變數 `GITHUB_TOKEN`，`gh` 工具會報錯，忽視本地已登入的認證。
* **解決**：執行前先手動清除該變數（PowerShell：`Remove-Item Env:\GITHUB_TOKEN`）。

### 4. nlm login 無法彈出瀏覽器授權視窗 (救磚方案)
* **問題**：在某些系統環境或權限限制下，執行 `nlm login` 可能會卡死，完全無法順利彈出 Google Chrome 登入授權視窗。
* **解決**：手動至瀏覽器登入 NotebookLM，使用擴充套件（如 EditThisCookie、Get Cookies.txt）匯出該網頁的所有 Cookies JSON 格式，然後透過 Python 強制寫入：
  ```python
  import json
  from notebooklm_tools.core.auth import AuthManager
  
  with open("your_exported_cookies.json", "r", encoding="utf-8") as f:
      cookies = json.load(f)
      
  manager = AuthManager('default')
  manager.save_profile(cookies, force=True)
  ```
