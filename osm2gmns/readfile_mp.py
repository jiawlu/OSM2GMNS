import csv
import os
from .util import *
import osmium
from collections import namedtuple
import multiprocessing as mp


Node = namedtuple('Node', ('id', 'tags', 'lonlat'))
Way = namedtuple('Way', ('id', 'tags', 'refs'))
Relation = namedtuple('Relation', ('id', 'tags', 'members'))


def collectNodes1(filename):
    class NodeHandler(osmium.SimpleHandler):
        def __init__(self):
            osmium.SimpleHandler.__init__(self)
            self.nodes = []

        def node(self, n):
            node_id = n.id
            if node_id % 3 == 1:
                lonlat = (n.location.lon, n.location.lat)
                tags = {tag.k: tag.v for tag in n.tags}
                node = Node(node_id, tags, lonlat)
                self.nodes.append(node)

    node_handler = NodeHandler()
    node_handler.apply_file(filename)
    return 'n', node_handler.nodes


def collectNodes2(filename):
    class NodeHandler(osmium.SimpleHandler):
        def __init__(self):
            osmium.SimpleHandler.__init__(self)
            self.nodes = []

        def node(self, n):
            node_id = n.id
            if node_id % 3 == 2:
                lonlat = (n.location.lon, n.location.lat)
                tags = {tag.k: tag.v for tag in n.tags}
                node = Node(node_id, tags, lonlat)
                self.nodes.append(node)

    node_handler = NodeHandler()
    node_handler.apply_file(filename)
    return 'n', node_handler.nodes


def collectNodes3(filename):
    class NodeHandler(osmium.SimpleHandler):
        def __init__(self):
            osmium.SimpleHandler.__init__(self)
            self.nodes = []

        def node(self, n):
            node_id = n.id
            if node_id % 3 == 0:
                lonlat = (n.location.lon, n.location.lat)
                tags = {tag.k: tag.v for tag in n.tags}
                node = Node(node_id, tags, lonlat)
                self.nodes.append(node)

    node_handler = NodeHandler()
    node_handler.apply_file(filename)
    return 'n', node_handler.nodes


def collectWaysRelations(filename):
    class WayRelationHandler(osmium.SimpleHandler):
        def __init__(self):
            osmium.SimpleHandler.__init__(self)
            self.ways = []
            self.relations = []

        def way(self, w):
            way_id = w.id
            refs = [node.ref for node in w.nodes]
            tags = {tag.k: tag.v for tag in w.tags}
            way = Way(way_id, tags, refs)
            self.ways.append(way)

        def relation(self, r):
            relation_id = r.id
            members = [(member.ref, member.type, member.role) for member in r.members]
            tags = {tag.k: tag.v for tag in r.tags}
            relation = Relation(relation_id, tags, members)
            self.relations.append(relation)

    wr_handler = WayRelationHandler()
    wr_handler.apply_file(filename)
    return 'wr', wr_handler.ways, wr_handler.relations


def readOSMFile(filename):

    bounds = default_bounds

    f = osmium.io.Reader(filename)
    header = f.header()
    print('Bbox:', header.box())

    results = []
    p = mp.Pool(4)
    results.append(p.apply_async(collectNodes1, (filename,)))
    results.append(p.apply_async(collectNodes2, (filename,)))
    results.append(p.apply_async(collectNodes3, (filename,)))
    results.append(p.apply_async(collectWaysRelations, (filename,)))
    p.close()
    p.join()

    nodes, ways, relations = [], [], []
    for result in results:
        result_tuple = result.get()
        if result_tuple[0] == 'n':
            nodes += result_tuple[1]
        elif result_tuple[0] == 'wr':
            ways = result_tuple[1]
            relations = result_tuple[2]

    return {'bounds':bounds, 'nodes':nodes, 'ways':ways, 'relations':relations}



def readCSVFile(folder, encoding):
    node_filepath = os.path.join(folder,'node.csv')
    link_filepath = os.path.join(folder,'link.csv')

    if encoding is None:
        nfin = open(node_filepath, 'r')
        lfin = open(link_filepath, 'r')
    else:
        nfin = open(node_filepath, 'r', encoding=encoding)
        lfin = open(link_filepath, 'r', encoding=encoding)

    reader = csv.DictReader(nfin)
    node_data = [line for line in reader]
    nfin.close()

    reader = csv.DictReader(lfin)
    link_data = [line for line in reader]
    lfin.close()

    return node_data, link_data

