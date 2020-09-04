import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration
from datetime import datetime, timedelta
from typing import Union
from uuid import UUID

from asyncpg.pool import Pool
from tornado.web import RequestHandler

from app.config import Config
from app.logger import logger
from app.database.dao.users import UsersDao
from app.models import Session, User


class BaseHandler(RequestHandler):
    def data_received(self, chunk):
        # IDE seems to want to override this method, sure then
        pass

    @property
    def db(self) -> Pool:
        return self.application.db

    async def prepare(self):
        """
        Do not call manually. This runs on every request before get/post/etc.
        """
        self._current_user = await self.get_current_user()

    def is_authenticated(self) -> bool:
        """
        Check if current request is authenticated

        :returns: a boolean
        """
        return self.current_user != None

    async def get_current_user(self) -> Union[Session, None]:
        """
        Do not use this method to get the current user session, use the property `self.current_user` instead.
        """
        session_hash = self.session_hash

        if session_hash is None:
            return None

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        api_response = None
        session = None

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.whoami()
                session = Session()
                session.id = UUID(api_response.sid)
                session.hash = session_hash
                session.issued_at = api_response.issued_at
                session.expires_at = api_response.expires_at

                user = User()
                user.id = UUID(api_response.identity.id)
                user.name.first = api_response.identity.traits["name"]["first"]
                user.name.last = api_response.identity.traits["name"]["last"]
                user.email = api_response.identity.traits["email"]
                user.phone = "070 00 00 000" # api_response.identity.traits["phone"] ory does not yet support phone numbers
                user.city = api_response.identity.traits["city"]
                user.street = api_response.identity.traits["street"]
                user.postal_code = api_response.identity.traits["postal_code"]
                user.country = api_response.identity.traits["country"]
                user.verified = api_response.identity.verifiable_addresses[0].verified

                dao = UsersDao(self.db)
                user_info = await dao.get_user_member_number(user.id)
                user.created = user_info["created"]
                user.number = user_info["member_number"]

                session.user = user
                logger.debug("Session user: " + str(user.id))

            except ApiException as e:
                logger.error("Exception when calling PublicApi->whoami: %s\n" % e)

        return session

    @property
    def current_user(self) -> Union[Session, None]:
        """
        Get the current user session object that includes a object for the current user.
        :return: A Session object if authenticated, otherwise None
        """
        return super().current_user

    @property
    def session_hash(self) -> Union[str, None]:
        session_hash = self.get_cookie("ory_kratos_session")
        return session_hash

    def clear_session_cookie(self):
        self.clear_cookie("ory_kratos_session")

    @staticmethod
    def check_uuid(uuid: Union[UUID, str]) -> Union[UUID, None]:
        if uuid is None:
            logger.warning("UUID is None")
            return None
        if type(uuid) is str:
            try:
                uuid = UUID(uuid)
            except ValueError as exc:
                logger.debug(exc)
                logger.warning("Badly formatted UUID string: " + uuid)
                return None
        elif type(uuid) is not UUID:
            logger.warning("UUID is wrong type: " + type(uuid).__str__())
            return None

        return uuid

    def respond(self, message: str, status_code: int = 200, json_data: Union[None, dict] = None,
                show_error_page: bool = False):
        if show_error_page is True and status_code >= 400:
            return self.send_error(status_code, error_message=message)

        self.set_status(status_code, message)

        if status_code >= 400:
            self.write({'success': False, 'reason': message, 'data': json_data})
        else:
            self.write({'success': True, 'reason': message, 'data': json_data})

    def write_error(self, status_code: int, error_message: str = "", **kwargs: any) -> None:
        message = ""

        if error_message != "":
            message = error_message
        elif kwargs["exc_info"] is not None:
            message = kwargs["exc_info"].__str__()

        self.set_status(status_code, message)

        template = "error/" + status_code.__str__() + ".html"

        self.render(template)
