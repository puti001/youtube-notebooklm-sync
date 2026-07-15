"""
generate_slides.py
==================
批次觸發 NotebookLM Studio 生成簡報 (Slide Deck)。

使用方式：
  1. 編輯下方 NOTEBOOK_ID, IP_SOURCE_IDS, JOBS 三個設定區塊
  2. 執行: python generate_slides.py

# 每個 Job 的來源組合：
#   - 操作講義 Note (操作步驟說明)
#   - GiGi 機器人設定圖   (IP 角色參考)
#   - Puti 老師設定圖      (IP 角色參考)
#   - Q版黑白手繪塗鴉風格設定圖 (視覺風格參考)

間隔設定：每個簡報之間預設等待 3 分鐘（INTERVAL_SECONDS = 180），
避免被 NotebookLM 後台速率限制卡死。

取得 Source ID 方式：
  python upload_outlines.py   <-- 上傳大綱並顯示 ID
  (或在 NotebookLM 來源列表中查看每個來源的 URL 末段)
"""

import sys
import io
import time

# 修正 Windows 控制台輸出編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

from notebooklm_tools.cli.utils import get_client

# ============================================================
# 設定區塊 1：筆記本 ID
# ============================================================
NOTEBOOK_ID = "343fffa5-573f-4d1f-9281-a612abe756df"

# ============================================================
# 設定區塊 2：共用 IP 風格來源 ID
# 這三個 ID 是上傳至筆記本的圖片來源，每次生成都會帶入
# ============================================================
GIGI_ID  = "3c090b83-38d8-4622-a4f8-0d911581afff"  # GiGi 機器人設定圖
PUTI_ID  = "893e5c8e-5cf3-45c1-bae0-861e445851a9"  # Puti 老師設定圖
FRAME_ID = "8ecaa418-fc5e-4e4e-a303-fdec9b8f016d"  # Q版黑白手繪塗鴉風格設定圖

# ============================================================
# 設定區塊 3：待生成的簡報列表
# 格式：("顯示名稱",  "操作講義 Note 的 Source ID")
# ============================================================
JOBS = [
    ("AI Agent基本功 EP05 三層", "8b71fd4c-a63f-4483-b456-efa6390894c7"),
    ("AI Agent 台語教材",        "f4e24149-5447-4c01-a666-c2fcd7065749"),
    ("ChatGPT APP EP06",         "b227fb6f-76c8-4b05-96a8-5d65d9003d8f"),
    ("GPT Codex EP05",           "7b79cd51-3d89-416a-8714-64b0bfc3eb80"),
    ("OpenCode EP05 Big Pickle", "2e119c0d-db61-463b-8e8c-d432fa259139"),
]

# ============================================================
# 設定區塊 4：間隔秒數
# ============================================================
INTERVAL_SECONDS = 180  # 每 3 分鐘啟動一個

# ============================================================
# 執行
# ============================================================
client = get_client()
print(f"=== 批次簡報生成任務啟動 ({len(JOBS)} 個) ===")
print(f"每個間隔: {INTERVAL_SECONDS // 60} 分鐘")
print(f"等待 {INTERVAL_SECONDS // 60} 分鐘後啟動第一個...\n")
time.sleep(INTERVAL_SECONDS)

for i, (name, lecture_id) in enumerate(JOBS, 1):
    source_ids = [lecture_id, GIGI_ID, PUTI_ID, FRAME_ID]

    print(f"[{i}/{len(JOBS)}] 正在啟動: {name}")
    try:
        result = client.create_slide_deck(
            notebook_id=NOTEBOOK_ID,
            source_ids=source_ids,
            format_code=1,    # 1 = DETAILED (詳細格式)
            length_code=3,    # 3 = DEFAULT  (預設長度)
            language="zh-TW", # 繁體中文輸出
            focus_prompt="",
        )
        if result:
            print(f"  -> 成功！Artifact ID: {result.get('artifact_id')}")
            print(f"     Status: {result.get('status')}")
        else:
            print(f"  -> [!] 回傳結果為空，請手動至 Studio 確認")
    except Exception as e:
        print(f"  -> [ERROR] {e}")

    if i < len(JOBS):
        print(f"  等待 {INTERVAL_SECONDS // 60} 分鐘後啟動下一個...\n")
        time.sleep(INTERVAL_SECONDS)

print("\n=== 所有批次簡報生成任務已全部啟動完成！ ===")
print("請至 NotebookLM Studio 面板查看生成進度。")
