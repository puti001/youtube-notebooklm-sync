import os
import sys
import io
from notebooklm_tools.cli.utils import get_client

# 修正 Windows 控制台輸出編碼
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

notebook_id = "343fffa5-573f-4d1f-9281-a612abe756df"
target_dir = r"c:\antigravity\tools工具庫\notebooklm\知識庫\NotebookLM_講義"

try:
    client = get_client()
    print("NotebookLM Client initialized successfully.")

    # 1. 取得所有本地的大綱檔案 (簡報大綱-*.md)
    outline_files = [f for f in os.listdir(target_dir) if f.startswith("簡報大綱-") and f.endswith(".md")]
    if not outline_files:
        print("No '簡報大綱-*.md' files found.")
        sys.exit(0)

    # 2. 獲取現有來源
    sources = client.get_notebook_sources_with_types(notebook_id)
    
    # 3. 刪除所有舊的 "_簡報大綱" 結尾的來源 (防呆備援)
    print("Checking for old '_簡報大綱' prefixed/suffixed sources to delete...")
    if sources:
        for s in sources:
            title = s['title']
            if title.endswith("_簡報大綱"):
                print(f" -> Deleting obsolete source: {title} (ID: {s['id']})")
                try:
                    client.delete_source(s['id'])
                except Exception:
                    pass
                
    # 4. 上傳新的 "簡報大綱-[影片標題]" (如果已有同名的，先刪除，以強制覆蓋上傳最新內容)
    print(f"\nFound {len(outline_files)} outline files to upload.")
    for idx, filename in enumerate(outline_files, 1):
        title = filename.replace(".md", "")
        path = os.path.join(target_dir, filename)
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 再次拉取最新 sources 列表以獲取最新的 ID
        sources = client.get_notebook_sources_with_types(notebook_id)
        if sources:
            for s in sources:
                if s['title'].strip() == title.strip():
                    print(f" -> Deleting existing source to override: {title} (ID: {s['id']})")
                    try:
                        client.delete_source(s['id'])
                    except Exception:
                        pass
                    break

        print(f"[{idx}/{len(outline_files)}] Uploading: {title} ...")
        res = client.add_text_source(notebook_id, text=content, title=title, wait=True)
        if res and 'id' in res:
            print(f"  Successfully uploaded. ID: {res['id']}")
        else:
            print(f"  Failed to upload {title}")

    print("\nAll outlines updated and uploaded successfully! No slide generation triggered.")
except Exception as e:
    print(f"Error: {e}")
