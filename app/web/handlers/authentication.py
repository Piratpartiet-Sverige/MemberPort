import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration
from app.web.handlers.base import BaseHandler
from app.logger import logger
from tornado import httpclient  # noqa needed for kratos response


class SignInHandler(BaseHandler):
    def get(self):
        request = self.get_argument("request", default="")

        if (request == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/browser/flows/login")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                # Get the request context of browser-based registration user flows
                api_response = api_instance.get_self_service_browser_login_request(request)
                csrf_token = api_response.methods['password'].config.fields[-1].value
                if api_response.methods['password'].config.messages is not None:
                    error = api_response.methods['password'].config.messages[0].text
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_browser_login_request: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)

        self.render("sign-in.html", request=request, csrf_token=csrf_token, error=error)


class SignUpHandler(BaseHandler):
    def get(self):
        request = self.get_argument("request", default="")

        if (request == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/browser/flows/registration")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.AdminApi(api_client)
            try:
                api_response = api_instance.get_self_service_browser_registration_request(request)
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
                logger.error("Exception when calling AdminApi->get_self_service_browser_registration_request: %s\n" % e)
            except ValueError as e:
                logger.error("Exception when calling PublicApi->get_self_service_browser_registration_request: %s\n" % e)

        logger.debug("csrf_token: " + csrf_token)

        self.render("sign-up.html", request=request, csrf_token=csrf_token, error=error, inputs=inputs)
