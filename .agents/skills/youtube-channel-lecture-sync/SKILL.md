---
name: youtube-channel-lecture-sync
description: 自動從指定的 YouTube 頻道抓取最新影片，上傳至 Google NotebookLM 轉譯，並將逐字稿整理成「操作說明書等級」的詳細講義。
---

# 技能：YouTube 頻道同步與講義自動生成

本技能會引導 Agent 抓取指定 YouTube 頻道在特定天數內（例如：最近 7 天）或特定數量的新影片，自動與 NotebookLM 進行同步（無字幕的影片將自動上傳並轉譯），下載逐字稿，最後以【課程技術紀錄官】的規格轉換成操作講義並存入 Obsidian。

## 執行流程 (SOP)

### 1. 釐清參數
當使用者觸發此技能時，請先確定或向使用者確認以下參數（若使用者未指定，請詢問）：
- **頻道網址 (Channel URL)**：例如 `https://www.youtube.com/@GoogleDeepMind/videos`。
- **NotebookLM 筆記本 ID**：例如 `38be6902-b467-454a-8361-2f03d83690a7`。
- **時間範圍 (天數)**：預設為 `7` 天（僅抓取最近 7 天內的影片）。若要不限天數，請設為 `0`。
- **影片長度**：預設最少為 `600` 秒 (10分鐘)（選填）。
- **最大處理數**：預設最多為 `5` 部影片。

### 2. 執行同步腳本
使用 `run_command` 執行 `youtube_channel_sync.py` 進行同步與轉譯下載：
```powershell
python c:/antigravity/tools工具庫/notebooklm/youtube_channel_sync.py --channel-url "<CHANNEL_URL>" --notebook-id "<NOTEBOOK_ID>" --days <DAYS> --max-results <MAX_RESULTS> --min-duration <MIN_DURATION> --output-dir "c:/antigravity/tools工具庫/notebooklm/youtube_transcripts"
```

### 3. 解析同步結果
同步腳本完成後，讀取生成的結果檔：
`c:/antigravity/tools工具庫/notebooklm/youtube_transcripts/channel_sync_results.json`

將同步的影片清單以表格形式呈現給使用者，若無符合條件的新影片，請告知使用者並結束流程。

### 4. 讀取逐字稿並轉換成講義
對於清單中的每一部影片：
1. 讀取 `transcript_file` 對應的逐字稿檔案。
2. 套用以下**【課程技術紀錄官】**的核心轉換提示詞，將其轉換成詳細的「操作說明書」講義：

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

### 5. 儲存與同步

1. **寫入本機 Obsidian 知識庫**：
   - 講義檔名**必須與原影片的標題一模一樣**，只需過濾 Windows 不合法字元 `\/:*?"<>|`，**絕不能加任何前綴（如 NotebookLM_講義_）或進行截斷**。
   - 寫入路徑：`c:/antigravity/tools工具庫/notebooklm/知識庫/NotebookLM_講義/<過濾後影片標題>.md`
2. **同步至 NotebookLM 筆記本**：
   - 呼叫 `nlm add text <NOTEBOOK_ID> "<講義內文>"`，使用正確的 keyword arguments（`text` 為講義內容，`title` 為原影片標題，不加 any 前綴）。
3. **回報結果**：
   - 顯示成功產出的講義清單與本機 [file:///...] 連結。
