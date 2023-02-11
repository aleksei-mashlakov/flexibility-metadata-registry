"""
This is the wrapper module around key-value RedisJSON database.
This module connects to Redis dababase as a client and manipulates with JSON objects.
"""

__version__ = "0.1"
__author__ = "Aleksei Mashlakov"

import os
import sys
from dataclasses import dataclass

from rejson import Client, Path

try:
    import logging

    from __main__ import logger_name

    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")


@dataclass
class JSONDB:
    """Wraps RedisJSON client's commands."""

    host: str = "localhost"
    port: int = 6379

    def __post_init__(self):
        self.rj = Client(host=self.host, port=self.port, decode_responses=True)

    def write_data(
        self, object_key: str, jsondata: dict, object_path: str = Path.rootPath()
    ):
        """Writes JSON object identified with key."""
        self.rj.jsonset(object_key, object_path, jsondata)
        return

    def read_data(self, object_key: str, object_path: str = Path.rootPath()):
        """Reads JSON object identified with key."""
        return self.rj.jsonget(object_key, self.validate_path(object_path))

    def update_data(
        self, object_key: str, jsondata: dict, object_path: str = Path.rootPath()
    ):
        """Updates JSON object identified with key."""
        self.rj.jsonset(object_key, object_path, jsondata)
        return

    def add_data(self, object_key: str, jsondata: dict, object_path: str):
        """Appends JSON object identified with key."""
        self.rj.jsonarrappend(object_key, object_path, jsondata)
        return

    def delete_data(self, object_key: str, object_path: str = Path.rootPath()):
        """Delets JSON object identified with key."""
        self.rj.jsondel(object_key, object_path)
        return

    def validate_path(self, object_path: str) -> str:
        return f"['{object_path[1:]}']" if object_path.startswith(".@") else object_path
