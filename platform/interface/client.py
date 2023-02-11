"""
This module sends asyncronous HTTPS requests with JSON objects.
"""

__version__ = "0.1"
__author__ = "Aleksei Mashlakov"

import os
import sys
from dataclasses import dataclass
from typing import Dict

from tornado.escape import json_decode, json_encode

# from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.httpclient import (
    AsyncHTTPClient,
    HTTPClient,
    HTTPError,
    HTTPRequest,
    HTTPResponse,
)
from tornado.ioloop import IOLoop

try:
    import logging

    from __main__ import logger_name

    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")


@dataclass
class Transport:
    def handle_response(self, response: HTTPResponse) -> Dict:
        if response.error:
            log.error(response.error)
            log.debug(response.reason)
            return
        else:
            # log.info(response.code)
            # log.info(response.headers)
            # log.info(response.request_time)
            # log.info(json_decode(response.body))
            return response.body

    def serve_request(
        self,
        url: str,
        body: str,
        method: str = "POST",
        headers_type: str = "application/json",
        ca_certs: str = "",
        client_key: str = "",
        client_cert: str = "",
    ) -> HTTPResponse:
        """ """
        self.url = url
        self.body = body
        self.method = method
        self.headers = self.get_headers(headers_type=headers_type)
        self.ca_certs = ca_certs
        self.client_key = client_key
        self.client_cert = client_cert
        response = IOLoop.current().run_sync(self.make_request)
        return response

    async def asynchronous_fetch(self, request: HTTPRequest) -> HTTPResponse:
        """ """
        http_client = (
            AsyncHTTPClient()
        )  # .configure(None, defaults=dict(user_agent="MyUserAgent"))
        # http_client = AsyncHTTPClient.configure(CurlAsyncHTTPClient)
        try:
            response = await http_client.fetch(request)
        except Exception as e:
            log.error(e)
        else:
            return self.handle_response(response)

    async def make_request(self) -> Dict:
        """ """
        request = HTTPRequest(
            url=self.url,
            method=self.method,
            headers=self.headers,
            # body=json_encode(self.body),
            body=self.body,
            validate_cert=False,
            ca_certs=self.ca_certs,
            client_key=self.client_key,
            client_cert=self.client_cert,
        )
        response = await self.asynchronous_fetch(request)
        return response

    def get_headers(self, headers_type: str = "application/json") -> Dict:
        """Creates JSON headers."""
        return {key: headers_type for key in ["Accept", "Content-Type"]}
