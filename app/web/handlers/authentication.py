import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration
from app.database.dao.geography import GeographyDao
from app.web.handlers.base import BaseHandler
from app.logger import logger
from tornado import httpclient  # noqa needed for kratos response


class SignInHandler(BaseHandler):
    def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/login/browser")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_login_flow(flow)
                csrf_token = api_response.methods['password'].config.fields[-1].value

                if api_response.methods['password'].config.messages is not None:
                    error = api_response.methods['password'].config.messages[0].text
                else:
                    for field in api_response.methods['password'].config.fields:
                        if field.messages is not None:
                            error = field.messages[0].text
                            break
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_login_flow: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)

        self.render("sign-in.html", flow=flow, csrf_token=csrf_token, error=error)


class SignUpHandler(BaseHandler):
    async def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/registration/browser")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.AdminApi(api_client)
            try:
                api_response = api_instance.get_self_service_registration_flow(flow)
                logger.debug(api_response)
                csrf_token = api_response.methods['password'].config.fields[0].value
                inputs = api_response.methods['password'].config.fields

                if api_response.methods['password'].config.messages is not None:
                    error = api_response.methods['password'].config.messages[0].text
                else:
                    for field in api_response.methods['password'].config.fields:
                        if field.messages is not None:
                            error = field.messages[0].text
                            break
                logger.debug(error)
            except ApiException as e:
                logger.error("Exception when calling AdminApi->get_self_service_registration_flow: %s\n" % e)
            except ValueError as e:
                logger.error("Exception when calling PublicApi->get_self_service_registration_flow: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)

        dao = GeographyDao(self.db)
        countries = await dao.get_countries()
        placeholders = {
            "password": "Lösenord",
            "traits.name.first": "Förnamn",
            "traits.name.last": "Efternamn",
            "traits.postal_address.street": "Gatuadress",
            "traits.postal_address.postal_code": "Postnummer",
            "traits.postal_address.city": "Stad",
            "traits.phone": "Telefonnummer",
            "traits.email": "E-post"
        }

        positions = {
            "csrf_token": 0,
            "traits.name.first": 1,
            "traits.name.last": 2,
            "traits.email": 3,
            "traits.phone": 4,
            "password": 5,
            "traits.postal_address.street": 6,
            "traits.postal_address.postal_code": 7,
            "traits.postal_address.city": 8,
            "traits.municipality": 9,
            "traits.country": 10
        }

        self.render(
            "sign-up.html",
            flow=flow,
            csrf_token=csrf_token,
            error=error,
            inputs=sorted(inputs, key=lambda field: positions[field.name]),
            countries=countries,
            placeholders=placeholders
        )


class RecoveryHandler(BaseHandler):
    def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/recovery/browser")

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
