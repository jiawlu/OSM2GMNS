import pandas as pd
import os
import locale
from .util import *


def _getBounds(element):
    try:
        minlat = float(element.attrib['minlat'])
    except KeyError:
        minlat = -90.0
    try:
        minlon = float(element.attrib['minlon'])
    except KeyError:
        minlon = -180.0
    try:
        maxlat = float(element.attrib['maxlat'])
    except KeyError:
        maxlat = 90.0
    try:
        maxlon = float(element.attrib['maxlon'])
    except KeyError:
        maxlon = 180.0
    return {'minlat':minlat, 'minlon':minlon, 'maxlat':maxlat, 'maxlon':maxlon}


def readXMLFile(osm_filename):
    import xml.etree.cElementTree as ET
    from .file import Node, Way, Relation

    bounds = default_bounds.copy()
    nodes, ways, relations = [], [], []

    osmtree = ET.ElementTree(file=osm_filename)
    osmnet = osmtree.getroot()
    for element in osmnet:
        if element.tag == 'bounds':
            bounds = _getBounds(element)

        elif element.tag == 'node':
            node_id = element.attrib['id']
            lonlat = (float(element.attrib['lon']),float(element.attrib['lat']))
            tags = {}
            for info in element:
                if info.tag == 'tag':
                    tags[info.attrib['k']] = info.attrib['v']

            node = Node(node_id, tags, lonlat)
            nodes.append(node)

        elif element.tag == 'way':
            way_id = element.attrib['id']
            refs = []
            tags = {}
            for info in element:
                if info.tag == 'nd':
                    ref_node_id = info.attrib['ref']
                    refs.append(ref_node_id)
                elif info.tag == 'tag':
                    tags[info.attrib['k']] = info.attrib['v']

            way = Way(way_id,tags, refs)
            ways.append(way)

        elif element.tag == 'relation':
            relation_id = element.attrib['id']
            members = []
            tags = {}
            for info in element:
                if info.tag == 'member':
                    member_type = info.attrib['type']
                    ref_id = info.attrib['ref']
                    member_role = info.attrib['role']
                    members.append((ref_id,member_type,member_role))
                elif info.tag == 'tag':
                    tags[info.attrib['k']] = info.attrib['v']

            relation = Relation(relation_id, tags, members)
            relations.append(relation)

    return {'bounds':bounds, 'nodes':nodes, 'ways':ways, 'relations':relations}


def readPBFFile(pbf_filename):
    from .file import File, Node, Way, Relation

    bounds = default_bounds.copy()
    nodes, ways, relations = [], [], []
    pbf_data = File(pbf_filename)

    for item in pbf_data:
        if isinstance(item,Node):
            nodes.append(item)
        elif isinstance(item, Way):
            ways.append(item)
        elif isinstance(item, Relation):
            relations.append(item)
        else:
            print('unsupported type')

    return {'bounds':bounds, 'nodes':nodes, 'ways':ways, 'relations':relations}


def readCSVFile(folder):
    if folder:
        node_filepath = os.path.join(folder,'node.csv')
        link_filepath = os.path.join(folder,'link.csv')
    else:
        node_filepath = 'node.csv'
        link_filepath = 'link.csv'

    local_encoding = locale.getdefaultlocale()
    try:
        node_data = pd.read_csv(node_filepath,dtype={'osm_node_id':str})
    except UnicodeDecodeError:
        node_data = pd.read_csv(node_filepath,dtype={'osm_node_id':str},encoding=local_encoding[1])
    try:
        link_data = pd.read_csv(link_filepath,dtype={'osm_way_id':str})
    except UnicodeDecodeError:
        link_data = pd.read_csv(link_filepath,dtype={'osm_way_id':str},encoding=local_encoding[1])

    return node_data, link_data
