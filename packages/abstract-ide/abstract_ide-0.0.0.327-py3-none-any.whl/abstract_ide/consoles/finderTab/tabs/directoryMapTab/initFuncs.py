

from .functions import (append_log, display_map, start_map)

def initFuncs(self):
    try:
        for f in (append_log, display_map, start_map):
            setattr(self, f.__name__, f)
    except Exception as e:
        logger.info(f"{e}")
    return self
