# coding=utf-8

import base64
import json
import copy
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


MAC_CONFIGS = {
    "random": False,
    "authPass": None,
    "useOnlinePac": False,
    "TTL": 0,
    "global": False,
    "reconnectTimes": 3,
    "index": 0,
    "proxyType": 0,
    "proxyHost": None,
    "authUser": None,
    "proxyAuthPass": None,
    "isDefault": False,
    "pacUrl": None,
    "proxyPort": 0,
    "randomAlgorithm": 0,
    "proxyEnable": False,
    "enabled": True,
    "autoban": False,
    "proxyAuthUser": None,
    "shareOverLan": False,
    "localPort": 1080,
    "configs": []
}


class Transfer(object):
    """ 转换Win配置文件到 """

    def get_file_contents(self, fname):
        contents = ""
        if os.path.isfile(fname):
            with open(fname) as f:
                contents = "".join(f.readlines())

        return contents

    def put_file_contents(self, fname, contents):
        if os.path.isfile(fname):
            os.remove(fname)

        with open(fname, "w") as f:
            f.write(contents)

        return True

    def transfer_win_config(self, win_config):
        remarks = win_config["remarks"].split(",")[0]
        return {
            "enable": True,
            "password": win_config["password"],
            "method": win_config["method"],
            "remarks": remarks,
            "remarks_base64": base64.b64encode(remarks),
            "server": win_config["server"],
            "server_port": win_config["server_port"],
            "enabled_kcptun": False,
            "kcptun": {
                "nocomp": False,
                "key": "it's a secrect",
                "crypt": "aes",
                "datashard": 10,
                "mtu": 1350,
                "mode": "fast",
                "parityshard": 3,
                "arguments": ""
            }
        }

    def transfer_win_configs(self, win_config_fname, fname):
        contents, mac_configs = "", copy.copy(MAC_CONFIGS)
        if os.path.isfile(win_config_fname):
            contents = self.get_file_contents(win_config_fname)

        if contents != "":
            win_configs = json.loads(contents)
            if len(win_configs["configs"]) > 0:
                for win_config in win_configs["configs"]:
                    mac_configs["configs"].append(
                        self.transfer_win_config(win_config))

        return self.put_file_contents(fname, json.dumps(mac_configs))


if __name__ == "__main__":
    win = sys.argv[1]
    mac = sys.argv[2]
    print("Transfer Win({0}) To Mac({1}).".format(win, mac))
    print(Transfer().transfer_win_configs(win, mac))
