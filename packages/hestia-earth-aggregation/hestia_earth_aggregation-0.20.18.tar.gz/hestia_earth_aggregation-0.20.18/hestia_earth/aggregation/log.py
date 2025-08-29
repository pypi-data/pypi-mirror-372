import os
import sys
import platform
import resource
import logging

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# disable root logger
root_logger = logging.getLogger()
root_logger.disabled = True

# create custom logger
logger = logging.getLogger('hestia_earth.aggregation')
logger.removeHandler(sys.stdout)
logger.setLevel(logging.getLevelName(LOG_LEVEL))


def log_to_file(filepath: str):
    """
    By default, all logs are saved into a file with path stored in the env variable `LOG_FILENAME`.
    If you do not set the environment variable `LOG_FILENAME`, you can use this function with the file path.

    Parameters
    ----------
    filepath : str
        Path of the file.
    """
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", '
        '"filename": "%(filename)s", "message": "%(message)s"}',
        '%Y-%m-%dT%H:%M:%S%z')
    handler = logging.FileHandler(filepath, encoding='utf-8')
    handler.setFormatter(formatter)
    handler.setLevel(logging.getLevelName(LOG_LEVEL))
    logger.addHandler(handler)


LOG_FILENAME = os.getenv('LOG_FILENAME')
if LOG_FILENAME is not None:
    log_to_file(LOG_FILENAME)


def _join_args(**kwargs): return ', '.join([f"{key}={value}" for key, value in kwargs.items()])


def log_memory_usage(**kwargs):
    factor = 1024 * (
        1024 if platform.system() in ['Darwin', 'Windows'] else 1
    )
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / factor
    extra = (', ' + _join_args(**kwargs)) if len(kwargs.keys()) > 0 else ''
    logger.info('memory_used=%s, unit=MB' + extra, value)


def debugRequirements(**kwargs):
    logger.debug(_join_args(**kwargs))


def _sum_values(values: list):
    """
    Sum up the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return sum(filtered_values) if len(filtered_values) > 0 else None


def debugWeights(weights: dict):
    total_weight = _sum_values(v.get('weight') for v in weights.values()) or 100
    for id, weight in weights.items():
        value = weight.get('weight')
        logger.debug('id=%s, weight=%s, ratio=%s/%s', id, value * 100 / total_weight, value, total_weight)
