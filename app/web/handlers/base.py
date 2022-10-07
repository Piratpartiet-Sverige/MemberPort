import json

from asyncio.coroutines import coroutine
from datetime import datetime
from typing import Union
from uuid import UUID

from asyncpg.pool import Pool
from tornado.web import RequestHandler
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from app.logger import logger
from app.database.dao.users import UsersDao
from app.database.dao.roles import RolesDao
from app.models import Session, User


def has_permissions(*permissions: str) -> callable:
    """
    Decorator that checks if the current user has the permissions listed
    :returns 403, PERMISSION DENIED, if the current user doesn't have all of the permissions
    """
    def has_permissions_wrapper(func: coroutine):
        async def permission_check(self, *args, **kwargs):
            roles_dao = RolesDao(self.db)
            for permission in permissions:
                if not await roles_dao.check_user_permission(self.current_user.user.id, permission):
                    return self.respond("PERMISSION DENIED", 403, None)

            return await func(self, *args, **kwargs)
        return permission_check
    return has_permissions_wrapper


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
        return self.current_user is not None

    async def get_current_user(self) -> Union[Session, None]:
        """
        Do not use this method to get the current user session, use the property `self.current_user` instead.
        """
        session_hash = self.session_hash

        if session_hash is None:
            return None

        logger.debug(session_hash)
        kratos_host_user = "http://pirate-kratos:4433/sessions/whoami"
        kratos_host_logout = "http://pirate-kratos:4433/self-service/logout/browser"
        http_client = AsyncHTTPClient()
        http_request_user = HTTPRequest(url=kratos_host_user, headers={"Cookie": session_hash})
        http_request_logout = HTTPRequest(url=kratos_host_logout, headers={"Cookie": session_hash})

        try:
            response_user = await http_client.fetch(http_request_user)
            response_logout = await http_client.fetch(http_request_logout)

            api_response = json.loads(response_user.body)
            api_response_logout = json.loads(response_logout.body)
        except Exception as e:
            logger.critical("Error when retrieving session: %s" % e)
            return None

        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        session = Session()
        session.id = UUID(api_response["id"])
        session.hash = session_hash
        session.issued_at = datetime.strptime(api_response["issued_at"], time_format)
        session.expires_at = datetime.strptime(api_response["expires_at"], time_format)

        identity = api_response.get("identity", {})
        identity_traits = identity.get("traits", {})
        metadata = identity.get("metadata_public", {})
        if metadata is None:
            metadata = {}

        user = User()
        user.id = UUID(identity["id"])
        user.name.first = identity_traits["name"]["first"]
        user.name.last = identity_traits["name"]["last"]
        user.email = identity_traits["email"]
        user.phone = identity_traits.get("phone", "")
        user.postal_address.street = identity_traits["postal_address"]["street"]
        user.postal_address.postal_code = identity_traits["postal_address"]["postal_code"]
        user.postal_address.city = identity_traits["postal_address"]["city"]
        user.municipality = identity_traits["municipality"]
        user.country = identity_traits["country"]
        user.verified = identity["verifiable_addresses"][0]["verified"]
        user.created = datetime.strptime(identity["created_at"], time_format)
        user.number = metadata.get("member_number", -1)

        session.user = user
        session.logout_url = api_response_logout["logout_url"]
        logger.debug("Session user: " + str(user.id))

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

        if session_hash is not None:
            session_hash = "ory_kratos_session=" + session_hash

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
            except ValueError:
                logger.warning("Badly formatted UUID string: " + uuid)
                return None
        elif type(uuid) is not UUID:
            logger.warning("UUID is wrong type: " + type(uuid).__str__())
            return None

        return uuid

    async def permission_check(self):
        dao = UsersDao(self.db)
        return await dao.check_user_admin(self.current_user.user.id)

    def respond(self, message: str, status_code: int = 200, json_data: Union[None, dict] = None,
                show_error_page: bool = False):
        if show_error_page is True and status_code >= 400:
            return self.send_error(status_code, error_message=message)

        self.set_status(status_code, message)

        if status_code >= 400:
            self.write({'success': False, 'reason': message, 'data': json_data})
        elif status_code != 204:
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
