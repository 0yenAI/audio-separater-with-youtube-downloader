import yt_dlp
from pathlib import Path
from datetime import datetime
import subprocess
import logging

from utils import play_bell_sound

# 不要なログを抑制
logging.basicConfig(level=logging.ERROR)

def download_videos(urls: list[str]) -> list[Path]:
    """
    YouTubeから動画をMP4形式でダウンロードする
    ダウンロードしたファイルのパスのリストを返す
    """
    print("YouTube動画のダウンロードを開始します...")
    downloaded_temp_paths_with_ids = [] # (一時的なダウンロードパス, 動画ID)を格納
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4/best',
        'outtmpl': '%(id)s.%(ext)s', # 動画IDと拡張子で命名
        'noplaylist': True,
        'paths': {'home': '.'}, # カレントディレクトリにダウンロード
        'overwrites': True, # 既存ファイルを上書き
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in urls:
                print(f" - ダウンロード中: {url}")
                info = ydl.extract_info(url, download=True)
                if info and info.get('_type') == 'video':
                    filepath = info.get('filepath')
                    video_id = info.get('id')
                    if filepath and video_id:
                        downloaded_temp_paths_with_ids.append((Path(filepath), video_id))
                elif info and info.get('_type') == 'playlist':
                    for entry in info.get('entries', []):
                        if entry and entry.get('_type') == 'video':
                            filepath = entry.get('filepath')
                            video_id = entry.get('id')
                            if filepath and video_id:
                                downloaded_temp_paths_with_ids.append((Path(filepath), video_id))
        print("ダウンロードが完了しました。")
        play_bell_sound()

        # ダウンロードされたファイルを新しい命名規則でリネーム
        renamed_paths_with_ids = []
        for old_path, video_id in downloaded_temp_paths_with_ids:
            if old_path.exists():
                timestamp_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                new_filename = f"{timestamp_str}.mp4" # mp4でダウンロードされることを想定
                new_path = old_path.parent / new_filename
                old_path.rename(new_path)
                renamed_paths_with_ids.append((new_path, video_id))
                print(f" - ファイル名を変更しました: {old_path.name} -> {new_path.name}")
            else:
                print(f"警告: ダウンロードされた一時ファイルが見つかりません: {old_path}")

        return renamed_paths_with_ids
    except Exception as e:
        print(f"ダウンロード中にエラーが発生しました: {e}")
        return []
