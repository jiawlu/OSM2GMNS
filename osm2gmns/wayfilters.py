# Note: we adopt the filter logic from osmnx (https://github.com/gboeing/osmnx)
# exclude links with tag attributes in the filters
filters = {}


filters['auto'] = {'area':['yes'],
                   'highway':['cycleway','footway','path','pedestrian','steps','track','corridor','elevator','escalator',
                              'proposed','construction','bridleway','abandoned','platform','raceway','service'],
                   'motor_vehicle':['no'],
                   'motorcar':['no'],
                   'access':['private'],
                   'service':['parking','parking_aisle','driveway','private','emergency_access']
                   }

filters['bike'] = {'area':['yes'],
                   'highway':['footway','steps','corridor','elevator','escalator','motor','proposed','construction','abandoned','platform','raceway'],
                   'bicycle':['no'],
                   'service':['private'],
                   'access':['private']
                   }

filters['walk'] = {'area':['yes'],
                   'highway':['cycleway','motor','proposed','construction','abandoned','platform','raceway'],
                   'foot':['no'],
                   'service':['private'],
                   'access':['private']
                   }


def getAllowableAgentType(way):
    allowable_agent_type_list = []
    for agent_type, m_filter in filters.items():
        allowed = True
        for tag, exclude_list in m_filter.items():
            if eval(f'way.{tag} in exclude_list'):
                allowed = False
                break
        if allowed: allowable_agent_type_list.append(agent_type)

    if 'track' in way.highway: allowable_agent_type_list.append('track')

    return allowable_agent_type_list
