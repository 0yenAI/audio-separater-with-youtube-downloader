import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime
import os

from youtube_downloader import download_videos

class TestYoutubeDownloader(unittest.TestCase):

    @patch('yt_dlp.YoutubeDL')
    @patch('youtube_downloader.play_bell_sound')
    @patch('pathlib.Path.rename')
    @patch('pathlib.Path.exists')
    def test_download_videos_single_video(self, mock_exists, mock_rename, mock_play_bell_sound, mock_youtubedl):
        mock_exists.return_value = True
        mock_info = {
            '_type': 'video',
            'filepath': 'test_video.mp4',
            'id': 'test_video_id'
        }
        mock_youtubedl.return_value.__enter__.return_value.extract_info.return_value = mock_info

        urls = ["https://www.youtube.com/watch?v=test_video_id"]
        downloaded_paths = download_videos(urls)

        self.assertEqual(len(downloaded_paths), 1)
        self.assertTrue(downloaded_paths[0].name.startswith(datetime.now().strftime('%Y-%m-%d')))
        mock_play_bell_sound.assert_called_once()
        mock_rename.assert_called_once()

    @patch('yt_dlp.YoutubeDL')
    @patch('youtube_downloader.play_bell_sound')
    @patch('pathlib.Path.rename')
    @patch('pathlib.Path.exists')
    def test_download_videos_playlist(self, mock_exists, mock_rename, mock_play_bell_sound, mock_youtubedl):
        mock_exists.return_value = True
        mock_info = {
            '_type': 'playlist',
            'entries': [
                {'_type': 'video', 'filepath': 'video1.mp4', 'id': 'video1_id'},
                {'_type': 'video', 'filepath': 'video2.mp4', 'id': 'video2_id'},
            ]
        }
        mock_youtubedl.return_value.__enter__.return_value.extract_info.return_value = mock_info

        urls = ["https://www.youtube.com/playlist?list=test_playlist_id"]
        downloaded_paths = download_videos(urls)

        self.assertEqual(len(downloaded_paths), 2)
        self.assertTrue(downloaded_paths[0].name.startswith(datetime.now().strftime('%Y-%m-%d')))
        self.assertTrue(downloaded_paths[1].name.startswith(datetime.now().strftime('%Y-%m-%d')))
        mock_play_bell_sound.assert_called_once()
        self.assertEqual(mock_rename.call_count, 2)

    @patch('yt_dlp.YoutubeDL')
    @patch('youtube_downloader.play_bell_sound')
    def test_download_videos_error(self, mock_play_bell_sound, mock_youtubedl):
        mock_youtubedl.return_value.__enter__.return_value.extract_info.side_effect = Exception("Download Error")

        urls = ["https://www.youtube.com/watch?v=invalid_id"]
        downloaded_paths = download_videos(urls)

        self.assertEqual(len(downloaded_paths), 0)
        mock_play_bell_sound.assert_not_called()
