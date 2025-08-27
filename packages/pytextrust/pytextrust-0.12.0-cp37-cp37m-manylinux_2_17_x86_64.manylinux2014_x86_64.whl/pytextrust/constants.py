import logging
import os
from pathlib import Path


LOG_FORMAT = '%(levelname)s %(asctime)s: %(message)s'


def get_logger():
    logging_level = os.getenv('PYTEXTRUST_LOG_LEVEL', 'INFO')
    if hasattr(logging, logging_level):
        log_level_obj = getattr(logging, logging_level)
    else:
        log_level_obj = logging.INFO

    logging.basicConfig(format=LOG_FORMAT, level=log_level_obj)
    logger = logging.getLogger(name="pytextrust")

    return logger


def get_module_path(imported_module):
    val = str(Path(os.path.abspath(imported_module.__file__)).parent)
    return val


def get_test_data_dir(imported_module):
    module_path = get_module_path(imported_module)
    test_data_dir = os.path.join(module_path, "tests", "data")

    return test_data_dir
