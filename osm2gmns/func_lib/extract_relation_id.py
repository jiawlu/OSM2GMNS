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


class OSMRelationIDFinder:
    """A class to find the osm relation id of a place of interest globally
       Use the Nominatim API to find the relation id of a place of interest

    Args:
        poi_name (str): the name of the place of interest,
            e.g., "Arizona State University"
            e.g., "Tempe, Arizona, USA"
            e.g., "Arizona, USA"

    Example:
    >>> import osm2gmns as og
    >>> rel = og.OSM_RelationID_Finder("Arizona State University")
    >>> rel.rel_id
        Info: Found relation id 3444656 from web
        Info: location of the place of interest:
        {
            "place_id": 318528634,
            "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "osm_type": "relation",
            "osm_id": 3444656,
            "lat": "33.4213174",
            "lon": "-111.93316305413154",
            "class": "amenity",
            "type": "university",
            "place_rank": 30,
            "importance": 0.5547365758311374,
            "addresstype": "amenity",
            "name": "Arizona State University",
            "display_name": "Arizona State University, 1151, South Forest Avenue, Tempe Junction, Tempe, Maricopa County, Arizona, 85281, United States",
            "boundingbox": [
                "33.4102062",
                "33.4329786",
                "-111.9411651",
                "-111.9092447"
            ]
        }
    3444656

    # download the corresponding osm file
    >>> og.downloadOSMData(rel.rel_id, 'asu.osm')

    """

    def __init__(self, poi_name: str) -> None:

        self.poi_name = poi_name
        self.__url_json = self.__get_url_data()

        # maximum number of results to show
        # if parameter will applied in function rel_id_info
        # if the number of results is greater than _max_show, only show the first _max_show results
        self._max_show = 5

        # TODO: Unable to find the relation id locally, search from the web
        # the default path to save/load global country, state, and city information
        self._path_global_rel_id = self.__path2linux(os.path.join(
            Path(__file__).resolve().parent.parent.parent, "dependencies/global_rel_id.json"))

    def __get_url_data(self) -> dict:
        # prepare url
        base_url = 'https://nominatim.openstreetmap.org/ui/search?'

        params = {"q": self.poi_name, "format": "json"}

        url = base_url + urllib.parse.urlencode(params)

        # get data from url using requests
        try:
            url_res = requests.get(url)
            url_json = json.loads(url_res.text)
            return url_json
        except Exception:
            return {}

    @property
    def rel_id(self) -> Union[float, None]:
        # Three logic to find the relation id
        # 1. Search from web, if relation id exist, return the relation id
        # 2. If relation id does not exist
        #    check whether url_json (result from web) is empty,
        #    if not, return relation id of the first element
        # 3. If url_json is empty, Search locally, return None if not found locally

        for i in self.__url_json:
            if i["osm_type"] == "relation":
                print(f"  Info: Found relation id {i['osm_id']} from web")
                print("  Info: location of the place of interest:")
                print(json.dumps(i, indent=4))
                return i["osm_id"]

        if len(self.rel_id_info) > 0:
            print("  Info: Could not find relation id directly from web")
            print(f"  but there is a possible relation id {self.rel_id_info[0]['osm_id']} from web")
            print("  or you can find more related ids: rel.rel_id_info")
            print(f"Detailed info for {self.rel_id_info[0]['osm_id']}: {json.dumps(self.rel_id_info[0], indent=4)}\n")
            return self.rel_id_info[0]["osm_id"]

        print("  Info: Could not find relation id from web: https://nominatim.openstreetmap.org/ui/search.html")
        print("  This might because the server blocked this request for many requests at the same time \n")
        return self.__find_local_rel_id()

    @property
    def rel_id_info(self) -> dict:
        # show detailed information of the relation id
        return self.__url_json if len(self.__url_json) < self._max_show else self.__url_json[:self._max_show]

    # convert OS path to standard linux path
    def __path2linux(self, path: Union[str, Path]) -> str:
        """Convert a path to a linux path, linux path can run in windows, linux and mac"""
        try:
            return path.replace("\\", "/")
        except Exception:
            return str(path).replace("\\", "/")

    def __find_local_rel_id(self) -> str:
        # sourcery skip: extract-duplicate-method

        # Step 0 load the global country, state, and city information from github
        try:
            print("  Info: Try to load global_rel_id.json from GitHub\n")
            github_url = "https://raw.githubusercontent.com/xyluo25/OSM2GMNS/master/dependencies/global_rel_id.json"
            global_rel_id_dict = json.loads(requests.get(github_url).text)
        except Exception:
            # if user can not access the internet, load the local file instead
            # please make sure the file exists in the local path
            # path: dependencies/global_rel_id.json
            print("  Info: Can not load global_rel_id.json from GitHub")
            print(f"  try to load local file: {self._path_global_rel_id}.\n")
            try:
                with open(self._path_global_rel_id, "r") as f:
                    global_rel_id_dict = json.load(f)
            except Exception:
                print("  Error: Can not load global_rel_id.json from local file\n \
                      please make sure the file exists in dependencies/global_rel_id.json \n \
                      Please search from https://www.openstreetmap.org/#map=5/40.298/-102.500  \n")
                return None

        # if we can not load dictionary, return None
        if not isinstance(global_rel_id_dict, dict):
            print("  Info: Could not load global_rel_id.json from GitHub.")
            print("  Please search from https://www.openstreetmap.org/#map=5/40.298/-102.500  \n")
            return None

        search_name = self.poi_name.split(",")[0].strip()
        if search_name == self.poi_name:
            search_name = self.poi_name.split(" ")[0].strip()

        # Step 1 Find the country start with the input characters
        start_with_country = [country_name for country_name in global_rel_id_dict["country"].keys(
        ) if country_name.lower().startswith(search_name.lower())][:self._max_show]

        # Step 2 Find the state start with the input characters
        start_with_state = [state_name for state_name in global_rel_id_dict["state"].keys(
        ) if state_name.lower().startswith(search_name.lower())][:self._max_show]

        # Step 3 Find the city start with the input characters
        start_with_city = [city_name for city_name in global_rel_id_dict["city"].keys(
        ) if city_name.lower().startswith(search_name.lower())][:self._max_show]

        # Step 4 Format the results
        formatted_str = ""
        if start_with_city:
            formatted_str += "City:\n"
            for city_name in start_with_city:
                formatted_str += f"""{city_name},
                {global_rel_id_dict["city"][city_name]["state"]},
                {global_rel_id_dict["city"][city_name]["country"]},
                rel_id: {global_rel_id_dict["city"][city_name]["osm_id"]} \n"""

        if start_with_state:
            formatted_str += "State:\n"
            for state_name in start_with_state:
                formatted_str += f"""{state_name},
                {global_rel_id_dict["state"][state_name]["country"]},
                rel_id: {global_rel_id_dict["state"][state_name]["osm_id"]} \n"""

        if start_with_country:
            formatted_str += "Country:\n"
            for country_name in start_with_country:
                formatted_str += f"""{country_name},
                rel_id: {global_rel_id_dict["country"][country_name]["osm_id"]} \n"""

        if formatted_str:

            formatted_str = f"""Info:\nWe can not search rel_id from web with place of interest: {self.poi_name} \n \
            Search locally with country, state and city startswith {search_name}:\n""" + formatted_str

            formatted_str += "You can replace your place of interest with local results above to get the rel_id\n"
            print(formatted_str)

        print("  Info: Could not load global_rel_id.json locally")
        print("  Please search from https://www.openstreetmap.org/#map=5/40.298/-102.500  \n")
        return {}


