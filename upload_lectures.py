"""
upload_lectures.py
==================
將本地操作講義 (.md) 上傳至 NotebookLM 筆記本作為文字來源。

掃描規則：
  - 目標目錄：LECTURES_DIR（預設為知識庫/NotebookLM_講義/）
  - 上傳條件：.md 檔案，且不以「簡報大綱-」開頭（排除大綱，只上傳講義）
  - 去重邏輯：若同名來源已存在於筆記本中，自動略過（不覆蓋）

使用方式：
  python upload_lectures.py

若需強制覆蓋重新上傳：
  python upload_lectures.py --overwrite
"""

import os
import sys
import io
import argparse

# 修正 Windows 控制台輸出編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

from notebooklm_tools.cli.utils import get_client

# ============================================================
# 設定區塊
# ============================================================
NOTEBOOK_ID  = "343fffa5-573f-4d1f-9281-a612abe756df"
LECTURES_DIR = r"c:\antigravity\tools工具庫\notebooklm\知識庫\NotebookLM_講義"

# ============================================================
# 執行
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="上傳操作講義至 NotebookLM")
    parser.add_argument("--overwrite", action="store_true", help="強制覆蓋已存在的同名來源")
    parser.add_argument("--notebook-id", type=str, default=NOTEBOOK_ID, help="NotebookLM 筆記本 ID")
    parser.add_argument("--lectures-dir", type=str, default=LECTURES_DIR, help="講義資料夾路徑")
    args = parser.parse_args()

    if not os.path.isdir(args.lectures_dir):
        print(f"[ERROR] 講義目錄不存在: {args.lectures_dir}")
        sys.exit(1)

    # 掃描所有 .md 講義檔（排除簡報大綱-開頭）
    lecture_files = sorted([
        f for f in os.listdir(args.lectures_dir)
        if f.endswith(".md") and not f.startswith("簡報大綱-")
    ])

    if not lecture_files:
        print("找不到任何操作講義 .md 檔案。")
        sys.exit(0)

    client = get_client()
    print(f"NotebookLM Client 初始化成功。")

    # 取得筆記本現有來源
    sources = client.get_notebook_sources_with_types(args.notebook_id)
    existing_titles = {s["title"].strip() for s in sources} if sources else set()

    print(f"\n找到 {len(lecture_files)} 篇操作講義，開始上傳...\n")
    success, skip, fail = 0, 0, 0

    for idx, filename in enumerate(lecture_files, 1):
        title = filename.replace(".md", "")
        path  = os.path.join(args.lectures_dir, filename)

        # 去重或覆蓋邏輯
        if title in existing_titles:
            if not args.overwrite:
                print(f"[{idx}/{len(lecture_files)}] Skip (已存在): {title}")
                skip += 1
                continue
            else:
                # 找到舊來源 ID 並刪除
                for s in sources:
                    if s["title"].strip() == title:
                        print(f"[{idx}/{len(lecture_files)}] 刪除舊版來源: {title} (ID: {s['id']})")
                        try:
                            client.delete_source(s["id"])
                        except Exception as e:
                            print(f"  [!] 刪除失敗: {e}")
                        break

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"[{idx}/{len(lecture_files)}] 上傳中: {title} ...")
        try:
            res = client.add_text_source(args.notebook_id, text=content, title=title, wait=True)
            if res and "id" in res:
                print(f"  -> 成功！Source ID: {res['id']}")
                success += 1
            else:
                print(f"  -> [!] 回傳結果異常，請至 NLM 網頁確認")
                fail += 1
        except Exception as e:
            print(f"  -> [ERROR] {e}")
            fail += 1

    print(f"\n=== 上傳完成 ===")
    print(f"  成功: {success}  略過: {skip}  失敗: {fail}")

if __name__ == "__main__":
    main()
