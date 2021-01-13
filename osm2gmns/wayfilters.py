# Note: we adopt the filter logic from osmnx (https://github.com/gboeing/osmnx)
# exclude links with tag attributes in the filters

# todo: walk, bike

negligible_highway_type_set = {'path','construction','proposed','raceway','bridleway','rest_area','su','living_street',
                               'road','abandoned','planned','trailhead','stairs','dismantled','disused','razed','access',
                               'corridor','stop'}
negligible_railway_type_set = {'construction','abandoned','disused','proposed','planned','dismantled','razed','ventilation_shaft'}
negligible_aeroway_type_set = set()

highway_poi_set = {'bus_stop','platform'}
railway_poi_set = {'depot','station','workshop','halt','interlocking','junction','spur_junction','terminal','platform'}
aeroway_poi_set = set()

network_type_all = {'auto','bike','walk','railway','aeroway'}


_filter_in = {}
_filters_ex = {}

_filter_in['auto'] = {'motor_vehicle':{'yes'},
                      'motorcar':{'yes'}}

_filter_in['bike'] = {'bicycle':{'yes'}}

_filter_in['walk'] = {'foot':{'yes'}}

_filters_ex['auto'] = {'highway':{'cycleway','footway','pedestrian','steps','track','corridor','elevator','escalator','service'},
                       'motor_vehicle':{'no'},
                       'motorcar':{'no'},
                       'access':{'private'},
                       'service':{'parking','parking_aisle','driveway','private','emergency_access'}}

_filters_ex['bike'] = {'highway':{'footway','steps','corridor','elevator','escalator','motor'},
                       'bicycle':{'no'},
                       'service':{'private'},
                       'access':{'private'}}

_filters_ex['walk'] = {'highway':{'cycleway','motor'},
                       'foot':{'no'},
                       'service':{'private'},
                       'access':{'private'}}

_agent_type_all = ['auto', 'bike', 'walk']



def _checkIn(way, agent_type):
    m_filter_in = _filter_in[agent_type]
    for tag, include_list in m_filter_in.items():
        if eval(f'way.{tag} in include_list'):
            return True
    return None


def _checkEx(way, agent_type):
    m_filter_ex = _filters_ex[agent_type]
    for tag, exclude_list in m_filter_ex.items():
        if eval(f'way.{tag} in exclude_list'):
            return False
    return True


def getAllowableAgentType(way):
    allowable_agent_type_list = []

    for agent_type in _agent_type_all:
        allowed = _checkIn(way, agent_type)
        if allowed:
            allowable_agent_type_list.append(agent_type)
            continue

        allowed = _checkEx(way, agent_type)
        if allowed:
            allowable_agent_type_list.append(agent_type)

    return allowable_agent_type_list
