import subprocess
from pathlib import Path
from datetime import datetime
import threading
import logging

from utils import show_loading_animation, play_bell_sound

# 不要なログを抑制
logging.basicConfig(level=logging.ERROR)

class AudioProcessor:
    def __init__(self):
        pass

    def _run_docker_command(self, command: list[str], process_name: str):
        """
        Dockerコマンドを実行し、ローディングアニメーションを表示する
        """
        print(f" - {process_name} Docker を実行中...")
        
        stop_event = threading.Event()
        animation_thread = threading.Thread(target=show_loading_animation, args=(stop_event,))
        animation_thread.start()

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)

            print(stdout)
            if stderr:
                print(f'"""{process_name} Docker (stderr):\n{stderr}"""')
            return True
        except subprocess.CalledProcessError as e:
            print(f"Docker エラーが発生しました: {e}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return False
        finally:
            stop_event.set()
            animation_thread.join()
            print("" + " " * 80 + "", end="")

    def isolate_vocals(self, video_path: Path, video_id: str = None):
        """
        単一の動画ファイルからボーカルを分離する (audio-separator Dockerを使用)
        """
        if not video_path.is_file():
            print(f"エラー: ファイルが見つかりません: {video_path}")
            return

        print(f"処理を開始します: {video_path.name}")

        today_str = datetime.now().strftime('%Y-%m-%d')
        output_dir = video_path.parent / f"output_{today_str}_{video_path.stem}"
        output_dir.mkdir(parents=True, exist_ok=True)

        image_name = "vocal-isolater-audio-separator"
        print(f" - Docker イメージをビルド中: {image_name}")
        build_command = ["docker", "build", "-t", image_name, "."]
        build_result = subprocess.run(build_command, capture_output=True, text=True, check=True)
        print(build_result.stdout)
        if build_result.stderr:
            print(f'"""Docker Build (stderr):\n{build_result.stderr}"""')

        command = [
            "docker", "run", "--rm",
            "-v", f"{video_path.parent.absolute()}:/input",
            "-v", f"{output_dir.absolute()}:/output",
            image_name, "audio-separator",
            f"/input/{video_path.name}",
            "--output_dir", "/output",
            "-m", "MDX23C-8KFFT-InstVoc_HQ.ckpt",
            "--output_format", "MP3"
        ]
        
        if self._run_docker_command(command, "audio-separator"):
            # audio-separatorの出力ファイル名は元の動画IDに基づくため、video_idを使用
            # video_idがない場合は、video_path.stem（タイムスタンプ名）を使用
            base_name = video_id if video_id else video_path.stem
            spleeter_output_vocals_path = output_dir / f"{base_name}_(Vocals)_MDX23C-8KFFT-InstVoc_HQ.mp3"
            final_output_path = output_dir / f"{video_path.stem}_isolated.mp3"

            if spleeter_output_vocals_path.is_file():
                spleeter_output_vocals_path.rename(final_output_path)
                print(f"処理が完了しました。出力ファイル: {final_output_path.name}")
                play_bell_sound()
            else:
                print("エラー: ボーカルの分離に失敗しました。")

    def convert_to_midi(self, audio_path: Path):
        """
        単一の音声ファイルからMIDIを生成する (basic-pitch Dockerを使用)
        """
        if not audio_path.is_file():
            print(f"エラー: ファイルが見つかりません: {audio_path}")
            return

        print(f"MIDI変換を開始します: {audio_path.name}")
        
        output_dir = audio_path.parent
        
        command = [
            "docker", "run", "--rm",
            "-v", f"{audio_path.parent.absolute()}:/basic-pitch/audio",
            "my-basic-pitch-app",
            "basic-pitch",
            "/basic-pitch/audio",
            f"/basic-pitch/audio/{audio_path.name}",
        ]

        if self._run_docker_command(command, "basic-pitch"):
            midi_filename = f"{audio_path.stem}_basic_pitch.mid"
            final_output_path = output_dir / midi_filename
            
            if final_output_path.exists():
                print(f"処理が完了しました。出力ファイル: {final_output_path}")
                play_bell_sound()
            else:
                print("エラー: MIDIファイルの生成に失敗しました。")
