import logging

# Server logger
logger = logging.getLogger("MemberPort")
access = logging.getLogger("tornado.access")
application = logging.getLogger("tornado.application")
general = logging.getLogger("tornado.general")


def setup_logger(debug: bool):
    formatter = logging.Formatter(
        "[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s"
    )

    file_handler = logging.handlers.RotatingFileHandler("server.log", maxBytes=1000000, backupCount=10)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    file_handler = logging.handlers.RotatingFileHandler("tornado.log", maxBytes=1000000, backupCount=10)
    file_handler.setFormatter(formatter)
    access.addHandler(file_handler)
    application.addHandler(file_handler)
    general.addHandler(file_handler)

    if debug is True:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
