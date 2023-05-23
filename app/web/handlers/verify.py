from app.logger import logger
from app.web.handlers.base import BaseHandler

import ory_kratos_client
from ory_kratos_client.api import frontend_api
from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration


class VerifyHandler(BaseHandler):
    async def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("/kratos/self-service/verification/browser")

        configuration = Configuration(
            host="http://pirate-kratos:4433"
        )

        cookie = self.request.headers['Cookie']
        errors = []
        nodes = []
        action = ""
        method = ""
        state = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = frontend_api.FrontendApi(api_client)
            try:
                api_response = api_instance.get_verification_flow(flow, cookie=cookie)
                state = api_response.state.value

                errors = api_response.ui.messages.value if hasattr(api_response.ui, 'messages') else []
                nodes = api_response.ui.nodes.value

                action = api_response.ui.action
                method = api_response.ui.method
            except ApiException as e:
                logger.error("Exception when calling FrontendApi->get_verification_flow: %s\n" % e)

                if e.status == 410:
                    return self.redirect("/kratos/self-service/verification/browser")

        email = ""
        if self.current_user is not None:
            if self.current_user.user is not None:
                email = self.current_user.user.email
            elif self.current_user.bot is not None:
                email = self.current_user.bot.email

        await self.render(
            "verify.html",
            title="Verifiera",
            email=email,
            action=action,
            method=method,
            errors=errors,
            nodes=nodes,
            state=state
        )
