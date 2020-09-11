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
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/browser/flows/verification/email")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""
        action = ""
        success = False

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.CommonApi(api_client)
            try:
                api_response = api_instance.get_self_service_verification_request(request)
                if api_response.form.errors is not None:
                    error = api_response.form.errors[0]

                success = api_response.success
                action = api_response.form.action
                csrf_token = api_response.form.fields[0].value
            except ApiException as e:
                logger.error("Exception when calling CommonApi->get_self_service_verification_request: %s\n" % e)

        if error != "":
            logger.error("Error: " + error.message)
            error = error.message

        dao = UsersDao(self.db)
        permissions_check = await dao.check_user_admin(self.current_user.user.id)

        await self.render(
            "verify.html",
            admin=permissions_check,
            title="Verifiera",
            user=self.current_user.user,
            action=action,
            error=error,
            success=success,
            csrf_token=csrf_token
        )
