#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2020 German Aerospace Center (DLR) and others.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# https://www.eclipse.org/legal/epl-2.0/
# This Source Code may also be made available under the following Secondary
# Licenses when the conditions for such availability set forth in the Eclipse
# Public License 2.0 are satisfied: GNU General Public License, version 2
# or later which is available at
# https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later

# @file    osmGet.py
# @author  Daniel Krajzewicz
# @author  Jakob Erdmann
# @author  Michael Behrisch
# @date    2009-08-01


import os
import http.client as httplib
import urllib.parse as urlparse
import base64



_url = "www.overpass-api.de/api/interpreter"
# alternatives: overpass.kumi.systems/api/interpreter, sumo.dlr.de/osm/api/interpreter


def _readCompressed(conn, urlpath, query, filename):
    conn.request("POST", "/" + urlpath, """
    <osm-script timeout="240" element-limit="1073741824">
    <union>
       %s
       <recurse type="node-relation" into="rels"/>
       <recurse type="node-way"/>
       <recurse type="way-relation"/>
    </union>
    <union>
       <item/>
       <recurse type="way-node"/>
    </union>
    <print mode="body"/>
    </osm-script>""" % query)
    response = conn.getresponse()
    # print(response.status, response.reason)
    if response.status == 200:
        print('valid reponses got from API server.')
        print('receving data...')
        out = open(filename, "wb")
        out.write(response.read())
        out.close()
        print(f'map data has been written to {filename}')


def downloadOSMData(area_id, output_filename='map.osm', url=_url):
    """
    Download OpenStreetMap data via overpass API

    Parameters
    ----------
    area_id: int
        relation_id of the area of interest
    output_filename: int
        full path where the downloaded network will be stored
    url: int
        OpenStreetMap API url

    Returns
    -------
    None
    """

    file_name, file_extension = os.path.splitext(output_filename)
    if not file_extension:
        print(f'WARNING: no file extension in output_filename {output_filename}, output_filename is changed to {file_name}.osm')
        output_filename = f'{file_name}.osm'
    elif file_extension not in ['.osm', '.xml']:
        print(f'WARNING:  the file extension in output_filename {output_filename} is not supported, output_filename is changed to {file_name}.osm')
        output_filename = f'{file_name}.osm'

    if "http" in url:
        url = urlparse.urlparse(url)
    else:
        url = urlparse.urlparse("https://" + url)
    if os.environ.get("https_proxy") is not None:
        headers = {}
        proxy_url = urlparse.urlparse(os.environ.get("https_proxy"))
        if proxy_url.username and proxy_url.password:
            auth = '%s:%s' % (proxy_url.username, proxy_url.password)
            headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(auth)
        conn = httplib.HTTPSConnection(proxy_url.hostname, proxy_url.port)
        conn.set_tunnel(url.hostname, 443, headers)
    else:
        if url.scheme == "https":
            conn = httplib.HTTPSConnection(url.hostname, url.port)
        else:
            conn = httplib.HTTPConnection(url.hostname, url.port)

    if area_id < 3600000000:
        area_id += 3600000000
    _readCompressed(conn, url.path, '<area-query ref="%s"/>' % area_id, output_filename)

    conn.close()
