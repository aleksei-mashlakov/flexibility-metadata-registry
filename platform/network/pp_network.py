
"""
This module models physical power system network using pandapower network.
"""

__version__ = '0.1'
__author__ = 'Aleksei Mashlakov'

import os
import sys
import yaml
from dataclasses import dataclass

from pandapower.topology import create_nxgraph
from importlib import import_module

try:
    import logging
    from __main__ import logger_name
    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")

@dataclass
class Network:

    def get_network_graph(self, model: str, respect_switches: bool = True, **kwargs):
        """ """
        log.debug("making_graph, network={}".format(model))
        net = self.get_network(model, **kwargs)
        graph = create_nxgraph(net, respect_switches=respect_switches)
        return graph

    def get_network(self, model: str, **kwargs):
        """ """
        log.debug("making_network, network={}".format(model))
        module = import_module(f"pandapower.networks.{model}")
        net = getattr(module, model)(**kwargs)
        return net
