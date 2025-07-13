import os
import time
import threading
import subprocess
import logging

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
            print(f'\r{space} {s}', end='', flush=True)
            num += 1
        else:
            if count <= len(s):
                time.sleep(clock)
                print(f'\r{s[len(s) - count:]} {" " * (num - count)} {s[:(len(s) - count)]}', end='', flush=True)
                num += 1
            else:
                num = 1

def play_bell_sound():
    """
    bell.mp3を再生する
    """
    try:
        subprocess.run(["afplay", "bell.mp3"], check=True)
    except FileNotFoundError:
        logging.error("警告: afplayコマンドが見つかりません。再生できませんでした。")
    except subprocess.CalledProcessError:
        logging.error("警告: bell.mp3の再生に失敗しました。")
