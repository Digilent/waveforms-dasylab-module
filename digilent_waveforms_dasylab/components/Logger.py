import logging

Logger = logging.getLogger()

if not Logger.hasHandlers():

    # Create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # create formatter and add to console_handler
    formatter = logging.Formatter("[%(filename)s:%(lineno)s::%(funcName)s()] %(message)s")
    console_handler.setFormatter(formatter)

    # Add console_handler to logger
    Logger.addHandler(console_handler)
