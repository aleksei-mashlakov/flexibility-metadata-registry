import os
import sys
import pandapower as pp
# Explicitly set path so don't need to run setup.py - if we have multiple copies of the code we would otherwise need
# to setup a separate environment for each to ensure the code pointers are correct.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'platform')))  # noqa

# from pandas.util.testing import assert_frame_equal
from network.pp_network import Network


def test_mv_network_creation():
    # print(os.getcwd())
    net = Network().get_network('mv_oberrhein', include_substations=True)
    assert len(net.bus) == 320
    assert len(net.trafo) == 143


def test_graph_creation():
    # print(os.getcwd())
    networkx = Network().get_network_graph('mv_oberrhein',
                                            respect_switches=True,
                                            include_substations=True)
    assert len(networkx.edges()) == 318
    assert len(networkx.nodes()) == 320

# test_mv_network_creation()
# test_graph_creation()
