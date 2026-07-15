# YouTube Channel Sync & Slide Generator

一個自動化 YouTube 頻道影片同步、逐字稿本地清洗、以及 IP 同台互動風格簡報的完整工作流。

---

## 🌟 核心特色
1. **本機極速字幕下載優先**：預設利用 `yt-dlp` 下載影片的 `zh-TW` 字幕，在 1 秒內完成本機文字清洗去重，不需等待雲端語音轉譯。
2. **NotebookLM 雲端轉譯備援 (Fallback)**：若影片無字幕，自動將影片 URL 上傳至 NotebookLM 筆記本進行語音轉譯。
3. **本機離線 Whisper 聽寫防線 (Ultimate Fallback)**：若 YouTube 字幕下載與 NotebookLM 雲端轉譯皆失效/額度用盡，自動下載影片音訊並動態呼叫本機 `faster-whisper` 或 `openai-whisper` 模型進行精準語音聽寫，完成完全本機自給自足的逐字稿生成。
4. **直出簡報生成**：直接使用操作講義配合風格與人物設定圖片生成簡報，無須額外生成大綱，流程最簡化、生成成功率更高。
5. **命名 100% 一致**：
   - 操作講義：`[影片標題].md`
   - 上傳至 NotebookLM 的標題與影片完全一致，無 YAML Frontmatter，方便排版。

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
* **功能**：自動檢查指定日期後上傳的最新影片，並做兩件事：
  1. **上傳影片 URL 至 NotebookLM 筆記本**（作為永久參考來源，已存在則略過）
  2. **本機字幕優先下載**（`yt-dlp`，1 秒內完成）；無字幕時自動 fallback 至 NotebookLM 雲端語音轉譯。

### 2. 操作講義上傳 (`upload_lectures.py`)
```bash
python upload_lectures.py
```
* **功能**：掃描本地知識庫中的操作講義 `.md` 檔（不含 `簡報大綱-` 前綴），上傳至 NotebookLM 筆記本供日後快速閱讀，取代重看影片。
* **去重**：同名來源已存在則自動略過；加上 `--overwrite` 參數可強制覆蓋重新上傳。

### 3. 批次觸發簡報生成 (`generate_slides.py`)
```bash
python generate_slides.py
```
* **功能**：以每 3 分鐘為間隔，依序觸發 NotebookLM Studio 為各個講義自動生成簡報 (Slide Deck)。
* **來源組合**：每個簡報由四個來源組合觸發——`操作講義 Note` + `GiGi 機器人設定圖` + `Puti 老師設定圖` + `Q版黑白手繪塗鴉風格設定圖`。
* **設定方式**：直接編輯腳本頂部的四個設定區塊（`NOTEBOOK_ID`、`IP_SOURCE_IDS`、`JOBS`、`INTERVAL_SECONDS`）即可。
* **取得 Source ID**：執行 `upload_lectures.py` 上傳講義後，從終端機輸出中複製各來源的 `Source ID`。

> [!TIP]
> 每個 Slide Deck 的生成約需 2～5 分鐘不等，3 分鐘的間隔設計可避免被 NotebookLM 的後台速率限制卡死。


---

## 🤖 AI Agent 完整工作流 SOP

### Step 1 → 逐字稿（`youtube_channel_sync.py` 自動完成）

### Step 2 → 操作講義 SOP Prompt

將逐字稿轉換為操作講義時，把以下 Prompt + 逐字稿內容一起餵給 AI Agent：

```markdown
【角色設定】 你是一位專業的「課程技術紀錄官」。你的任務是將這份逐字稿轉化為**「操作說明書等級」**的詳細紀實。你必須確保讀者看完這份紀錄後，不需要看影片也能操作文中提到的軟體。
【核心原則：拒絕摘要】


細節極大化：請保留所有教學步驟，包括「點擊哪顆按鈕」、「在哪個選單」、「設定什麼參數」。
情境重現：保留講師與同學的互動細節（如：現場笑聲、對同學疑問的即時解答）。
專業術語準確性：準確記錄軟體名稱（如：Gemini, NotebookLM, Canva, HankMD...）與功能術語。
【結構化規範】


標題：依據教學進度使用 ## 標題。
操作清單：使用有序列表（1, 2, 3）詳細描述軟體操作流程。
重要叮嚀：講師提到的「地雷」或 關鍵、訣竅、秘訣...，請獨立成 > [!IMPORTANT] 區塊。
金句與幽默：使用 粗體 或引用。

【逐字稿內容如下】
（貼上逐字稿）
```


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
