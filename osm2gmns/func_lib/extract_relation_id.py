# -*- coding:utf-8 -*-
##############################################################
# Created Date: Monday, May 29th 2023
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################


import requests
import json
import urllib
import os
from typing import Union
from pathlib import Path


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

        # the default path to save/load global country, state, and city information
        self._path_global_rel_id = self._path2linux(os.path.join(
            Path(__file__).resolve().parent, "global_rel_id.json"))

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
        # 3. If url_json is empty, Search locally, return None if not found locally

        for i in self._url_json:
            if i["osm_type"] == "relation":
                return i["osm_id"]

        if len(self.rel_id_info) > 0:
            return self.rel_id_info[0]["osm_id"]

        return self._find_local_rel_id()

    @property
    def rel_id_info(self):
        # show detailed information of the relation id
        return self._url_json if len(self._url_json) < self._max_show else self._url_json[:self._max_show]

        # convert OS path to standard linux path
    def _path2linux(self, path: Union[str, Path]) -> str:
        """Convert a path to a linux path, linux path can run in windows, linux and mac"""
        try:
            return path.replace("\\", "/")
        except Exception:
            return str(path).replace("\\", "/")

    def _find_local_rel_id(self) -> str:

        # Step 0 load the global country, state, and city information locally
        try:
            with open(self._path_global_rel_id, "r") as f:
                self._global_rel_id = json.load(f)
        except Exception:
            github_url = "https://raw.githubusercontent.com/xyluo25/OSM2GMNS/master/osm2gmns/func_lib/global_rel_id.json"
            self._global_rel_id = json.loads(requests.get(github_url).text)

        # if we can not load dictionary, return None
        if isinstance(self._global_rel_id, dict):
            return None

        search_name = self._poi_name.split(",")[0].strip()
        if search_name == self._poi_name:
            search_name = self._poi_name.split(" ")[0].strip()

        # Step 1 Find the country start with the input characters
        start_with_country = [country_name for country_name in self._global_rel_id["country"].keys(
        ) if country_name.lower().startswith(search_name.lower())][:self._max_show]

        # Step 2 Find the state start with the input characters
        start_with_state = [state_name for state_name in self._global_rel_id["state"].keys(
        ) if state_name.lower().startswith(search_name.lower())][:self._max_show]

        # Step 3 Find the city start with the input characters
        start_with_city = [city_name for city_name in self._global_rel_id["city"].keys(
        ) if city_name.lower().startswith(search_name.lower())][:self._max_show]

        # Step 4 Format the results
        formatted_str = ""
        if start_with_city:
            formatted_str += "City:\n"
            for city_name in start_with_city:
                formatted_str += f"""{city_name}, {self._global_rel_id["city"][city_name]["state"]}, {self._global_rel_id["city"][city_name]["country"]}, rel_id: {self._global_rel_id["city"][city_name]["osm_id"]} \n"""

        if start_with_state:
            formatted_str += "State:\n"
            for state_name in start_with_state:
                formatted_str += f"""{state_name}, {self._global_rel_id["state"][state_name]["country"]}, rel_id: {self._global_rel_id["state"][state_name]["osm_id"]} \n"""

        if start_with_country:
            formatted_str += "Country:\n"
            for country_name in start_with_country:
                formatted_str += f"""{country_name}, rel_id: {self._global_rel_id["country"][country_name]["osm_id"]} \n"""

        if formatted_str:

            formatted_str = f"""Info:\nWe can not search rel_id from web with place of interest: {self._poi_name} \nSearch locally with country, state and city startswith {search_name}:\n""" + formatted_str

            formatted_str += "You can replace your place of interest with local results above to get the rel_id\n"
            print(formatted_str)

        return None


if __name__ == "__main__":

    rel = OSM_RelationID_Finder("tem, Az, USA")
    print(rel.rel_id)
