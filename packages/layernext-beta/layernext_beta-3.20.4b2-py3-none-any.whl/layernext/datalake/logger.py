import logging
import logging.handlers
import os
import sys


def get_debug_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        # Create a package-level logger

        logger.setLevel(
            logging.DEBUG
        )  # Ensure the logger level is set to capture the intended messages

        log_directory = "logs/"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)  # Create the directory if it does not exist

        file_handler = logging.FileHandler(log_directory + "package.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        )
        logger.addHandler(file_handler)

        # NOTE: comment out the following line to disable the stdout logger since stdout is captured in the chat app
        # stream_handler = logging.StreamHandler(sys.stdout)
        # stream_handler.setLevel(logging.DEBUG)
        # stream_handler.setFormatter(
        #     logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # )
        # logger.addHandler(stream_handler)

        logger.propagate = False  # Ensure propagation is enabled

        return logger
