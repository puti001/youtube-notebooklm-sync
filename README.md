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
3. Agent 會自動執行 `youtube_channel_sync.py` 獲取逐字稿，然後：
   - 轉換生成「操作講義」：存為 `[影片標題].md`
   - 轉換生成「15頁簡報大綱」：存為 `簡報大綱-[影片標題].md`（使用 `簡報大綱-` 前綴方便在資料夾中歸類）。
   - 將講義與簡報大綱同步上傳至你的 NotebookLM 筆記本中當作 Note 來源。

---

## ⚠️ 開發踩坑與解決之道 (Troubleshooting & Tips)

當其他 Agent 或開發者維護此專案時，請特別注意以下在開發過程中踩過的坑與其對應的解決方案：

### 1. NotebookLM API 參數順序陷阱
* **問題**：`add_text_source` 的底層 Method 定義為 `(notebook_id, text, title)`（內容在前，標題在後），而非直覺的 `(notebook_id, title, content)`。若不慎傳反，會導致整篇講義內容被當作標題，上傳後網頁端內容顯示為空。
* **解決**：在呼叫 API 時，一律強制使用具名參數（Keyword Arguments），以防順序混淆：
  ```python
  client.add_text_source(notebook_id, text=content, title=title, wait=True)
  ```

### 2. nlm CLI 憑證 (Cookie) 儲存路徑
* **問題**：`notebooklm-tools` 與 `nlm` CLI 工具載入憑證的真實路徑為：
  `C:\Users\<Username>\.notebooklm-mcp-cli\profiles\default\cookies.json`
  而非 Python 庫 site-packages 目錄下。若要以程式碼手動更新或匯入 Google Cookie，直接寫入庫目錄將無任何效果。
* **解決**：應使用庫中內建的 `AuthManager` 來進行安全的 Profile 寫入，它會自動建立設定檔並重設 metadata：
  ```python
  from notebooklm_tools.core.auth import AuthManager
  manager = AuthManager('default')
  manager.save_profile(cookies, force=True)
  ```

### 3. GitHub CLI (gh) 認證被無效環境變數卡死
* **問題**：如果當前終端機 session 中存在一個過期或無效的環境變數 `GITHUB_TOKEN`，`gh` 工具會優先讀取它而報錯 `The token in GITHUB_TOKEN is invalid`，即使你本機已經透過 `gh auth login` 登入過也無效。
* **解決**：在執行 `gh repo create` 或 `gh auth status` 之前，先於環境中手動清除該變數（例如在 PowerShell 下執行 `Remove-Item Env:\GITHUB_TOKEN`）。

### 4. 影片無法匯入或 NotebookLM 轉譯暫時性失敗
* **問題**：有些 YouTube 影片上傳至 NotebookLM 雲端時，會因為轉譯逾時或版權問題，導致 API 下載逐字稿時返回 `NOT_FOUND` 或來源為空白。
* **解決**：實作「本地字幕下載優先」機制。使用 `yt-dlp` 下載 `zh-TW` 的 VTT 字幕，並利用 Python 進行重複字幕段落與時間戳清洗，大約 1 秒內即可完成；只有在影片完全沒有字幕時，才 fallback 採用 NotebookLM 語音轉譯。

### 5. nlm login 無法彈出瀏覽器授權視窗 (救磚方案)
* **問題**：在某些系統環境、虛擬主機或權限限制下，執行 `nlm login` 可能會卡死，完全無法順利彈出 Google Chrome 登入授權視窗。
* **解決**：可以手動至瀏覽器打開 NotebookLM 並登入 Google 帳號，使用瀏覽器擴充套件（如 EditThisCookie、Get Cookies.txt）匯出該網頁的所有 Cookies JSON 格式，然後透過以下 Python 程式直接寫入憑證設定檔，即可成功強行登入：
  ```python
  import json
  from notebooklm_tools.core.auth import AuthManager
  
  # 載入從瀏覽器擴充套件匯出的 cookie json
  with open("your_exported_cookies.json", "r", encoding="utf-8") as f:
      cookies = json.load(f)
      
  # 強制寫入 nlm 的 default profile 中
  manager = AuthManager('default')
  manager.save_profile(cookies, force=True)
  print("強行登入成功！")
  ```

