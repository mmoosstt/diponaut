import time as _time
from time import *


class Timer(object):

    SERVER_TIME_OFFSET = 0.0

    @classmethod
    def time(cls):
        # time in s
        return _time.time() + cls.SERVER_TIME_OFFSET

    @classmethod
    def synchronise(cls, api):

        _server_time = api.get_server_time()
        if _server_time:
            _t_server = _server_time["serverTime"]
            _t_local = int(_time.time() * 1000)
            _t_delta = (_t_server - _t_local) / 1000.

            cls.SERVER_TIME_OFFSET = cls.SERVER_TIME_OFFSET + (_t_delta - cls.SERVER_TIME_OFFSET)

            print("server time = client time + offset({0})".format(cls.SERVER_TIME_OFFSET))

time = Timer.time
