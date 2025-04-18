# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2/17/23 3:02 PM
# @desc         [script description]


from osm2gmns.osm2gmns import initlib
from osm2gmns.osm2gmns import getNetFromFile, generateNodeActivityInfo, fillLinkAttributesWithDefaultValues, consolidateComplexIntersections, outputNetToCSV
from osm2gmns.downloader import downloadOSMData

__version__ = '1.0.0rc1'

initlib()


# zero or more dev releases (denoted with a “.devN” suffix)
# zero or more alpha releases (denoted with a “.aN” suffix)
# zero or more beta releases (denoted with a “.bN” suffix)
# zero or more release candidates (denoted with a “.rcN” suffix)
