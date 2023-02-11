"""
This module manages all databases.
"""


__version__ = "0.1"
__author__ = "Aleksei Mashlakov"

import os
import sys
from dataclasses import dataclass
from typing import Dict

import yaml
from redis import Redis

from database.cluster import ClusterDB
from database.graph import GraphDB
from database.jsonstore import JSONDB

try:
    import logging

    from __main__ import logger_name

    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")


@dataclass
class DataBaseManager:

    config: dict = None

    def __post_init__(self):
        self.redis = Redis(host=self.config["host"], port=self.config["port"])
        self.jsonstore = JSONDB(host=self.config["host"], port=self.config["port"])
        self.graphstore = GraphDB(
            name=self.config["redisgraph"]["network"], database=self.redis
        )
        self.clusterstore = ClusterDB()


class DeleteDataBaseManager(DataBaseManager):
    async def handle_request(self, request_data) -> Dict:
        log.info(f"handling_delete, id={request_data['id']}")
        try:
            self.graphstore.delete_data(request_data)
            self.jsonstore.delete_data(request_data["id"])
        except Exception as e:
            log.error(f"Exception: {e}")
            return {"success": False}
        else:
            return {"success": True}


class RegisterDataBaseManager(DataBaseManager):
    async def handle_request(self, request_data) -> Dict:
        log.info(f"handling_registration, id={request_data['id']}")
        try:
            self.graphstore.write_data(request_data)
            self.jsonstore.write_data(request_data["id"], request_data)
        except Exception as e:
            log.error(f"Exception: {e}")
            return {"success": False}
        else:
            return {"success": True}


class SearchDataBaseManager(DataBaseManager):
    async def handle_request(self, request_data) -> Dict:
        log.info(f"handling_search, id={request_data['id']}")
        try:
            indexes = self.graphstore.read_data(request_data)
            print(f"Warning: Returning only discover path")
            response_data = {
                index: self.jsonstore.read_data(index, ".discover") for index in indexes
            }
        except Exception as e:
            log.error(f"Exception: {e}")
            return {"success": False}
        else:
            return response_data


class UpdateDataBaseManager(DataBaseManager):
    async def handle_request(self, request_data) -> Dict:
        log.info(f"handling_update, id={request_data['id']}")
        try:
            self.graphstore.update_data(request_data)
            self.jsonstore.update_data(request_data["id"], request_data)
        except Exception as e:
            log.error(f"Exception: {e}")
            return {"success": False}
        else:
            return {"success": True}
