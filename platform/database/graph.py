"""
This module controls Redis graph database.
"""

__version__ = "0.1"
__author__ = "Aleksei Mashlakov"

import os
import sys
from dataclasses import dataclass
from typing import ClassVar

from network.pp_network import Network
from redis import Redis
from redisgraph import Edge, Graph, Node, Path

try:
    import logging

    from __main__ import logger_name

    log = logging.getLogger(logger_name)
except Exception as e:
    log = logging.getLogger("PLATFORM")


@dataclass
class GraphDB(object):

    database: Redis
    name: str = "mv_oberrhein"

    def __post_init__(self):
        self.graph = Graph(self.name, self.database)

    def delete(self):
        # All done, remove graph.
        self.graph.delete()

    def write_data(self, request_data):
        """ """
        try:
            # query = "MATCH (r:Resourse { id: '%s' }) RETURN r.id" % request_data['id']
            # result = self.graph.query(query)
            # result.pretty_print()
            # if not result.result_set:
            connection_properties = request_data["properties"]["connection"][
                "properties"
            ]
            connection_point = connection_properties["connectionpoint"]["value"]
            transformer = connection_properties["distributiontransformer"]["value"]
            node = Node(
                label="Resourse",
                properties={
                    "id": request_data["id"],
                    "type": request_data["@type"],
                    "connectionpoint": connection_point,
                    "distributiontransformer": transformer,
                },
            )
            self.graph.add_node(node)

            resource_flexibility = {
                your_key: request_data["properties"]["flexibility"][your_key]
                for your_key in ["minimum", "maximum", "unit"]
            }

            for service in request_data["properties"]["flexibility"]["properties"][
                "services"
            ]:
                service_node = Node(
                    label="Service",
                    properties={
                        **{"type": service, "providedby": request_data["id"]},
                        **resource_flexibility,
                    },
                )
                self.graph.add_node(service_node)
                new_edge = Edge(node, "offersService", service_node)
                self.graph.add_edge(new_edge)
            self.graph.flush()

            query = """MATCH (n:Bus { index: %d})
                       MATCH (m:Resourse { id: '%s' })
                       MERGE (n)-[r:isConnectedTo]->(m)""" % (
                connection_point,
                request_data["id"],
            )
            result = self.graph.query(query)
            # result.pretty_print()
        except Exception as e:
            raise (e)
        return

    def read_data(self, request_data):
        service = request_data["properties"]["service"]["@type"]
        connection_properties = request_data["properties"]["connection"]["properties"]
        connection_point_dict = connection_properties["distributiontransformer"]
        if connection_point_dict:
            connection_trafo = connection_point_dict["value"]
        if service == "seas:BalancingExecution":
            query = (
                "MATCH (r:Resourse)-[o:offersService]->(s:Service) \
                     WHERE  s.type='%s' \
                     RETURN r.id"
                % service
            )
        elif service == "seas:LoadShifting":
            query = (
                "MATCH (r:Resourse)-[o:offersService]->(s:Service) \
                     WHERE  r.distributiontransformer='%s' AND s.type='%s' \
                     RETURN r.id"
                % (connection_trafo, service)
            )
        else:  # search by type
            query = "MATCH (r:Resourse) \
                     WHERE  r.type='sapi:MicroGridManagementSystem' OR \
                            r.type='sapi:ElectricityManagementEntity'\
                     RETURN r.id"
        result = self.graph.query(query)
        # result.pretty_print()

        indexes = []
        for row in result.result_set:
            for idx, cell in enumerate(row):
                indexes.append(cell)

        # Iterate through resultset
        # for record in result.result_set:
        #     path = record[0]
        #     print(path)

        return indexes

    def update_data(self, request_data):
        connection_properties = request_data["properties"]["connection"]["properties"]
        connection_point = connection_properties["connectionpoint"]["value"]
        transformer = connection_properties["distributiontransformer"]["value"]
        query = (
            "MATCH (r:Resourse { id: '%s' }) \
                 SET r.type='%s'"
            % (request_data["id"], request_data["@type"])
        )
        # AND r.connectionpoint=%d AND \
        # r.distributiontransformer='%s'" \
        # connection_point, transformer)
        result = self.graph.query(query)
        # result.pretty_print()
        return

    def delete_data(self, request_data):
        query = (
            "MATCH (b:Bus)-[r1:isConnectedTo]->(r:Resourse {id:'%s'})-[r2:offersService]->(s:Service) \
                 DELETE r, r1, r2, s"
            % request_data["id"]
        )
        result = self.graph.query(query)
        # result.pretty_print()
        return

    def build_db_graph(self):
        """ """
        net = Network().get_network(self.name, include_substations=True)
        networkx = Network().get_network_graph(self.name, include_substations=True)
        trafos = list(
            net.trafo.loc[:, ["hv_bus", "lv_bus"]].itertuples(index=False, name=None)
        )
        lines = list(
            net.line.loc[:, ["from_bus", "to_bus"]].itertuples(index=False, name=None)
        )
        created_nodes = {}
        reverse = False
        for edge in networkx.edges(data=False):
            if edge in lines:
                df = net.line[
                    (net.line.loc[:, "from_bus"] == edge[0])
                    & (net.line.loc[:, "to_bus"] == edge[1])
                ].dropna()
                # label = 'isConnectedTo' #df['name'].values[0].replace(' ','_')
                properties = {
                    **{"index": df.index[0]},
                    **df.iloc[0, :].to_dict(),
                    **{"type": "line"},
                }
            elif (edge[1], edge[0]) in lines:
                df = net.line[
                    (net.line.loc[:, "from_bus"] == edge[1])
                    & (net.line.loc[:, "to_bus"] == edge[0])
                ].dropna()
                # label = 'isConnectedTo' #df['name'].values[0].replace(' ','_')
                properties = {
                    **{"index": df.index[0]},
                    **df.iloc[0, :].to_dict(),
                    **{"type": "line"},
                }
                reverse = True
            elif edge in trafos:
                df = net.trafo[
                    (net.trafo.loc[:, "hv_bus"] == edge[0])
                    & (net.trafo.loc[:, "lv_bus"] == edge[1])
                ].dropna(axis=1)
                # label = 'isConnectedTo' #df['name'].values[0].replace(' ','_').replace('/','_')
                properties = {
                    **{"index": df.index[0]},
                    **df.iloc[0, :].to_dict(),
                    **{"type": "trafo"},
                }
            elif (edge[1], edge[0]) in trafos:
                df = net.trafo[
                    (net.trafo.loc[:, "hv_bus"] == edge[1])
                    & (net.trafo.loc[:, "lv_bus"] == edge[0])
                ].dropna(axis=1)
                # label = 'isConnectedTo' #df['name'].values[0].replace(' ','_').replace('/','_')
                properties = {
                    **{"index": df.index[0]},
                    **df.iloc[0, :].to_dict(),
                    **{"type": "trafo"},
                }
                reverse = True
            else:
                continue
            for node in edge:
                if not node in created_nodes.keys():
                    df = net.bus.loc[node, :].dropna()
                    node_properties = {
                        **{"index": df.name},
                        **df.to_dict(),
                        **{"type": "bus"},
                    }
                    new_node = Node(label="Bus", properties=node_properties)
                    self.graph.add_node(new_node)
                    created_nodes[node] = new_node
                else:
                    pass
            if reverse:
                new_edge = Edge(
                    created_nodes[edge[1]],
                    "isConnectedTo",
                    created_nodes[edge[0]],
                    properties=properties,
                )
                self.graph.add_edge(new_edge)
                reverse = False
            else:
                new_edge = Edge(
                    created_nodes[edge[0]],
                    "isConnectedTo",
                    created_nodes[edge[1]],
                    properties=properties,
                )
                self.graph.add_edge(new_edge)
        self.graph.commit()
        return
