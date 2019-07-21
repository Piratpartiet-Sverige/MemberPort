from datetime import datetime, timedelta
from typing import Union
from uuid import UUID

from asyncpg.pool import Pool
from tornado.web import RequestHandler

from app.config import Config
from app.logger import logger
from app.database.dao.users import UsersDao
from app.models import Session


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
        return self._current_user is not None

    async def get_current_user(self) -> Union[Session, None]:
        """
        Do not use this method to get the current user session, use the property `self.current_user` instead.
        """
        session_hash = self.session_hash
        ip = self.request.remote_ip

        if session_hash is None:
            return None

        dao = UsersDao(self.db)
        session = await dao.get_session_by_hash(session_hash)

        if session is None:
            # Session hash is not in the database
            self.clear_session_cookie()
            return None

        max_idle_days = Config.get_config().getint("Session", "max_idle_days")

        # Check if session is older than max configured idle days, if it is; sign out
        if session.last_used < datetime.now() - timedelta(days=max_idle_days):
            await dao.remove_session(session_hash)
            self.clear_session_cookie()
            return None

        new_session = await dao.update_session(session_hash, ip)
        return new_session

    @property
    def current_user(self) -> Union[Session, None]:
        """
        Get the current user session object that includes a object for the current user.
        :return: A Session object if authenticated, otherwise None
        """
        return super().current_user

    @property
    def session_hash(self) -> Union[str, None]:
        session_hash = self.get_secure_cookie("session")
        return session_hash.decode("utf8") if session_hash is not None else None

    def set_session_cookie(self, value=None):
        if value is not None and value != "":
            self.set_secure_cookie("session", value)

    def clear_session_cookie(self):
        self.clear_cookie("session")

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
