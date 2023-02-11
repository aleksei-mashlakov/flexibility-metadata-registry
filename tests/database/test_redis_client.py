import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
import numpy as np
import json
import requests
import yaml
import redis
import pandapower as pp
import uuid
import random

from interface.client import Transport
from interface.encryption import RSAEncryption
from database.manager import DataBaseManager
from network.pp_network import Network
from requests.structures import CaseInsensitiveDict


headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Content-Type"] = "application/json"

NGINX_URL="https://localhost:443"


def test_graph_buiding():
    config = yaml.full_load(open(os.getenv("CONFIG_FILE"), 'r'))['databases']['redis']
    DataBaseManager(config=config).graphstore.build_db_graph()

def test_MGMS_registration():
    print(os.getcwd())
    network_name = 'mv_oberrhein'
    net = Network().get_network(network_name, include_substations=True)
    trafos = np.random.choice(net.trafo.name, 2)

    for trafo in trafos:
        request = yaml.full_load(open('../config/thing_description_template.yaml', 'r'))
        id = str(uuid.uuid4())
        connection = net.trafo[net.trafo.name==trafo]['lv_bus'].values[0]
        request['id'] = request['id'] + id
        request['properties']['connection']['properties']['distributiontransformer']['value'] = str(trafo)
        request['properties']['connection']['properties']['connectionpoint']['value'] = int(connection)
        service_list =  [['seas:LoadShifting'],['seas:LoadShifting','seas:BalancingExecution'],['seas:BalancingExecution']]
        services = random.choice([item for item in service_list])
        request['properties']['flexibility']['properties']['services'] = services
        request['properties']['flexibility']['maximum'] = int(np.random.randint(0,500))
        print(id)
        #print(request)
        # DataBaseManager().handle_registration_request(request)
        #print(requests.post(NGINX_URL+"/registry/register", headers=headers, data=json.dumps(request), verify=False))
        #print(requests.post(NGINX_URL+"/registry/delete", headers=headers, data=json.dumps(request), verify=False))
        response = Transport().serve_request(url=NGINX_URL+"/registry/register",
                                            #body=RSAEncryption().encrypt(json.dumps(request)),
                                            body=json.dumps(request),
                                            ca_certs='../config/keys/ca-cert.pem',
                                            client_key='../config/keys/client-key.pem',
                                            client_cert='../config/keys/client-cert.pem')
        #print(json.loads(RSAEncryption().decrypt(response)))
        print(json.loads(response))
        # print(Transport().serve_request(url=NGINX_URL+"/registry/delete",
        #                                 body=request,
        #                                 ca_certs='../config/keys/ca-cert.pem',
        #                                 client_key='../config/keys/client-key.pem',
        #                                 client_cert='../config/keys/client-cert.pem')
        #                                 )
        #DataBaseManager().handle_update_request(request)
        #DataBaseManager().handle_delete_request(request)

def test_search_request():
    network_name = 'mv_oberrhein'
    net = Network().get_network(network_name, include_substations=True)
    trafos = np.random.choice(net.trafo.name, 2)

    for service in ['seas:LoadShifting','seas:BalancingExecution']:
        for trafo in trafos:
            print('Service {}, trafo {}'.format(service, trafo))
            request = yaml.full_load(open('../config/thing_search_template.yaml', 'r'))
            request['properties']['connection']['properties']['distributiontransformer']['value'] = str(trafo)
            request['properties']['service']['@type'] = str(service)
            #response_data = DataBaseManager().handle_search_request(request)
            # print(requests.post(NGINX_URL+"/registry/search", headers=headers, data=json.dumps(request)))
            #print(Transport().serve_request(url=NGINX_URL+"/registry/search", body=request))
            #print(response_data)

    request = yaml.full_load(open('../config/thing_search_template.yaml', 'r'))
    request['properties']['connection']['properties']['distributiontransformer']['value'] = str(trafo)
    request['properties']['service']['@type'] = str('')
    response = Transport().serve_request(url=NGINX_URL+"/registry/search",
                                        #body=RSAEncryption().encrypt(json.dumps(request)),
                                        body=json.dumps(request),
                                        ca_certs='../config/keys/ca-cert.pem',
                                        client_key='../config/keys/client-key.pem',
                                        client_cert='../config/keys/client-cert.pem')

    # response_data = DataBaseManager().handle_search_request(request)
    # print(Transport().serve_request(url=NGINX_URL+"/registry/search", body=request))
    #print(json.loads(RSAEncryption().decrypt(response)))
    print(json.loads(response))

def test_delete():
    try:
        config = yaml.full_load(open(os.getenv("CONFIG_FILE"), 'r'))['databases']['redis']
        DataBaseManager(config).graphstore.delete()
    except redis.exceptions.ResponseError as e:
        #print(e)
        pass

def test_server_stop():
    try:
        print(requests.post(NGINX_URL+"/shutdown", headers=headers, data={}))
        #print(Transport().serve_request(url=NGINX_URL+"/shutdown", body={}))
        #print(Transport().serve_request(url=NGINX_URL+"/shutdown", body={}))
    except Exception as e:
        print(e)
        pass

test_delete()
test_graph_buiding()
test_MGMS_registration()
test_search_request()
# test_delete()
# test_server_stop()
