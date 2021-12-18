import osm2gmns.settings as og_settings
import logging


_log_created = False


def getLogger():
    global _log_created

    if not og_settings.log:
        return None

    logger = logging.getLogger(og_settings.log_name)

    if not _log_created:
        logger.setLevel(og_settings.log_level)
        handler = logging.FileHandler('osm2gmns.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', '%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        _log_created = True

    return logger



def config(verbose=og_settings.verbose,
           lonlat_coord_precision=og_settings.lonlat_coord_precision,
           local_coord_precision=og_settings.local_coord_precision,
           log_level=None):
    og_settings.verbose = verbose
    og_settings.lonlat_coord_precision = lonlat_coord_precision
    og_settings.local_coord_precision = local_coord_precision

    if log_level is not None:
        if not isinstance(log_level, str):
            print('WARNING: log_level must be a string and chosen from DEBUG, INFO, WARNING, ERROR, CRITICAL')
        else:
            log_level_upper = log_level.upper()
            if log_level_upper == 'DEBUG':
                og_settings.log = True
                og_settings.log_level = logging.DEBUG
            elif log_level_upper == 'INFO':
                og_settings.log = True
                og_settings.log_level = logging.INFO
            elif log_level_upper == 'WARNING':
                og_settings.log = True
                og_settings.log_level = logging.WARNING
            elif log_level_upper == 'ERROR':
                og_settings.log = True
                og_settings.log_level = logging.ERROR
            elif log_level_upper == 'CRITICAL':
                og_settings.log = True
                og_settings.log_level = logging.CRITICAL
            else:
                print('WARNING: log_level must be a string and chosen from DEBUG, INFO, WARNING, ERROR, CRITICAL')

