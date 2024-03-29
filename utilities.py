import logging


def handle_error(e):
    logging.error("An unexpected error occurred: ", exc_info=True)