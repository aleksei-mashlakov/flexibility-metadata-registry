
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
import numpy as np
import json
from interface.encryption import RSAEncryption
import yaml


if __name__ == "__main__":

    message = {"success":True}
    message = yaml.full_load(open('../config/thing_description_template.yaml', 'r'))

    print(message)
    encrypted_mes = RSAEncryption().encrypt(json.dumps(message))
    print(encrypted_mes)
    decrypted_mes = json.loads(RSAEncryption().decrypt(encrypted_mes))
    print(decrypted_mes)#['success'])
