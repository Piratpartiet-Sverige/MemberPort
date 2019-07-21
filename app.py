#!/bin/env python3
from tornado.options import options
from app.config import Config
from app.web import web_server
from app.logger import setup_logger


def main():
    config = Config.get_config()
    debug = config.getboolean("WebServer", "debug", fallback=False)
    setup_logger(debug)

    web_server.start()


if __name__ == "__main__":
    options.parse_command_line()
    main()
