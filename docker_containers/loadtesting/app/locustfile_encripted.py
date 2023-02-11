import json
import os
import random
import sys
import uuid
from abc import ABC
from dataclasses import dataclass, field
from enum import Enum, auto
from itertools import combinations
from json import JSONDecodeError
from typing import Dict, List

import numpy as np
import yaml
from interface.encryption import RSAEncryption
from locust import HttpUser, between, task


def get_json_headers(headers_type: str = "application/json") -> Dict:
    """ Creates JSON headers. """
    return {key:headers_type for key in ["Accept","Content-Type"]}

@dataclass
class Role(Enum):
    """ """

    MGMS = auto()
    AMS = auto()

@dataclass
class Service(ABC):
    """  """

    services: List

    def get_random_service_combination(self) -> List:
        return random.choice(self.make_combinations())

    def get_random_service(self) -> str:
        return random.choice(self.services)

    def make_combinations(self) -> List:
        return sum([list(map(list, combinations(self.services, i))) for i in range(len(self.services) + 1)], [])

@dataclass
class Thing(ABC):

    trafos: List = field(default_factory=lambda: [x for x in range(143)])

@dataclass
class MgmsThing(Thing):

    def __post_init__(self):
        super().__init__()
        self.role = Role.MGMS
        self.td = yaml.full_load(open(os.getenv('THING_CONFIG_FILE'), 'r'))
        trafo = str(np.random.choice(self.trafos))
        with open(os.getenv('NET_CONNECTIONS'), 'r', encoding ='utf8') as json_file:
            trafo_d = json.load(json_file)[trafo]
        self.td['id'] = self.td['id'] + str(uuid.uuid4())
        self.td['properties']['connection']['properties']['distributiontransformer']['value'] = trafo_d['name']
        self.td['properties']['connection']['properties']['connectionpoint']['value'] = trafo_d['lv_bus']
        service = Service(services=[
                                    'seas:LoadShifting',
                                    'seas:BalancingExecution'
                                    ]
                         )
        self.td['properties']['flexibility']['properties']['services'] = service.get_random_service_combination()
        self.td['properties']['flexibility']['maximum'] = int(np.random.randint(0, 500))

    def get(self):
        return self.td['id'], self.td

@dataclass
class AmsThing(Thing):

    def __post_init__(self):
        super().__init__()
        self.role = Role.AMS
        self.td = yaml.full_load(open(os.getenv('THING_SEARCH_FILE'), 'r'))
        self.td['id'] = self.td['id'] + str(uuid.uuid4())
        service = Service(services=['seas:LoadShifting',
                                    'seas:BalancingExecution'
                                    ]
                         )
        self.td['properties']['service']['@type'] = service.get_random_service()

        if service == 'seas:LoadShifting':
            trafo = str(np.random.choice(self.trafos))
            with open(os.getenv('NET_CONNECTIONS'), 'r', encoding ='utf8') as json_file:
                trafo_d = json.load(json_file)[trafo]
            self.td['properties']['connection']['properties']['distributiontransformer']['value'] = trafo_d['name']

    def get(self):
        return self.td['id'], self.td

class QuickstartUser(HttpUser):

    registered_things : Dict = {}
    host =  os.getenv('REGISTRY_HOST')
    wait_time = between(0.1, 1)
    path_to_cert = os.getenv('CLIENT_CERT')
    path_to_key = os.getenv('CLIENT_KEY')


    @task(5)
    def register(self):
        id, td = MgmsThing().get()
        with self.client.post("/registry/register",
                              headers=get_json_headers(),
                              #data=json.dumps(td),
                              data=RSAEncryption().encrypt(json.dumps(td)),
                              verify=False,
                              cert=(
                                   self.path_to_cert,
                                   self.path_to_key
                                   ),
                              catch_response=True
                              ) as response:
            try:
                response_content = json.loads(RSAEncryption().decrypt(response.content))
                if response_content["success"] != True:
                    response.failure("Did not get expected value in success")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'greeting'")
            else:
                self.registered_things[id] = td

    @task(3)
    def update(self):
        if not len(self.registered_things) == 0:
            for id, td in random.sample(self.registered_things.items(),
                                        int(float(os.getenv('UPDATE_PERCENT'))\
                                        *len(self.registered_things))
                                        ):
                with self.client.post("/registry/update",
                                      headers=get_json_headers(),
                                      data=RSAEncryption().encrypt(json.dumps(td)),
                                      verify=False,
                                      cert=(
                                           self.path_to_cert,
                                           self.path_to_key
                                           ),
                                      catch_response=True
                                      ) as response:
                    try:
                        response_content = json.loads(RSAEncryption().decrypt(response.content))
                        if response_content["success"] != True:
                            response.failure("Did not get expected value in success")
                    except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                    except KeyError:
                        response.failure("Response did not contain expected key 'greeting'")

    @task(5)
    def search(self):
        id, td = AmsThing().get()
        with self.client.post("/registry/search",
                              headers=get_json_headers(),
                              data=RSAEncryption().encrypt(json.dumps(td)),
                              verify=False,
                              cert=(
                                   self.path_to_cert,
                                   self.path_to_key
                                   ),
                              catch_response=True
                              ) as response:
            try:
                response_content = json.loads(RSAEncryption().decrypt(response.content))
                if response_content == {"success":False}:
                    response.failure("Did not get expected value in success")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'greeting'")

    @task(1)
    def delete(self):
        if not len(self.registered_things) == 0:
            for id, td in random.sample(self.registered_things.items(), 1
                                        #int(float(os.getenv('DELETE_PERCENT'))\
                                        #*len(self.registered_things))
                                        ):
                with self.client.post("/registry/register",
                                      headers=get_json_headers(),
                                      data=RSAEncryption().encrypt(json.dumps(td)),
                                      verify=False,
                                      cert=(
                                           self.path_to_cert,
                                           self.path_to_key
                                           ),
                                      catch_response=True
                                      ) as response:
                    try:
                        response_content = json.loads(RSAEncryption().decrypt(response.content))
                        if response_content["success"] != True:
                            response.failure("Did not get expected value in success")
                    except JSONDecodeError:
                        response.failure("Response could not be decoded as JSON")
                    except KeyError:
                        response.failure("Response did not contain expected key 'greeting'")
                    else:
                        if id in self.registered_things:
                            del self.registered_things[id]
