---
name: youtube-notebooklm-lecture
description: 搜尋 YouTube 影片（支援自訂主題、日期範圍、語言、影片長度），可選本機下載字幕或 NotebookLM 自動語音轉譯模式，並將其逐字稿轉化為「操作說明書等級」的詳細講義。
---

# 技能：YouTube 影片轉文本講義 (通用版)

本技能會引導 Agent 搜尋 YouTube 上符合指定主題、日期範圍、語言與影片長度限制 the 影片，下載並整理其逐字稿（可選本地字幕模式或 NotebookLM 多模態語音轉譯模式），最後以「課程技術紀錄官」的最高規格標準，將逐字稿轉化為一份「操作說明書等級」的詳細講義。

## 執行流程 (SOP)

### 1. 釐清搜尋參數
當使用者要求執行本技能時，請先確定或向使用者詢問以下參數：
- **主題 (Query)**：例如 `notebooklm`、`chatgpt`、`canva`（必填）。
- **日期範圍**：例如 `2026-01-01` 至 `2026-06-26`（選填，格式 YYYY-MM-DD）。
- **影片長度**：預設為 `900` 秒 (15分鐘) 以上（選填，可自訂為 30 分鐘等）。
- **影片語言**：預設為 `zh` (中文)，可選 `en` (英文) 或 `all` (不限)。
- **轉譯模式與筆記本 ID**：
  - **Local 字幕下載模式** (預設)：若目標影片本身在 YouTube 上已具有繁簡中文字幕，直接執行此模式。
  - **NotebookLM 語音轉譯模式**：若目標影片在 YouTube 上無字幕，可傳入 Google NotebookLM 的筆記本 ID（例如 `38be6902-b467-454a-8361-2f03d83690a7`），腳本將自動上傳影片至該筆記本並等待 Google 語音模型完成高品質轉譯。

### 2. 執行搜尋與字幕下載
在當前工作目錄下，建立一個名為 `youtube_transcripts` 的資料夾。
使用 `run_command` 執行以下指令（根據參數進行填寫）：

#### 互動式引導模式
```powershell
python C:/Users/clong/.gemini/config/skills/youtube-notebooklm-lecture/scripts/youtube_search.py --output-dir "youtube_transcripts"
```

#### 範例 A：Local 字幕下載模式 (主題為 Canva，大於 15 分鐘，中文影片)
```powershell
python C:/Users/clong/.gemini/config/skills/youtube-notebooklm-lecture/scripts/youtube_search.py --query "canva" --min-duration 900 --lang "zh" --output-dir "youtube_transcripts"
```

#### 範例 B：NotebookLM 語音轉譯模式 (主題為 ChatGPT，2026年影片，大於 30 分鐘，自動上傳筆記本)
```powershell
python C:/Users/clong/.gemini/config/skills/youtube-notebooklm-lecture/scripts/youtube_search.py --query "chatgpt" --start-date "2026-01-01" --min-duration 1800 --lang "zh" --notebook-id "38be6902-b467-454a-8361-2f03d83690a7" --output-dir "youtube_transcripts"
```

### 3. 讀取並展示結果
搜尋與轉譯完成後，讀取生成的 `youtube_transcripts/search_results.json` 檔案。
將搜尋到並成功取得逐字稿的影片清單以表格形式呈現給使用者，欄位包括：
- 上傳日期
- 影片標題
- 影片長度（分鐘）
- 影片連結 (URL)

若有多部影片，請詢問使用者想要處理哪幾部影片；若使用者同意全部處理，請直接進行下一步。

### 4. 讀取逐字稿並套用提示詞轉換
讀取該影片對應的逐字稿純文字檔案（檔案路徑已記錄在 JSON 中的 `transcript_file` 屬性）。
使用以下**【課程技術紀錄官】**的核心指令，將其轉換成文本講義：

---

### 📋 【課程技術紀錄官】轉換提示詞 (Core Prompt)

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

---

### 5. 儲存與呈現講義
1. 將產出的 Markdown 講義檔案，使用 Obsidian MCP 寫入至 Obsidian 知識庫中，路徑格式為 `知識庫/NotebookLM_講義/<大分類>/NotebookLM_講義_<影片標題(簡化)>.md`。
2. 在對話中回報儲存路徑，並將講義的精華結構呈現給使用者。
