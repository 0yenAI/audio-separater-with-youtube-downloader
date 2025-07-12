# -*- coding: utf-8 -*-
import sys
import os
import tempfile
import argparse
from pathlib import Path
from datetime import datetime
from moviepy.audio.io.AudioFileClip import AudioFileClip
import logging
import subprocess
import yt_dlp
import time
import threading

# 不要なログを抑制
logging.basicConfig(level=logging.ERROR)

def show_loading_animation(stop_event):
    """
    ローディングアニメーションを表示する
    """
    num = 1
    clock = 0.5
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    print(" ")

    while not stop_event.is_set():
        s = 'N O W  L O A D I N G'
        space = ' ' * num
        count = num - 20

        if num < 20:
            time.sleep(clock)
            print(f'\r{space} {s}', end='')
            num += 1
        else:
            if count <= len(s):
                time.sleep(clock)
                print(f'\r{s[len(s) - count:]} {" " * (num - count)} {s[:(len(s) - count)]}', end='')
                num += 1
            else:
                num = 1

def download_videos(urls: list[str]) -> list[Path]:
    """
    YouTubeから動画をMP4形式でダウンロードする
    ダウンロードしたファイルのパスのリストを返す
    """
    print("YouTube動画のダウンロードを開始します...")
    downloaded_temp_paths = [] # 一時的なダウンロードパスを格納
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
                    if filepath:
                        downloaded_temp_paths.append(Path(filepath))
                elif info and info.get('_type') == 'playlist':
                    for entry in info.get('entries', []):
                        if entry and entry.get('_type') == 'video':
                            filepath = entry.get('filepath')
                            if filepath:
                                downloaded_temp_paths.append(Path(filepath))
        print("ダウンロードが完了しました。")
        try:
            subprocess.run(["afplay", "bell.mp3"], check=True)
        except FileNotFoundError:
            print("警告: afplayコマンドが見つかりません。再生できませんでした。")
        except subprocess.CalledProcessError:
            print("警告: bell.mp3の再生に失敗しました。")

        # ダウンロードされたファイルを新しい命名規則でリネーム
        renamed_paths = []
        for old_path in downloaded_temp_paths:
            if old_path.exists():
                timestamp_str = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                new_filename = f"{timestamp_str}.mp4" # mp4でダウンロードされることを想定
                new_path = old_path.parent / new_filename
                old_path.rename(new_path)
                renamed_paths.append(new_path)
                print(f" - ファイル名を変更しました: {old_path.name} -> {new_path.name}")
            else:
                print(f"警告: ダウンロードされた一時ファイルが見つかりません: {old_path}")

        return renamed_paths
    except Exception as e:
        print(f"ダウンロード中にエラーが発生しました: {e}")
        return []


