"""
This module processes client requests, fetches databases, and writes responses.
"""

__version__ = "0.1"
__author__ = "Aleksei Mashlakov"

import os
import sys

from tornado.escape import json_decode, json_encode
from tornado.ioloop import IOLoop
from tornado.locks import Semaphore
from tornado.web import RequestHandler

from interface.encryption import RSAEncryption

# sem = Semaphore(1)

try:
    import logging

    from __main__ import logger_name

    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")


class BasicHandler(RequestHandler):
    def initialize(self, database):
        self.db = database

    async def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json_decode(self.request.body)
        else:
            self.json_args = None
            self.send_error(status_code=400, reason="Content-Type must be JSON")

    async def post(self):
        try:
            # async with sem:
            #     response = await self.db.handle_request(self.json_args)
            response = await self.db.handle_request(self.json_args)
            self.write(json_encode(response))
        except ValueError:
            self.send_error(400, reason="Unable to parse JSON.")  # Bad Request


class EncryptedHandler(RequestHandler):
    def initialize(self, database):
        self.db = database

    async def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json_decode(RSAEncryption().decrypt(self.request.body))
        else:
            self.json_args = None
            self.send_error(status_code=400, reason="Content-Type must be JSON")

    async def post(self):
        try:
            # async with sem:
            #     response = await self.db.handle_request(self.json_args)
            response = await self.db.handle_request(self.json_args)
            encrypted_response = RSAEncryption().encrypt(json_encode(response))
            self.write(encrypted_response)
        except ValueError:
            self.send_error(400, reason="Unable to parse JSON.")  # Bad Request


class ShutdownHandler(RequestHandler):
    async def post(self):
        try:
            self.write(json_encode({"success": True}))
            IOLoop.current().stop()
        except ValueError:
            self.send_error(400, reason="Bad Request.")
