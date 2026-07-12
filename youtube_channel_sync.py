import os
import sys
import json
import re
import argparse
import subprocess
from datetime import datetime, timedelta
import yt_dlp

# 解決 Windows 控制台輸出編碼問題
import io
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

def parse_date(date_str):
    if not date_str:
        return None
    date_str = date_str.replace('-', '')
    try:
        return datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        print(f"Error: 錯誤的時間格式 '{date_str}'。請使用 YYYY-MM-DD。")
        sys.exit(1)

def get_existing_notebook_sources(notebook_id, nlm_path):
    cmd = [nlm_path, "list", "sources", notebook_id]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    try:
        stdout = res.stdout.strip()
        start = stdout.find('[')
        end = stdout.rfind(']') + 1
        if start != -1 and end != -1:
            return json.loads(stdout[start:end])
    except Exception:
        pass
    return []

def get_channel_videos(channel_url, cutoff_date, max_results, min_duration):
    print(f"正在從頻道抓取影片資訊: {channel_url} ...")
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'playlistend': max_results * 5,  # 多抓一些候選影片
    }
    
    raw_entries = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(channel_url, download=False)
            raw_entries = result.get('entries', [])
        except Exception as e:
            print(f"抓取頻道影片清單失敗: {e}")
            sys.exit(1)
            
    print(f"從頻道中共撈取到 {len(raw_entries)} 部候選影片，開始進行詳情解析與過濾...")
    
    filtered_videos = []
    if cutoff_date:
        print(f"時間過濾條件：只保留 {cutoff_date.strftime('%Y-%m-%d')} 之後上傳的影片")
        
    for entry in raw_entries:
        if len(filtered_videos) >= max_results:
            break
            
        video_id = entry.get('id')
        title = entry.get('title', '')
        
        # 獲取單部影片詳情以確認上傳日期與片長
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl_single:
            try:
                info = ydl_single.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                duration = info.get('duration')
                upload_date_str = info.get('upload_date')
                
                # 1. 檢查日期範圍 (頻道影片是由新到舊，若早於限制日期可以直接中斷以節省時間)
                if upload_date_str:
                    upload_date = datetime.strptime(upload_date_str, "%Y%m%d")
                    if cutoff_date and upload_date < cutoff_date:
                        print(f"   [停止] 遇到已早於指定日期 ({cutoff_date.strftime('%Y-%m-%d')}) 的影片: {title} ({upload_date.strftime('%Y-%m-%d')})")
                        break
                else:
                    upload_date = None
                
                # 2. 檢查片長
                if duration is not None and duration < min_duration:
                    continue
                
                duration_min = round(duration / 60, 1) if duration else 0
                formatted_date = f"{upload_date_str[:4]}-{upload_date_str[4:6]}-{upload_date_str[6:]}" if upload_date_str else "未知"
                
                print(f"   [符合條件] [{formatted_date}] {title} ({duration_min} 分鐘)")
                filtered_videos.append({
                    'id': video_id,
                    'title': title,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'upload_date': formatted_date,
                    'duration_sec': duration,
                    'duration_min': duration_min,
                    'uploader': info.get('uploader', '未知講者')
                })
            except Exception:
                continue
                
    return filtered_videos

