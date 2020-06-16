import tornado.web
import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration

from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class VerifyHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        request = self.get_argument("request", default="")

        if (request == ""):
            return self.redirect("http://127.0.0.1:8888/.ory/kratos/public/self-service/browser/flows/verification/email")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        csrf_token = ""
        error = ""
        action = ""

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_verification_request(request)

                if api_response.methods["profile"].config.errors != None:
                    error = api_response.methods["profile"].config.errors[0]
                
                action = api_response.methods["profile"].config.action
                csrf_token = api_response.methods["profile"].config.fields[0].value

                action = action.replace("http://pirate-kratos:4433", "/.ory/kratos/public")
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_verification_request: %s\n" % e)

        if error != "":
            logger.error("Error: " + error.message)

        await self.render("profile.html", title="Profil", user=self.current_user.user, action=action, error=error, csrf_token=csrf_token)

    @tornado.web.authenticated
    async def post(self):
        request = self.get_argument("request", default="")

        if request == "":
            self.respond("No request ID was found", 400)
            return

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_instance.complete_self_service_browser_verification_flow(request, "email")
            except ApiException as e:
                logger.error("Exception when calling PublicApi->complete_self_service_browser_verification_flow: %s\n" % e)
                self.respond("API exception against Kratos", 500)
                return

        self.respond("Verification of e-mail succesfull", 200)
