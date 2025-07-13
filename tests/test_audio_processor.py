import unittest
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
import os
import subprocess

from audio_processor import AudioProcessor

class TestAudioProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = AudioProcessor()
        self.test_video_path = Path("test_video.mp4")
        self.test_audio_path = Path("test_audio.mp3")

    @patch('audio_processor.AudioProcessor._run_docker_command')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.rename')
    @patch('pathlib.Path.is_file') # for spleeter_output_vocals_path.is_file()
    @patch('audio_processor.play_bell_sound')
    @patch('subprocess.run') # for docker build
    def test_isolate_vocals_success(self, mock_subprocess_run, mock_play_bell_sound, mock_is_file_output, mock_rename, mock_is_file_input, mock_mkdir, mock_run_docker_command):
        mock_is_file_input.return_value = True
        mock_run_docker_command.return_value = True
        mock_is_file_output.return_value = True
        mock_subprocess_run.return_value.stdout = "Docker build success"
        mock_subprocess_run.return_value.stderr = ""

        self.processor.isolate_vocals(self.test_video_path)

        mock_mkdir.assert_called_once()
        mock_run_docker_command.assert_called_once()
        mock_rename.assert_called_once()
        mock_play_bell_sound.assert_called_once()

    @patch('audio_processor.AudioProcessor._run_docker_command')
    @patch('pathlib.Path.is_file')
    def test_isolate_vocals_file_not_found(self, mock_is_file_input, mock_run_docker_command):
        mock_is_file_input.return_value = False

        self.processor.isolate_vocals(self.test_video_path)

        mock_run_docker_command.assert_not_called()

    @patch('audio_processor.AudioProcessor._run_docker_command')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.mkdir')
    @patch('subprocess.run') # for docker build
    def test_isolate_vocals_docker_command_fail(self, mock_subprocess_run, mock_mkdir, mock_is_file_input, mock_run_docker_command):
        mock_is_file_input.return_value = True
        mock_run_docker_command.return_value = False
        mock_subprocess_run.return_value.stdout = "Docker build success"
        mock_subprocess_run.return_value.stderr = ""

        self.processor.isolate_vocals(self.test_video_path)

        mock_mkdir.assert_called_once()
        # mock_run_docker_command.assert_called_once() # 呼び出されるが、その後の処理は行われない

    @patch('audio_processor.AudioProcessor._run_docker_command')
    @patch('pathlib.Path.is_file')
    @patch('pathlib.Path.exists')
    @patch('audio_processor.play_bell_sound')
    def test_convert_to_midi_success(self, mock_play_bell_sound, mock_exists, mock_is_file_input, mock_run_docker_command):
        mock_is_file_input.return_value = True
        mock_run_docker_command.return_value = True
        mock_exists.return_value = True

        self.processor.convert_to_midi(self.test_audio_path)

        mock_run_docker_command.assert_called_once()
        mock_play_bell_sound.assert_called_once()

    @patch('audio_processor.AudioProcessor._run_docker_command')
    @patch('pathlib.Path.is_file')
    def test_convert_to_midi_file_not_found(self, mock_is_file_input, mock_run_docker_command):
        mock_is_file_input.return_value = False

        self.processor.convert_to_midi(self.test_audio_path)

        mock_run_docker_command.assert_not_called()

    @patch('audio_processor.AudioProcessor._run_docker_command')
    @patch('pathlib.Path.is_file')
    def test_convert_to_midi_docker_command_fail(self, mock_is_file_input, mock_run_docker_command):
        mock_is_file_input.return_value = True
        mock_run_docker_command.return_value = False

        self.processor.convert_to_midi(self.test_audio_path)

        mock_run_docker_command.assert_called_once()

    @patch('audio_processor.show_loading_animation')
    @patch('subprocess.Popen')
    @patch('threading.Thread')
    @patch('audio_processor.play_bell_sound')
    def test_run_docker_command_success(self, mock_play_bell_sound, mock_thread, mock_popen, mock_show_loading_animation):
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("stdout_output", "stderr_output")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        command = ["docker", "run", "hello-world"]
        result = self.processor._run_docker_command(command, "Test Process")

        self.assertTrue(result)
        mock_popen.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        mock_thread.assert_called_once_with(target=mock_show_loading_animation, args=(ANY,))
        mock_thread.return_value.start.assert_called_once()
        mock_thread.return_value.join.assert_called_once()
        mock_play_bell_sound.assert_not_called() # _run_docker_commandではベルは鳴らさない

    @patch('audio_processor.show_loading_animation')
    @patch('subprocess.Popen')
    @patch('threading.Thread')
    def test_run_docker_command_called_process_error(self, mock_thread, mock_popen, mock_show_loading_animation):
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("stdout_output", "stderr_output")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        command = ["docker", "run", "invalid-command"]
        result = self.processor._run_docker_command(command, "Test Process")

        self.assertFalse(result)
        mock_popen.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        mock_thread.assert_called_once_with(target=mock_show_loading_animation, args=(ANY,))
        mock_thread.return_value.start.assert_called_once()
        mock_thread.return_value.join.assert_called_once()

    @patch('audio_processor.show_loading_animation')
    @patch('subprocess.Popen')
    @patch('threading.Thread')
    def test_run_docker_command_exception(self, mock_thread, mock_popen, mock_show_loading_animation):
        mock_popen.side_effect = Exception("Some error")

        command = ["docker", "run", "some-command"]
        result = self.processor._run_docker_command(command, "Test Process")

        self.assertFalse(result)
        mock_popen.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        mock_thread.assert_called_once_with(target=mock_show_loading_animation, args=(ANY,))
        mock_thread.return_value.start.assert_called_once()
        mock_thread.return_value.join.assert_called_once()
