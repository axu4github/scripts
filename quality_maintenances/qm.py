# -*- coding: utf-8 -*-

import redis

""" 质检任务维护脚本 """

REDIS_HOST = ''
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
print r
