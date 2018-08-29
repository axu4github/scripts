# coding=utf-8

from transfer_voice_annotation_files import TransferVoiceAnnotationFiles
from doraemon import Doraemon
import unittest
import os


class TestTransferVoiceAnnotationFiles(unittest.TestCase):

    def setUp(self):
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.resources = os.path.join(self.root, "resources")

    def test_get_tagfiles(self):
        self.assertEqual(
            1,
            len(TransferVoiceAnnotationFiles().get_tagfiles(self.resources)))

    def test_transfer_tag_file(self):
        tag_file = os.path.join(self.resources, "test.TAG")
        transferred = TransferVoiceAnnotationFiles().transfer_tagfile(tag_file)

        self.assertEqual(map(lambda num: str(num), range(1, 21)), transferred)
        self.assertEqual(20, len(transferred))

    def test_save_transferred(self):
        tvaf = TransferVoiceAnnotationFiles()
        tag_file = os.path.join(self.resources, "test.TAG")
        transferred = tvaf.transfer_tagfile(tag_file)
        is_saved, output_fpath = tvaf.save_transferred(tag_file, transferred)

        self.assertTrue(is_saved)
        self.assertTrue(os.path.isfile(output_fpath))
        self.assertEqual(transferred, Doraemon.get_file_contents(output_fpath))

        if os.path.isfile(output_fpath):
            os.remove(output_fpath)

        self.assertTrue(not os.path.isfile(output_fpath))


if __name__ == "__main__":
    unittest.main()
