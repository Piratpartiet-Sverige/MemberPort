import ory_kratos_client

from ory_kratos_client.api import frontend_api
from ory_kratos_client.configuration import Configuration
from ory_kratos_client.rest import ApiException
from app.database.dao.geography import GeographyDao
from app.database.dao.organizations import OrganizationsDao
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
            api_instance = frontend_api.FrontendApi(api_client)
            try:
                api_response = api_instance.get_login_flow(flow, cookie=cookie)
                nodes = api_response.ui.nodes.value
                errors = api_response.ui.messages.value if hasattr(api_response.ui, 'messages') else []
                action = api_response.ui.action
                method = api_response.ui.method
            except ApiException as e:
                logger.error("Exception when calling FrontendApi->get_login_flow: %s\n" % e)
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
            api_instance = frontend_api.FrontendApi(api_client)
            try:
                api_response = api_instance.get_registration_flow(flow, cookie=cookie)
                nodes = api_response.ui.nodes.value
                errors = api_response.ui.messages.value if hasattr(api_response.ui, 'messages') else []
                action = api_response.ui.action
                method = api_response.ui.method
            except ApiException as e:
                logger.error("Exception when calling FrontendApi->get_registration_flow: %s\n" % e)

                if e.status == 410:
                    return self.redirect("/kratos/self-service/registration/browser")

        geo_dao = GeographyDao(self.db)
        org_dao = OrganizationsDao(self.db)

        countries = await geo_dao.get_countries()
        default_country = await geo_dao.get_default_country()
        default_country = "" if default_country is None else default_country.name

        organizations = await org_dao.get_organizations_for_signup()

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
            organizations=organizations,
            placeholders=placeholders
        )


class RecoveryHandler(BaseHandler):
    def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("/kratos/self-service/recovery/browser")

        configuration = Configuration(
            host="http://pirate-kratos:4433"
        )

        cookie = self.request.headers['Cookie']
        action = ""
        method = ""
        nodes = []
        errors = []
        state = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = frontend_api.FrontendApi(api_client)
            try:
                api_response = api_instance.get_recovery_flow(flow, cookie=cookie)
                nodes = api_response.ui.nodes.value
                errors = api_response.ui.messages.value if hasattr(api_response.ui, 'messages') else []
                action = api_response.ui.action
                method = api_response.ui.method
                state = api_response.state.value
            except ApiException as e:
                logger.error("Exception when calling FrontendApi->get_recovery_flow: %s\n" % e)

        placeholders = ui_placeholders("Registrera")

        self.render(
            "recovery.html",
            flow=flow,
            method=method,
            action=action,
            nodes=nodes,
            errors=errors,
            placeholders=placeholders,
            state=state
        )
