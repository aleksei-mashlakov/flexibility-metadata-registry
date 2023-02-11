"""
This module is empty.
"""

__version__ = "0.1"
__author__ = "Aleksei Mashlakov"

import json
import pickle

# from rediscluster import RedisCluster
from redis import Redis

try:
    import logging

    from __main__ import logger_name

    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")


class ClusterDB(object):
    def __init__(self):
        pass
        # self.master = RedisCluster(startup_nodes='7000', decode_responses=True)
        # self.replica = RedisCluster(startup_nodes='7001', decode_responses=True)

    def write_data(self):
        pass

    def read_data(self):
        pass
