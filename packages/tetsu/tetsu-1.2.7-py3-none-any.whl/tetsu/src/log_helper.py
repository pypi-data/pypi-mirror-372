# Logging class
import logging
import logging.config
import os
import time

import yaml


def logger(
        name=None,
        handler="console",
        filepath=None,
        level=logging.DEBUG,
):
    """
    This is a simple logger to save logs locally or print to console

    :param name: name of logging file. You do not need to include the .log extension here
    :param handler: logging handler selection. Values should be 'file','console' or 'both'
    :param filepath: file path for the logging file, should contain ending '/'
    :param level: logging level. Default is logging.INFO

    :returns: Python logger
    """
    # Set Handler

    if handler not in ["file", "console", "both"]:
        print("Please select an appropriate handler list: file, console or both")
        return

    try:
        # only create directory when given a filepath
        if filepath is not None:
            os.makedirs(filepath, exist_ok=True)
            print(f"Successfully created the directory {filepath}. Logs will be stored here.")
    except OSError:
        print(f"Creation of the directory {filepath} failed")

    current_logger = logging.getLogger(name)
    current_logger.handlers.clear()
    current_logger.setLevel(level)
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    if handler in ["file", "both"]:
        if filepath is None:
            print("Need to provide a filepath if using file logger.")
            return

        file = f"{filepath}/{name}" + str(time.strftime("%Y%m%d-%H%M%S")) + ".log"
        fh = logging.FileHandler(file)
        fh.setFormatter(formatter)
        current_logger.addHandler(fh)

    if handler in ["console", "both"]:
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        current_logger.addHandler(ch)

    current_logger.propagate = False
    return current_logger


def log_setup(
        name='logging',
        filepath='config'
):
    """
    Initialize a project-level logging object and read in the configuration parameters from an external file.
    This function is meant to be run once at the beginning of main.py

    :param name: name of logging file
    :param filepath: file path for the logging file
    """
    with open(f"{filepath}/{name}.yaml") as log_file:
        logging_conf = yaml.safe_load(log_file)
    logging.config.dictConfig(logging_conf)
