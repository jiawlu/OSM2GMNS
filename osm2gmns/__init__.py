# @author       Jiawei Lu (jiaweil9@asu.edu)
# @time         2/17/23 3:02 PM
# @desc         [script description]


from osm2gmns.osm2gmns import initlib
from osm2gmns.osm2gmns import getNetFromFile, generateNodeActivityInfo, fillLinkAttributesWithDefaultValues, consolidateComplexIntersections, outputNetToCSV

__version__ = '1.0.0b2'
print(__version__)

initlib()


# zero or more dev releases (denoted with a “.devN” suffix)
# zero or more alpha releases (denoted with a “.aN” suffix)
# zero or more beta releases (denoted with a “.bN” suffix)
# zero or more release candidates (denoted with a “.rcN” suffix)
