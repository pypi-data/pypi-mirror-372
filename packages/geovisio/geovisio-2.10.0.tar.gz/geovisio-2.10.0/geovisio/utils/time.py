import logging
from contextlib import contextmanager
from datetime import timedelta
from time import perf_counter


@contextmanager
def log_elapsed(ctx: str, log_lvl: int = logging.DEBUG, logger: logging.Logger = logging.getLogger("geovisio.utils")):
    """Context manager used to log the elapsed time of the context

    Args:
        ctx: Label to describe what is timed
        log_level: logging level, default to DEBUG
                logger: If set, use this logger to log, else the default logger is used
    """
    start = perf_counter()
    yield
    logger.log(log_lvl, f"{ctx} done in {timedelta(seconds=perf_counter()-start)}")
