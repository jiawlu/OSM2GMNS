# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2/17/23 3:02 PM
# @desc         [script description]

import gurobipy as grb

m = grb.Model()

a = 1



import osm2gmns as og
import os
import time

# t1 = time.time()

# working_directory = '/Users/jiawei/Dropbox (ASU)/Work/CAVLite/OSM2GMNS/maps/AZ'
# net = og.getNetFromFile(os.path.join(working_directory, 'arizona-latest.osm.pbf'))

working_directory = '/Users/jiawei/Dropbox (ASU)/Work/CAVLite/OSM2GMNS/maps/asu'
net = og.getNetFromFile(os.path.join(working_directory, 'asu.osm'))

og.outputNetToCSV(net, working_directory)


# t2 = time.time()
# print(f'total time: {t2-t1}')