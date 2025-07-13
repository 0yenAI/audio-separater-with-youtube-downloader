import unittest
from unittest.mock import patch
import os
import time
import threading
import subprocess

from utils import play_bell_sound, show_loading_animation

class TestUtils(unittest.TestCase):

    @patch('subprocess.run')
    def test_play_bell_sound_success(self, mock_run):
        mock_run.return_value.returncode = 0
        play_bell_sound()
        mock_run.assert_called_once_with(["afplay", "bell.mp3"], check=True)

    @patch('subprocess.run')
    def test_play_bell_sound_file_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        with self.assertLogs('root', level='ERROR') as cm:
            play_bell_sound()
            self.assertIn("警告: afplayコマンドが見つかりません。再生できませんでした。", cm.output[0])

    @patch('subprocess.run')
    def test_play_bell_sound_called_process_error(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, ["afplay", "bell.mp3"])
        with self.assertLogs('root', level='ERROR') as cm:
            play_bell_sound()
            self.assertIn("警告: bell.mp3の再生に失敗しました。", cm.output[0])

    # show_loading_animationは視覚的なテストが難しいため、簡単な実行テストのみ
    def test_show_loading_animation(self):
        stop_event = threading.Event()
        thread = threading.Thread(target=show_loading_animation, args=(stop_event,))
        thread.start()
        time.sleep(1)  # アニメーションが少し実行されるのを待つ
        stop_event.set()
        thread.join()
        self.assertTrue(True) # エラーが発生しなければOK
