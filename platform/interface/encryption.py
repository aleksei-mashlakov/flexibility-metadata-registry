# coding: utf-8

"""
This module encrypts and decrypts short and long string messages with RSA scheme.
"""

__version__ = "0.1"
__author__ = "Aleksei Mashlakov"

from __future__ import unicode_literals

import ast
import os
from dataclasses import dataclass

import pybase64
import six
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

try:
    import logging

    from __main__ import logger_name

    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")


class PublicKeyFileExists(Exception):
    pass


@dataclass
class RSAEncryption:

    PRIVATE_KEY_FILE_PATH: str = os.getenv("PRIVATE_KEY")
    PUBLIC_KEY_FILE_PATH: str = os.getenv("PRIVATE_KEY")
    MAX_ENC_LENGTH = 200  #  2048bit certificate
    MAX_DEC_LENGTH = 344  #  2048bit certificate

    def encrypt(self, message):
        public_key = self._get_public_key()
        public_key_object = RSA.importKey(public_key)
        encryptor = PKCS1_OAEP.new(public_key_object)
        if len(message) > self.MAX_ENC_LENGTH:
            return self.rsa_long_encrypt(encryptor, message)
        else:
            encrypted_message = encryptor.encrypt(str.encode(message))
            # use pybase64 for save encrypted_message in database without problems with encoding
            return pybase64.b64encode(encrypted_message)

    def decrypt(self, encoded_encrypted_message):
        private_key = self._get_private_key()
        private_key_object = RSA.importKey(private_key)
        decryptor = PKCS1_OAEP.new(private_key_object)
        if len(encoded_encrypted_message) > self.MAX_DEC_LENGTH:
            return self.rsa_long_decrypt(decryptor, encoded_encrypted_message)
        else:
            encrypted_message = pybase64.b64decode(encoded_encrypted_message)
            decrypted_message = decryptor.decrypt(encrypted_message)
            return decrypted_message
            # return six.text_type(decrypted_message, encoding='utf8')

    def generate_keys(self):
        """Be careful rewrite your keys"""
        random_generator = Random.new().read
        key = RSA.generate(1024, random_generator)
        private, public = key.exportKey(), key.publickey().exportKey()

        if os.path.isfile(self.PUBLIC_KEY_FILE_PATH):
            raise PublicKeyFileExists("Public key exists. Delete.")
        self.create_directories()

        with open(self.PRIVATE_KEY_FILE_PATH, "w") as private_file:
            private_file.write(private)
        with open(self.PUBLIC_KEY_FILE_PATH, "w") as public_file:
            public_file.write(public)
        return private, public

    def create_directories(self, for_private_key=True):
        public_key_path = self.PUBLIC_KEY_FILE_PATH.rsplit("/", 1)
        if not os.path.exists(public_key_path):
            os.makedirs(public_key_path)
        if for_private_key:
            private_key_path = self.PRIVATE_KEY_FILE_PATH.rsplit("/", 1)
            if not os.path.exists(private_key_path):
                os.makedirs(private_key_path)

    def _get_public_key(self):
        """run generate_keys() before get keys"""
        if self.PUBLIC_KEY_FILE_PATH is not None:
            with open(self.PUBLIC_KEY_FILE_PATH, "r") as _file:
                return _file.read()
        else:
            private, public = self.generate_keys()
            return public

    def _get_private_key(self):
        """run generate_keys() before get keys"""
        if self.PUBLIC_KEY_FILE_PATH is not None:
            with open(self.PRIVATE_KEY_FILE_PATH, "r") as _file:
                return _file.read()
        else:
            private, public = self.generate_keys()
            return private

    def _to_format_for_encrypt(self, value):
        if isinstance(value, int):
            return six.binary_type(value)
        for str_type in six.string_types:
            if isinstance(value, str_type):
                return value.encode("utf8")
        if isinstance(value, six.binary_type):
            return value

    def rsa_long_encrypt(self, encryptor, message: str, length: int = 200):
        """
        The maximum length of a single encryption string is (key_size/8)-11
        100 for 1024bit certificate, 200 for 2048bit certificate
        """
        res = []
        for i in range(0, len(message), length):
            res.append(
                str(
                    pybase64.b64encode(
                        encryptor.encrypt(str.encode(message[i : i + length]))
                    ),
                    "utf-8",
                )
            )
        return "".join(res)

    def rsa_long_decrypt(self, decryptor, message: str, length: int = 344):
        """
        1024bit certificate uses 128, 2048bit certificate uses 256 bits
        length = 172 for 1024bit and 344 for 2048 bit
        """
        res = []
        for i in range(0, len(message), length):
            res.append(
                str(
                    decryptor.decrypt(pybase64.b64decode(message[i : i + length])),
                    "utf-8",
                )
            )
        return "".join(res)
