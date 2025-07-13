import argparse
from pathlib import Path

from youtube_downloader import download_videos
from audio_processor import AudioProcessor

def main():    
    parser = argparse.ArgumentParser(description="動画からボーカルを分離、YouTube動画をダウンロード、または音声ファイルをMIDIに変換します。")        
    group = parser.add_mutually_exclusive_group(required=True)    
    group.add_argument(        "-c", "--convert",         nargs='+',         help="ボーカル分離を行う動画ファイルのパス。"    )    
    group.add_argument(        "-d", "--download",         nargs='+',         help="ダウンロードするYouTube動画のURL。"    )
    group.add_argument(        "-m", "--midi",         nargs='+',         help="MIDI変換を行う音声ファイルのパス。"    )
    args = parser.parse_args()    

    audio_processor = AudioProcessor()

    if args.convert:        
        for path_str in args.convert:            
            video_path = Path(path_str)            
            audio_processor.isolate_vocals(video_path)            
            print("-" * 20)    
    elif args.download:        
            downloaded_files_with_ids = download_videos(args.download)        
            if downloaded_files_with_ids:            
                print("\nダウンロードされた動画のボーカル分離を開始します...")            
                for video_path, video_id in downloaded_files_with_ids:                
                    audio_processor.isolate_vocals(video_path, video_id)                
                    print("-" * 20)
    elif args.midi:
        for path_str in args.midi:
            audio_path = Path(path_str)
            audio_processor.convert_to_midi(audio_path)
            print("-" * 20)

if __name__ == "__main__":
    main()