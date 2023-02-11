import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docker_containers')))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'docker_containers')))


from loadtesting.app.locustfile import Service
from loadtesting.app.locustfile import MgmsThing, AmsThing

def test_services():
    mgmss = Service(services=['seas:LoadShifting',
                              'seas:BalancingExecution'])
    amss = Service(services=['seas:LoadShifting',
                             'seas:BalancingExecution'])
    for i in range(5):
        print(f"MGMS services: {mgmss.get_random_service_combination()}")
        print(f"AMS services: {amss.get_random_service()}")

def test_things():
    for i in range(5):
        mgms = MgmsThing()
        print(f"{mgms.role} {mgms.id}:")
        print(mgms.td['id'])
        print(type(mgms.td['id']))
        #print(mgms.get())

        ams = AmsThing()
        print(f"{ams.role} {ams.id}:")
        print(ams.td['id'])
        print(type(ams.td['id']))
        #print(ams.get())

test_services()
test_things()
