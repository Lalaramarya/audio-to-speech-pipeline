import unittest
from unittest.mock import Mock

from ekstep_data_pipelines.data_marker.data_mover import MediaFilesMover


class DataMoverTests(unittest.TestCase):
    def setUp(self):
        self.file_system = Mock()
        self.media_files_mover = MediaFilesMover(self.file_system, 2)

    def test__should_move_media_files(self):
        landing_base_path = (
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/landing/"
            "hindi/audio/swayamprabha_chapter"
        )

        files = [
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/1/clean/file1.wav",
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/1/clean/file2.wav",
        ]
        self.media_files_mover.move_media_files(files, landing_base_path)
        call_args_list = self.file_system.mv_file.call_args_list

        self.assertEqual(
            call_args_list[0][0][0],
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/1/clean/file1.wav",
        )
        self.assertEqual(call_args_list[0][0][1], f"{landing_base_path}/1/clean")

        self.assertEqual(
            call_args_list[1][0][0],
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/1/clean/file2.wav",
        )
        self.assertEqual(call_args_list[1][0][1], f"{landing_base_path}/1/clean")

    def test__should_move_media_dirs(self):
        landing_base_path = (
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/landing/"
            "hindi/audio/swayamprabha_chapter/archive"
        )

        files = [
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/1",
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/2",
        ]
        self.media_files_mover.move_media_paths(files, landing_base_path)
        call_args_list = self.file_system.mv.call_args_list
        self.assertEqual(
            call_args_list[0][0][0],
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/1",
        )
        self.assertEqual(call_args_list[0][0][1], f"{landing_base_path}/1")

        self.assertEqual(
            call_args_list[1][0][0],
            "gs://ekstepspeechrecognition-dev/data/audiotospeech/raw/catalogued/hindi/audio/"
            "swayamprabha_chapter/2",
        )
        self.assertEqual(call_args_list[1][0][1], f"{landing_base_path}/2")