def getOSMRelationID(poi_name: str) -> Union[float, None]:
    """Get the relation id of a place of interest globally

    Args:
        poi_name (str): the name of the place of interest,
            e.g., "Arizona State University"
            e.g., "Tempe, Arizona, USA"
            e.g., "Arizona, USA"

    Returns:
        Union[float, None]: the relation id of the place of interest, if not found, return None

    Example:
        >>> import osm2gmns as og
        >>> rel = og.getOSMRelationID("Arizona State University")
        >>> rel
            Info: Found relation id 3444656 from web
            Info: location of the place of interest:
            {
                "place_id": 318528634,
                "licence": "Data \u00a9 OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
                "osm_type": "relation",
                "osm_id": 3444656,
                "lat": "33.4213174",
                "lon": "-111.93316305413154",
                "class": "amenity",
                "type": "university",
                "place_rank": 30,
                "importance": 0.5547365758311374,
                "addresstype": "amenity",
                "name": "Arizona State University",
                "display_name": "Arizona State University, 1151, South Forest Avenue, Tempe Junction, Tempe, Maricopa County, Arizona, 85281, United States",
                "boundingbox": [
                    "33.4102062",
                    "33.4329786",
                    "-111.9411651",
                    "-111.9092447"
                ]
            }
        3444656
    """
    rel = OSMRelationIDFinder(poi_name)
    return rel.rel_id