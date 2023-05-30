# -*- coding:utf-8 -*-
##############################################################
# Created Date: Monday, May 29th 2023
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################


import requests
import json
import urllib


class OSM_RelationID_Finder:
    """A class to find the osm relation id of a place of interest globally
       Use the Nominatim API to find the relation id of a place of interest
    """
    def __init__(self, poi_name: str):
        """
        Args:
            poi_name (str): the name of the place of interest,
                            e.g., "Arizona State University"
                            e.g., "Tempe, Arizona, USA"
                            e.g., "Arizona, USA"
        """
        self._poi_name = poi_name
        self._url_json = self._get_url_data()

        # maximum number of results to show
        self._max_show = 5

    def _get_url_data(self):
        # prepare url
        base_url = 'https://nominatim.openstreetmap.org/search?'
        params = {"q": self._poi_name, "format": "json"}
        url = base_url + urllib.parse.urlencode(params)

        # get data from url using requests
        url_res = requests.get(url)
        url_json = json.loads(url_res.text)
        return url_json

    @property
    def rel_id(self):
        # Three logic to find the relation id
        # 1. If relation id exist, return the relation id
        # 2. If relation id does not exist, check whether url_json is empty,
        #    if not, return relation id of the first element
        # 3. If url_json is empty, return None
        return next(
            (i["osm_id"] for i in self._url_json if i["osm_type"] == "relation"),
            self.rel_id_info[0]["osm_id"] if len(self.rel_id_info) > 0 else None,
        )

    @property
    def rel_id_info(self):
        # show detailed information of the relation id
        return self._url_json if len(self._url_json) < self._max_show else self._url_json[:self._max_show]


if __name__ == "__main__":

    rel = OSM_RelationID_Finder("Arizona State University")
    print(rel.rel_id)