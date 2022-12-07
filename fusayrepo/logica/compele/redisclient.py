# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

import redis

log = logging.getLogger(__name__)

PASS_REDIS_PROD = "Hart$$471"
#myredis = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True, password=PASS_REDIS_PROD)


myredis = redis.StrictRedis('localhost', 6379, charset="utf-8", decode_responses=True)


class RedisPublisher:

    def __init__(self):
        self.channel = 'facturas'
        self.red = myredis

    def publish_message(self, message):
        self.red.publish(self.channel, message)


"""
if __name__ == "__main__":
    redispub = RedisPublisher()

    message = {"emp_codigo": 1,"emp_esquema": "fusay","trn_codigo": 650,"accion": "autoriza"}

    redispub.publish_message(message)

    print("Termino")

"""
