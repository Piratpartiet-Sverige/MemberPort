from datetime import datetime, timedelta
from tornado.testing import AsyncHTTPTestCase
from uuid import uuid4

from app.models import Session, User
from app.web.web_server import WebAppOptions, configure_application


class WebTestCase(AsyncHTTPTestCase):
    def get_app(self):
        options = WebAppOptions()
        options.debug = True
        options.xsrf = False
        options.test = True
        options.cookie_secret = "ccd70ecea6d9f0833b07688e69bf2368f86f9127de17de102e17788a805afb7f"

        return configure_application(options)


def get_mock_session():
    session = Session()
    session.id = uuid4()
    session.hash = "ccd70ecea6d9f0833b07688e69bf2368f86f9127de17de102e17788a805afb7f"
    session.issued_at = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(days=1)

    user = User()
    user.id = uuid4()
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