def main():
    parser = argparse.ArgumentParser(description="自動化 YouTube 頻道影片抓取與 NotebookLM 語音轉譯")
    parser.add_argument('--channel-url', type=str, required=True, help="YouTube 頻道影片頁面網址 (例如：https://www.youtube.com/@GoogleDeepMind/videos)")
    parser.add_argument('--notebook-id', type=str, required=True, help="Google NotebookLM 筆記本 ID")
    parser.add_argument('--days', type=int, default=0, help="抓取最近幾天的影片，設為 0 則不限天數")
    parser.add_argument('--start-date', type=str, default=None, help="只抓取此日期之後的影片，格式為 YYYY-MM-DD")
    parser.add_argument('--max-results', type=int, default=10, help="每次最多處理影片數 (預設 10 部)")
    parser.add_argument('--min-duration', type=int, default=600, help="最低影片長度限制，單位秒，預設 600 秒 = 10 分鐘")
    parser.add_argument('--output-dir', type=str, default='youtube_transcripts', help="逐字稿輸出目錄")
    parser.add_argument('--nlm-path', type=str, default=r"C:\Users\clong\AppData\Roaming\Python\Python314\Scripts\nlm.exe", help="nlm.exe 的路徑")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 決定 cutoff_date
    cutoff_date = None
    if args.start_date:
        cutoff_date = parse_date(args.start_date)
    elif args.days > 0:
        cutoff_date = datetime.now() - timedelta(days=args.days)
        
    # 1. 抓取頻道影片並進行篩選
    videos = get_channel_videos(
        channel_url=args.channel_url,
        cutoff_date=cutoff_date,
        max_results=args.max_results,
        min_duration=args.min_duration
    )
    
    if not videos:
        print("\n沒有找到符合條件的最新影片，程序結束。")
        sys.exit(0)
        
    print(f"\n找到 {len(videos)} 部影片符合條件。開始與 NotebookLM 進行同步...")
    
    # 2. 取得筆記本現有來源
    existing = get_existing_notebook_sources(args.notebook_id, args.nlm_path)
    
    to_upload = []
    for video in videos:
        title = video['title']
        video_id = video['id']
        is_dup = False
        if existing:
            for ext in existing:
                ext_title = ext['title'].lower()
                # 匹配方式：1. 標題相似；2. 來源標題中包含影片 ID（用於 URL 當標題的情況）
                if (title[:15].lower() in ext_title or 
                    ext_title[:15] in title[:15].lower() or 
                    video_id.lower() in ext_title):
                    is_dup = True
                    break
        if is_dup:
            print(f" ➔ 影片已存在於筆記本中，跳過上傳：{title}")
        else:
            to_upload.append(video)
            
    if not to_upload:
        print("\n所有符合條件的影片皆已存在於 NotebookLM 中，無須新增。")
    else:
        print(f"\n準備上傳 {len(to_upload)} 部新影片至 NotebookLM...")
        for idx, video in enumerate(to_upload, 1):
            title = video['title']
            print(f" [{idx}/{len(to_upload)}] 正在上傳影片並等待後台語音轉譯：{title}...")
            cmd = [args.nlm_path, "add", "url", args.notebook_id, video['url'], "--wait"]
            try:
                subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=600)
                print("   上傳與轉譯完成")
            except subprocess.TimeoutExpired:
                print("   上傳或轉譯等待超時，跳過。")
            except Exception as e:
                print(f"   上傳失敗: {e}")
                
    # 3. 重新獲取來源列表，下載逐字稿
    print("\n開始獲取影片逐字稿...")
    latest_sources = None
    final_results = []
    
    for video in videos:
        title = video['title']
        video_id = video['id']
        clean_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        out_file = os.path.join(args.output_dir, f"{clean_title}.txt")
        
        print(f"\n[處理影片] {title}")
        
        # 3.1 嘗試本機 yt-dlp 快速下載字幕 (優先)
        vtt_file = None
        try:
            print(" ➔ 嘗試從 YouTube 本機下載字幕...")
            sub_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['zh-Hant', 'zh-TW', 'zh', 'en'],
                'outtmpl': os.path.join(args.output_dir, f"temp_{video_id}.%(ext)s"),
                'quiet': True
            }
            with yt_dlp.YoutubeDL(sub_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                
            # 搜尋下載的 vtt 檔案
            for f in os.listdir(args.output_dir):
                if f.startswith(f"temp_{video_id}") and f.endswith(".vtt"):
                    vtt_file = os.path.join(args.output_dir, f)
                    break
        except Exception as e:
            print(f" ⚠️ 本機字幕下載嘗試失敗: {e}")
            
        if vtt_file and os.path.exists(vtt_file):
            # 本機下載成功，清洗 VTT
            print(" ➔ 成功下載本機字幕，開始文字清洗與去重...")
            try:
                with open(vtt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if not line: continue
                    if line.startswith('WEBVTT') or line.startswith('Kind:') or line.startswith('Language:'): continue
                    if '-->' in line: continue
                    line = re.sub(r'<[^>]+>', '', line).strip()
                    if line: cleaned_lines.append(line)
                    
                # 語音轉寫文字去重
                final_lines = []
                for line in cleaned_lines:
                    if not final_lines:
                        final_lines.append(line)
                        continue
                    prev = final_lines[-1]
                    if line == prev: continue
                    if line.startswith(prev):
                        final_lines[-1] = line
                    elif prev.endswith(line) or line in prev:
                        continue
                    else:
                        final_lines.append(line)
                        
                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(final_lines))
                    
                os.remove(vtt_file)
                video['transcript_file'] = os.path.abspath(out_file)
                final_results.append(video)
                print(f" ➔ 成功取得逐字稿並寫入：{out_file}")
                continue
            except Exception as e:
                print(f" ⚠️ 本機字幕清洗失敗，將使用 Fallback 管道: {e}")
                if vtt_file and os.path.exists(vtt_file):
                    os.remove(vtt_file)
                    
        # 3.2 Fallback 管道：從 NotebookLM 下載
        print(" ➔ 影片無本機字幕，切換 Fallback 管道：從 NotebookLM 下載轉譯...")
        if latest_sources is None:
            latest_sources = get_existing_notebook_sources(args.notebook_id, args.nlm_path)
            
        matched_src = None
        if latest_sources:
            for src in latest_sources:
                src_title = src['title'].lower()
                if (title[:15].lower() in src_title or 
                    src_title[:15] in title[:15].lower() or 
                    video_id.lower() in src_title):
                    matched_src = src
                    break
                    
        if matched_src:
            print(f" 正在下載 NotebookLM 逐字稿：{title} -> {out_file}...")
            cmd = [args.nlm_path, "content", "source", matched_src['id'], "--output", out_file]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if res.returncode == 0 and os.path.exists(out_file):
                video['transcript_file'] = os.path.abspath(out_file)
                final_results.append(video)
                print(f" ➔ 成功從 NotebookLM 取得逐字稿並寫入：{out_file}")
            else:
                print(f" ⚠️ 呼叫 NotebookLM 下載失敗 (exit code: {res.returncode}): {res.stderr.strip() or '未知錯誤'}")
        else:
            print(f" ⚠️ 在 NotebookLM 中也找不到對應的來源，此影片無法擷取逐字稿。")
            
    # 4. 儲存結果 JSON
    results_json_path = os.path.join(args.output_dir, 'channel_sync_results.json')
    with open(results_json_path, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
        
    print(f"\n頻道同步完成！結果索引檔儲存至：{os.path.abspath(results_json_path)}")

if __name__ == '__main__':
    main()
