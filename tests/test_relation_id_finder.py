# -*- coding:utf-8 -*-
##############################################################
# Created Date: Sunday, February 4th 2024
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################


from osm2gmns.func_lib.extract_relation_id import OSMRelationIDFinder


def test_rel_id_web_search_exists():

    rel_identifier = OSMRelationIDFinder("Arizona State University")
    rel_id = rel_identifier.rel_id
    print(type(rel_id))
    assert isinstance(rel_id, int)


def test_rel_id_web_search_not_exists():

    rel_identifier = OSMRelationIDFinder("TTTTTTEEEEEESSSSSTTTTT")
    rel_id = rel_identifier.rel_id
    assert rel_id is None
