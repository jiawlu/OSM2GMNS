# -*- coding:utf-8 -*-
# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2020/11/3 23:24
# @desc         [script description]


import xml.etree.cElementTree as ET
import pandas as pd
import os


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
    # print(f'Loaing Network Data from ({osm_filename})')
    osmtree = ET.ElementTree(file=osm_filename)

    bounds = {'minlat':-90.0, 'minlon':-180.0, 'maxlat':90.0, 'maxlon':180.0}
    nodes = []
    ways = []

    osmnet = osmtree.getroot()
    for element in osmnet:
        if element.tag == 'bounds':
            bounds = getBounds(element)
        elif element.tag == 'node':
            nodes.append(element)
        elif element.tag == 'way':
            ways.append(element)

    return bounds, nodes, ways


def readCSVFile(folder):
    if folder:
        node_filepath = os.path.join(folder,'node.csv')
        link_filepath = os.path.join(folder,'link.csv')
    else:
        node_filepath = 'node.csv'
        link_filepath = 'link.csv'

    node_data = pd.read_csv(node_filepath)
    link_data = pd.read_csv(link_filepath)

    return node_data, link_data


if __name__ == '__main__':
    readXMLFile()
