# todo: walk, bike

negligible_highway_type_set = {'path','construction','proposed','raceway','bridleway','rest_area','su',
                               'road','abandoned','planned','trailhead','stairs','dismantled','disused','razed','access',
                               'corridor','stop'}
negligible_railway_type_set = {'construction','abandoned','disused','proposed','planned','dismantled','razed','ventilation_shaft'}
negligible_aeroway_type_set = set()

highway_poi_set = {'bus_stop','platform'}
railway_poi_set = {'depot','station','workshop','halt','interlocking','junction','spur_junction','terminal','platform'}
aeroway_poi_set = set()

network_types_all = {'auto','bike','walk','railway','aeroway'}

_filter_in = {'auto': {'motor_vehicle':{'yes'},
                      'motorcar':{'yes'}},
              'bike': {'bicycle':{'yes'}},
              'walk': {'foot':{'yes'}}}

_filters_ex = {'auto': {'highway':{'cycleway','footway','pedestrian','steps','track','corridor','elevator','escalator','service','living_street'},
                       'motor_vehicle':{'no'},
                       'motorcar':{'no'},
                       'access':{'private'},
                       'service':{'parking','parking_aisle','driveway','private','emergency_access'}},
               'bike': {'highway':{'footway','steps','corridor','elevator','escalator','motor','motorway','motorway_link'},
                       'bicycle':{'no'},
                       'service':{'private'},
                       'access':{'private'}},
               'walk': {'highway':{'cycleway','motor','motorway','motorway_link'},
                       'foot':{'no'},
                       'service':{'private'},
                       'access':{'private'}}}

_agent_types_all = ['auto', 'bike', 'walk']



def _checkIn(way, agent_type):
    m_filter_in = _filter_in[agent_type]
    for tag, include_list in m_filter_in.items():
        if getattr(way, tag) in include_list:
            return True
    return None


def _checkEx(way, agent_type):
    m_filter_ex = _filters_ex[agent_type]
    for tag, exclude_list in m_filter_ex.items():
        if getattr(way, tag) in exclude_list:
            return False
    return True


def getAllowableAgentType(way):
    allowable_agent_type_list = []

    for agent_type in _agent_types_all:
        allowed = _checkIn(way, agent_type)
        if allowed:
            allowable_agent_type_list.append(agent_type)
            continue

        allowed = _checkEx(way, agent_type)
        if allowed:
            allowable_agent_type_list.append(agent_type)

    return allowable_agent_type_list
