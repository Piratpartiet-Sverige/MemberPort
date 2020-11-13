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
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/verification/browser")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""
        action = ""
        state = ""

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_verification_flow(flow)
                csrf_token = api_response.methods['link'].config.fields[0].value

                if api_response.methods['link'].config.messages is not None:
                    error = api_response.methods['link'].config.messages[0].text
                else:
                    for field in api_response.methods['link'].config.fields:
                        if field.messages is not None:
                            error = field.messages[0].text
                            break

                state = api_response.state
                action = api_response.methods['link'].config.action
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_verification_flow: %s\n" % e)

        if error != "":
            logger.error("Error: " + error)

        dao = UsersDao(self.db)
        permissions_check = await dao.check_user_admin(self.current_user.user.id)

        await self.render(
            "verify.html",
            admin=permissions_check,
            title="Verifiera",
            user=self.current_user.user,
            action=action,
            error=error,
            state=state,
            csrf_token=csrf_token
        )
