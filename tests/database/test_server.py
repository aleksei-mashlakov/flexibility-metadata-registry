
import os
import sys
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
print(os.getcwd())

import requests
from requests.structures import CaseInsensitiveDict
import yaml
import json

url = "http://127.0.0.1:8084/register"
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Content-Type"] = "text/plain" # "application/json"
payload = yaml.full_load(open('../config/thing_description_template.yaml', 'r'))

"""
{
  "Id": 78912,
  "Customer": "Jason Sweet",
}
"""

resp = requests.post(url, headers=headers, data=json.dumps(payload))
print(resp.status_code)
print(resp.headers)
print(resp.content)
print(resp.json())
