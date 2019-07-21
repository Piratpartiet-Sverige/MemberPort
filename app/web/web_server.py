import asyncio
import asyncpg
import os.path
import ssl
import tornado.ioloop
import tornado.web

from configparser import ConfigParser
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from app.config import Config
from app.logger import logger
from app.web.handlers.authentication import SignInHandler, SignOutHandler, SignUpHandler
from app.web.handlers.main import MainHandler


class WebAppOptions:
    debug: bool = False
    https: bool = False
    port: int = 8888
    xsrf: bool = True
    cookie_secret: str = ""
    cert_file: os.PathLike = ""
    private_file: os.PathLike = ""
    db_username: str = ""
    db_password: str = ""
    db_hostname: str = ""
    dbname: str = ""


def start():
    logger.info("Starting server...")
    ioloop = tornado.ioloop.IOLoop.current()

    config = Config.get_config()  # type: ConfigParser

    options = WebAppOptions()
    options.debug = config.getboolean("WebServer", "debug", fallback=False)
    options.https = config.getboolean("WebServer", "https", fallback=False)
    options.port = config.getint("WebServer", "port")
    options.cookie_secret = config.get("WebServer", "cookie_secret")
    options.cert_file = config.get("WebServer", "certs")
    options.private_file = config.get("WebServer", "private")
    options.db_username = config.get("PostgreSQL", "username")
    options.db_password = config.get("PostgreSQL", "password")
    options.db_hostname = config.get("PostgreSQL", "hostname")
    options.dbname = config.get("PostgreSQL", "dbname")

    configure_application(options)

    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    ioloop.start()


def configure_application(options: WebAppOptions):
    ioloop = tornado.ioloop.IOLoop.current()

    webapp = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/sign-in", SignInHandler),
            (r"/sign-out", SignOutHandler),
            (r"/sign-up", SignUpHandler),
            (r"/login", tornado.web.RedirectHandler, dict(url=r"/sign-in")),
        ],
        cookie_secret=options.cookie_secret,
        template_path=os.path.join(os.path.dirname(__file__), "..", "..", "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "..", "..", "static"),
        login_url="/sign-in",
        xsrf_cookies=options.xsrf,
        ioloop=ioloop,
        debug=options.debug
    )

    if options.https is True:
        cert_file = os.path.abspath(options.cert_file)
        private_file = os.path.abspath(options.private_file)

        if os.path.isfile(cert_file) is False:
            logger.error("Path specified in config for certification points to a non-file: " + cert_file)
            raise FileNotFoundError("Given path is not a file: " + cert_file)
        if os.path.isfile(private_file) is False:
            logger.error("Path specified in config for private key points to a non-file: " + private_file)
            raise FileNotFoundError("Given path is not a file: " + private_file)

        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(cert_file, private_file)

        http_server = tornado.httpserver.HTTPServer(webapp, ssl_options=ssl_ctx)
        http_server.listen(options.port)

        db = init_db(options)
        if db is not None:
            webapp.db = asyncio.get_event_loop().run_until_complete(db)
        else:
            webapp.db = None

        return http_server
    else:
        webapp.listen(options.port)
        db = init_db(options)
        if db is not None:
            webapp.db = asyncio.get_event_loop().run_until_complete(db)
        else:
            webapp.db = None

        return webapp


def init_db(options: WebAppOptions):
    if options.db_hostname is "" and options.dbname is "":
        return None

    dsn = "postgres://{username}:{password}@{hostname}/{database}".format(
        username=options.db_username,
        password=options.db_password,
        hostname=options.db_hostname,
        database=options.dbname
    )

    return asyncpg.create_pool(dsn, min_size=2, max_size=20, max_inactive_connection_lifetime=1800)
