#!/bin/env python3
"""
MemberPort - Member management system
Copyright (C) 2020 Piratpartiet

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

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
