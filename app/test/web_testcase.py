from asyncio.coroutines import coroutine
from asyncpg import Connection
from asyncpg.pool import Pool
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock
from tornado.testing import AsyncHTTPTestCase
from uuid import UUID, uuid4

from app.models import Session, User
from app.web.web_server import WebAppOptions, configure_application


class MagicMockContext(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        if exc is not None:
            raise exc

        return self


class WebTestCase(AsyncHTTPTestCase):
    def __init__(self, methodName: str) -> None:
        self.connection = MagicMockContext(Connection)
        super().__init__(methodName=methodName)

    def get_app(self):
        options = WebAppOptions()
        options.debug = True
        options.xsrf = False
        options.test = True
        options.cookie_secret = "ccd70ecea6d9f0833b07688e69bf2368f86f9127de17de102e17788a805afb7f"  # noqa: S105 # nosec

        app = configure_application(options)
        app.db = Mock(Pool)
        app.db.acquire.return_value = self.connection

        return app

    def assert_datetime(self, field_name, datetime_str):
        try:
            time_format = "%Y-%m-%d %H:%M:%S"
            self.assertTrue(isinstance(datetime.strptime(datetime_str, time_format), datetime))
        except ValueError:
            self.fail("'" + field_name + "' field was wrong format")

    def assert_uuid(self, field_name, uuid_str):
        try:
            UUID(uuid_str)
        except Exception:
            self.fail("'" + field_name + "' field was wrong UUID format")


def get_mock_session():
    session = Session()
    session.id = uuid4()
    session.hash = "ccd70ecea6d9f0833b07688e69bf2368f86f9127de17de102e17788a805afb7f"
    session.issued_at = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(days=1)

    user = User()
    user.id = UUID('94983a62-8b07-4446-9753-8ba3a80d6000')
    user.name.first = "Barbro"
    user.name.last = "Pirat"
    user.email = "barbro.pirat@piratpartiet.se"
    user.phone = "070 00 00 000"
    user.postal_address.street = "Påhittad 8A"
    user.postal_address.postal_code = "22464"
    user.postal_address.city = "Lund"
    user.municipality = "Lund"
    user.country = "Sverige"
    user.verified = True
    user.created = session.issued_at
    user.number = 112

    session.user = user

    return session


def set_permissions(*permissions: str) -> callable:
    def set_permissions_wrapper(func: coroutine):
        def return_permissions(self, *args, **kwargs):
            side_effects = [[{"role": uuid4()}]]
            permission_list = []

            for permission in permissions:
                permission_list.append({"permission": permission})

            side_effects.append(permission_list)

            self.connection.fetch.side_effect = side_effects
            return func(self, *args, **kwargs)
        return return_permissions
    return set_permissions_wrapper
