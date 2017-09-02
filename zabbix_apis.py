# -*- coding: UTF-8 -*-

import urllib2
import json
import random

ZABBIX_URL = "http://10.0.3.49/zabbix/api_jsonrpc.php"
ZABBIX_USERNAME = "Admin"
ZABBIX_PASSWORD = "zabbix"

# 参数说明 (监控项，返回值类型)
# 返回值类型说明详见：https://www.zabbix.com/documentation/2.4/manual/api/reference/history/get
items = [
    ("vfs.fs.size[/,total]", 3),  # "/"目录全部大小
    ("vfs.fs.size[/,free]", 3),  # "/"目录可用大小
    ("vfs.fs.size[/,used]", 3),  # "/"目录已使用大小
    ("net.if.in[eth1]", 3),      # "eth1"入口流量
    ("net.if.out[eth1]", 3),     # "eth1"出口流量
    ("system.cpu.load[percpu,avg1]", 0),  # CPU负载每分钟
    ("system.cpu.load[percpu,avg5]", 0),  # CPU负载每5分钟
    ("system.cpu.load[percpu,avg15]", 0),  # CPU负载每15分钟
    ("vm.memory.size[total]", 3),     # 内存总数
    ("vm.memory.size[available]", 3),  # 内存可用
]


def get_request_params(**kwargs):
    request_params = {
        "jsonrpc": "2.0",
        "id": random.random(),
    }

    if "auth" in kwargs and kwargs["auth"] is not None:
        request_params["auth"] = kwargs["auth"]

    request_params.update(**kwargs)
    # print "[Request] => {0}".format(request_params)
    return request_params


def zabbix_request(url=ZABBIX_URL, method=None, params=None, **kwargs):
    if method is not None and params is not None:
        req = urllib2.Request(
            url=url,
            data=json.dumps(get_request_params(
                method=method, params=params, **kwargs)),
            headers={"Content-Type": "application/json"})
        res = urllib2.urlopen(req)
        return json.loads(res.read())['result']


def zabbix_login(user=ZABBIX_USERNAME, password=ZABBIX_PASSWORD):
    return zabbix_request(ZABBIX_URL, "user.login", {
        "user": user,
        "password": password
    })

if __name__ == '__main__':
    auth_token = zabbix_login()

    # 得到所有已添加服务器的"id"信息
    hosts = zabbix_request(auth=auth_token, method="host.get", params={
        "output": ["hostid", "host"]
    })

    print hosts
    if True:
        for info in hosts:
            print "*" * 100
            print info
            for (item, response_type) in items:
                print "-" * 50
                print "==> {0} <==".format(item)
                # 获取当前时间点的监控信息
                response = zabbix_request(auth=auth_token, method="item.get", params={
                    "output": ["lastvalue", "lastclock"],
                    # "output": "extend", # 全部返回值
                    "hostids": info["hostid"],
                    "search": {
                        "key_": item
                    }
                })

                # print "[Response] => {0}".format(response)

                print "-" * 50
                # 获取时间范围的监控信息
                print "[Response] => {0}".format(zabbix_request(auth=auth_token, method="history.get", params={
                    "history": response_type,
                    "time_from": "1496283310",
                    "time_till": "1496369710",
                    "hostids": info["hostid"],
                    "itemids": response[0]["itemid"],
                    "output": "extend",
                    "sortfield": "clock",
                    "sortorder": "DESC",
                    # "limit": 10 # 只返回其中10条
                }))

            print "*" * 100
            print ""
            exit()

    print "*" * 100