def isolate_vocals(video_path: Path):
    """
    単一の動画ファイルからボーカルを分離する (audio-separator Dockerを使用)
    """
    if not video_path.is_file():
        print(f"エラー: ファイルが見つかりません: {video_path}")
        return

    print(f"処理を開始します: {video_path.name}")

    # 1. 出力ファイル名の決定
    today_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = video_path.parent / f"output_{today_str}_{video_path.stem}"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # requirements.txt を生成
        print(f" - requirements.txt を生成中...")
        generate_req_command = ["uv", "pip", "freeze"] # 修正
        req_result = subprocess.run(generate_req_command, capture_output=True, text=True, check=True)
        with open("requirements.txt", "w") as f:
            f.write(req_result.stdout)
        print(" - requirements.txt 生成完了")

        # Docker イメージのビルド
        image_name = "vocal-isolater-audio-separator"
        print(f" - Docker イメージをビルド中: {image_name}")
        build_command = ["docker", "build", "-t", image_name, "."]
        build_result = subprocess.run(build_command, capture_output=True, text=True, check=True)
        print(build_result.stdout)
        if build_result.stderr:
            print(f"""Docker Build (stderr):
{build_result.stderr}""")

        # audio-separator Docker コンテナを実行してボーカルを分離
        # 入力ファイルをコンテナにマウントし、出力ディレクトリもマウントする
        # audio-separator -i <入力ファイル> -o <出力ディレクトリ> -m MDX23C
        command = [
            "docker", "run", "--rm",
            "-v", f"{video_path.parent.absolute()}:/input", # 入力ファイルのあるディレクトリをマウント
            "-v", f"{output_dir.absolute()}:/output",       # 出力ディレクトリをマウント
            image_name, "audio-separator",
            f"/input/{video_path.name}", # 入力ファイルを直接引数として渡す
            "--output_dir", "/output",   # 出力ディレクトリを --output_dir で指定
            "-m", "MDX23C-8KFFT-InstVoc_HQ.ckpt", # モデルファイル名を指定
            "--output_format", "MP3" # 出力形式をMP3に指定
        ]
        print(f" - audio-separator Docker を実行中...")
        
        stop_event = threading.Event()
        animation_thread = threading.Thread(target=show_loading_animation, args=(stop_event,))
        animation_thread.start()

        try:
            # Popenを使用して非同期でコマンドを実行
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate() # 完了を待つ

            stop_event.set() # アニメーションを停止
            animation_thread.join() # スレッドが終了するのを待つ

            # clear the animation line
            print("\r" + " " * 80 + "\r", end="")

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)

            print(stdout)
            if stderr:
                print(f"""audio-separator Docker (stderr):
{stderr}""")
        except subprocess.CalledProcessError as e:
            stop_event.set()
            animation_thread.join()
            print("\r" + " " * 80 + "\r", end="")
            print(f"Docker エラーが発生しました ({video_path.name}): {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return # エラーが発生した場合はここで処理を中断
        except Exception as e:
            stop_event.set()
            animation_thread.join()
            print("\r" + " " * 80 + "\r", end="")
            print(f"エラーが発生しました ({video_path.name}): {e}")
            return # エラーが発生した場合はここで処理を中断

        # audio-separator は出力ディレクトリ内に <元のファイル名>_vocals.mp3 と <元のファイル名>_accompaniment.mp3 を生成する
        # audio-separator は出力ディレクトリ内に <元のファイル名>_(Vocals)_<モデル名>.mp3 を生成する
        # 例: JfQzXhHCmkk_(Vocals)_MDX23C-8KFFT-InstVoc_HQ.mp3
        spleeter_output_vocals_path = output_dir / f"{video_path.stem}_(Vocals)_MDX23C-8KFFT-InstVoc_HQ.mp3"
        final_output_path = output_dir / f"{video_path.stem}_isolated.mp3"

        if spleeter_output_vocals_path.is_file():
            # ボーカルファイルをリネーム
            spleeter_output_vocals_path.rename(final_output_path)
            print(f"処理が完了しました。出力ファイル: {final_output_path.name}")
            try:
                subprocess.run(["afplay", "bell.mp3"], check=True)
            except FileNotFoundError:
                print("警告: afplayコマンドが見つかりません。再生できませんでした。")
            except subprocess.CalledProcessError:
                print("警告: bell.mp3の再生に失敗しました。")
        else:
            print("エラー: ボーカルの分離に失敗しました。")

    except subprocess.CalledProcessError as e:
        print(f"Docker エラーが発生しました ({video_path.name}): {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"エラーが発生しました ({video_path.name}): {e}")

def main():    
    parser = argparse.ArgumentParser(description="動画からボーカルを分離、またはYouTube動画をダウンロードします。")        
    group = parser.add_mutually_exclusive_group(required=True)    
    group.add_argument(        "-c", "--convert",         nargs='+',         help="ボーカル分離を行う動画ファイルのパス。"    )    
    group.add_argument(        "-d", "--download",         nargs='+',         help="ダウンロードするYouTube動画のURL。"    )    
    args = parser.parse_args()    
    if args.convert:        
        for path_str in args.convert:            
            video_path = Path(path_str)            
            isolate_vocals(video_path)            
            print("-" * 20)    
    elif args.download:        
            downloaded_files = download_videos(args.download)        
            if downloaded_files:            
                print("\nダウンロードされた動画のボーカル分離を開始します...")            
                for video_path in downloaded_files:                
                    isolate_vocals(video_path)                
                    print("-" * 20)

if __name__ == "__main__":    main()