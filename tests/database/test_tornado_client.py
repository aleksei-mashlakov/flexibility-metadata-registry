
"""
This is the example module. This module does stuff.
"""

# __all__ = ['a', 'b', 'c']
__version__ = '0.1'
__author__ = 'Aleksei Mashlakov'

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
import yaml
from interface.client import Transport


def main():
    url = "http://127.0.0.1:8084/register"
    payload = yaml.full_load(open('../config/thing_description_template.yaml', 'r'))
    request = make_request(url=url, body=payload)
    response = asynchronous_fetch(request) #
    # response = await asynchronous_fetch(request)
    return response

if __name__ == "__main__":
    payload = yaml.full_load(open('../config/thing_description_template.yaml', 'r'))
    url = "http://127.0.0.1:8084/register"
    # request = make_request(url=url, body=payload)
    # from tornado.httpclient import AsyncHTTPClient
    # client = AsyncHTTPClient()
    # response = client.fetch(request)
    # print(response)

    # response = await Transport().asynchronous_fetch(request)
    response = Transport().serve_request(url=url, body=payload)
    print(response)
