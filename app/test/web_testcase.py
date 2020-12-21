from tornado.testing import AsyncHTTPTestCase

from app.web.web_server import WebAppOptions, configure_application


class WebTestCase(AsyncHTTPTestCase):
    def get_app(self):
        options = WebAppOptions()
        options.debug = True
        options.xsrf = False
        options.cookie_secret = "ccd70ecea6d9f0833b07688e69bf2368f86f9127de17de102e17788a805afb7f"
        options.db_username = "super"
        options.db_password = "super"
        options.db_hostname = "postgres-db"
        options.dbname = "memberportdb"

        return configure_application(options)
