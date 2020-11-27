import xml.etree.cElementTree as ET
import pandas as pd
import os
import locale
import json
import sys
from .util import *



def getBounds(element):
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


def readXMLFile(osm_filename='map.osm'):
    bounds = default_bounds.copy()
    nodes = []
    ways = []
    relations = []

    osmtree = ET.ElementTree(file=osm_filename)
    osmnet = osmtree.getroot()
    for element in osmnet:
        if element.tag == 'bounds':
            bounds = getBounds(element)
        elif element.tag == 'node':
            nodes.append(element)
        elif element.tag == 'way':
            ways.append(element)
        elif element.tag == 'relation':
            relations.append(element)

    return bounds, nodes, ways, relations


def readJSONFile(folder, POIs):
    pointjson_path = os.path.join(folder,'point.geojson')
    if not os.path.exists(pointjson_path):
        print('cannot open file point.geojson')
        sys.exit()
    with open(pointjson_path) as json_file:
        pointdata = json.load(json_file)
        points = pointdata['features']

    linejson_path = os.path.join(folder,'line.geojson')
    if not os.path.exists(linejson_path):
        print('cannot open file line.geojson')
        sys.exit()
    with open(linejson_path) as json_file:
        linedata = json.load(json_file)
        lines = linedata['features']

    if not POIs:
        return points, lines, None

    areajson_path = os.path.join(folder,'area.geojson')
    if os.path.exists(areajson_path):
        with open(areajson_path) as json_file:
            areadata = json.load(json_file)
            areas = areadata['features']
    else:
        areas = None

    return points, lines, areas


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
