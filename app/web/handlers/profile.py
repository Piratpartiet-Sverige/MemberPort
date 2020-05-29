import tornado.web
import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        request = self.get_argument("request", default="")

        if (request == ""):
            return self.redirect("http://127.0.0.1:8888/.ory/kratos/public/self-service/browser/flows/settings")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        csrf_token = ""
        error = ""

        logger.debug("ory_kratos_session=" + self.session_hash + ";")

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_browser_settings_request(request)
                logger.debug(api_response)
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_browser_settings_request: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)

        await self.render("profile.html", title="Profil", user=self.current_user.user)
