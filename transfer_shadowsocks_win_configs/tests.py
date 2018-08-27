# coding=utf-8

from transfer_shadowsocks_win_configs import Transfer
import unittest
import os


class TestTransfer(unittest.TestCase):

    def setUp(self):
        self.root = os.path.dirname(os.path.abspath(__file__))
        self.win_config_filename = os.path.join(self.root, "gui-config.json")
        self.mac_config_filename = os.path.join(self.root, "mac_configs.json")

    def test_get_file_contents(self):
        self.assertTrue(
            len(Transfer().get_file_contents(self.win_config_filename)) > 0)

    def test_transfer_win_configs(self):
        self.assertTrue(not os.path.isfile(self.mac_config_filename))
        self.assertTrue(Transfer().transfer_win_configs(
            self.win_config_filename, self.mac_config_filename))

        self.assertTrue(os.path.isfile(self.mac_config_filename))

        if os.path.isfile(self.mac_config_filename):
            os.remove(self.mac_config_filename)

        self.assertTrue(not os.path.isfile(self.mac_config_filename))


if __name__ == "__main__":
    unittest.main()
