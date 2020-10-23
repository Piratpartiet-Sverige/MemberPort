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
from app.plugins.plugin import get_available_plugins, load_plugins
from app.web.handlers.admin.add_member import AddMemberHandler
from app.web.handlers.admin.members import MembersHandler
from app.web.handlers.admin.organizations import OrganizationsHandler
from app.web.handlers.admin.add_organization import AddOrganizationHandler
from app.web.handlers.admin.edit_organization import EditOrganizationHandler
from app.web.handlers.admin.roles import RolesHandler
from app.web.handlers.api.member import APIMemberHandler
from app.web.handlers.api.organization import APIOrganizationHandler
from app.web.handlers.authentication import SignInHandler, SignUpHandler
from app.web.handlers.kratos import KratosHandler
from app.web.handlers.main import MainHandler
from app.web.handlers.new_member import NewMemberHandler
from app.web.handlers.error import Error404Handler
from app.web.handlers.profile import ProfileHandler
from app.web.handlers.setup import SetupHandler
from app.web.handlers.verify import VerifyHandler
from app.database.setup import db_setup


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
    logger.info("Server was successfully started")

    ioloop.start()


def configure_application(options: WebAppOptions):
    ioloop = tornado.ioloop.IOLoop.current()

    available_plugins = get_available_plugins()
    plugins = load_plugins(available_plugins)

    handlers = [
        (r"/", MainHandler),
        (r"/kratos/(.*)", KratosHandler),
        (r"/admin/add-member", AddMemberHandler),
        (r"/admin/members", MembersHandler),
        (r"/admin/organizations", OrganizationsHandler),
        (r"/admin/add-organization", AddOrganizationHandler),
        (r"/admin/edit-organization", EditOrganizationHandler),
        (r"/admin/roles", RolesHandler),
        (r"/api/member", APIMemberHandler),
        (r"/api/organization", APIOrganizationHandler),
        (r"/auth/login", SignInHandler),
        (r"/auth/registration", SignUpHandler),
        (r"/login", tornado.web.RedirectHandler, dict(url=r"/auth/login")),
        (r"/new-member", NewMemberHandler),
        (r"/profile", ProfileHandler),
        (r"/verify", VerifyHandler),
    ]

    for plugin in plugins:
        handlers.append(plugin.get_handler())

    db = init_db(options)
    if db is not None:
        logger.debug("Database connection initialized...")
        db = asyncio.get_event_loop().run_until_complete(db)
        asyncio.get_event_loop().run_until_complete(db_setup(db))
        asyncio.get_event_loop().run_until_complete(first_setup(db, handlers))
    else:
        logger.error("Database connection failed")
        logger.warning("Running without a database")
        db = None

    webapp = tornado.web.Application(
        handlers,
        default_handler_class=Error404Handler,
        cookie_secret=options.cookie_secret,
        template_path=os.path.join(os.path.dirname(__file__), "..", "..", "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "..", "..", "static"),
        login_url="/auth/login",
        xsrf_cookies=options.xsrf,
        ioloop=ioloop,
        debug=options.debug
    )

    webapp.db = db

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

        return http_server
    else:
        webapp.listen(options.port)

        return webapp


def init_db(options: WebAppOptions):
    if options.db_hostname == "" and options.dbname == "":
        return None

    dsn = "postgres://{username}:{password}@{hostname}/{database}".format(
        username=options.db_username,
        password=options.db_password,
        hostname=options.db_hostname,
        database=options.dbname
    )

    return asyncpg.create_pool(dsn, min_size=2, max_size=20, max_inactive_connection_lifetime=1800)


async def first_setup(pool, handlers):
    sql = """SELECT s.initialized FROM settings s JOIN (
                SELECT initialized, MAX(created) AS created
                FROM settings se
                GROUP BY initialized
            ) lastEntry ON s.initialized = lastEntry.initialized AND s.created = lastEntry.created;"""

    async with pool.acquire() as con:
        row = await con.fetchrow(sql)

    if row["initialized"] is False:
        logger.info("Starting first time setup")
        handlers.clear()
        handlers.append((r"/kratos/(.*)", KratosHandler))
        handlers.append((r"/", SetupHandler))
