import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))
import yaml

from virtualthing.basemodel import ThingDescription

def test_base_model():
    request = yaml.full_load(open('../config/thing_description_template.yaml', 'r'))
    thing = ThingDescription(**request)
    print(thing)


test_base_model()
