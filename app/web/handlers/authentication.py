import ory_kratos_client

from ory_kratos_client.api import v0alpha2_api
from ory_kratos_client.configuration import Configuration
from ory_kratos_client.rest import ApiException
from app.database.dao.geography import GeographyDao
from app.models import ui_placeholders, ui_positions
from app.web.handlers.base import BaseHandler
from app.logger import logger
from tornado import httpclient  # noqa needed for kratos response


class SignInHandler(BaseHandler):
    def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("/kratos/self-service/login/browser")

        configuration = Configuration(
            host="http://pirate-kratos:4433"
        )

        cookie = self.request.headers['Cookie']
        action = ""
        method = ""
        nodes = []
        errors = []

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = v0alpha2_api.V0alpha2Api(api_client)
            try:
                api_response = api_instance.get_self_service_login_flow(flow, cookie=cookie)
                nodes = api_response.ui.nodes.value
                errors = api_response.ui.messages.value if hasattr(api_response.ui, 'messages') else []
                action = api_response.ui.action
                method = api_response.ui.method
            except ApiException as e:
                logger.error("Exception when calling v0alpha2_api->get_self_service_login_flow: %s\n" % e)
                logger.error(e.status)
                if e.status == 410:
                    return self.redirect("/kratos/self-service/login/browser")

        self.render(
            "sign-in.html",
            action=action,
            method=method,
            nodes=nodes,
            errors=errors
        )


class SignUpHandler(BaseHandler):
    async def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("/kratos/self-service/registration/browser")

        configuration = Configuration(
            host="http://pirate-kratos:4433"
        )

        cookie = self.request.headers['Cookie']
        action = ""
        method = ""
        nodes = []
        errors = []

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = v0alpha2_api.V0alpha2Api(api_client)
            try:
                api_response = api_instance.get_self_service_registration_flow(flow, cookie=cookie)
                nodes = api_response.ui.nodes.value
                errors = api_response.ui.messages.value if hasattr(api_response.ui, 'messages') else []
                action = api_response.ui.action
                method = api_response.ui.method
                logger.debug(api_response)
            except ApiException as e:
                logger.error("Exception when calling V0alpha2Api->get_self_service_registration_flow: %s\n" % e)

                if e.status == 410:
                    return self.redirect("/kratos/self-service/registration/browser")

        dao = GeographyDao(self.db)
        countries = await dao.get_countries()
        default_country = await dao.get_default_country()
        default_country = "" if default_country is None else default_country.name

        placeholders = ui_placeholders("Registrera")
        positions = ui_positions()

        self.render(
            "sign-up.html",
            action=action,
            method=method,
            errors=errors,
            nodes=sorted(nodes, key=lambda node: positions[node.attributes.name]),
            default_country=default_country,
            countries=countries,
            placeholders=placeholders
        )


class RecoveryHandler(BaseHandler):
    def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("/kratos/self-service/recovery/browser")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""
        action = ""
        state = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_recovery_flow(flow)
                action = api_response.methods["link"].config.action
                csrf_token = api_response.methods['link'].config.fields[0].value
                state = api_response.state

                if api_response.methods['link'].config.messages is not None:
                    error = api_response.methods['link'].config.messages[0].text
                else:
                    for field in api_response.methods['link'].config.fields:
                        if field.messages is not None:
                            error = field.messages[0].text
                            break
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_login_flow: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)
        logger.debug(state)

        self.render(
            "recovery.html",
            flow=flow,
            action=action,
            csrf_token=csrf_token,
            error=error,
            state=state
        )
