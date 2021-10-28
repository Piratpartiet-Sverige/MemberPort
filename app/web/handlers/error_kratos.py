import ory_kratos_client

from app.config import Config
from app.logger import logger
from app.web.handlers.base import BaseHandler
from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration


class ErrorKratosHandler(BaseHandler):
    async def get(self):
        error = self.get_argument("error", default="")

        if (error == ""):
            return self.redirect("/kratos/self-service/errors")

        message = ""
        config = Config.get_config()
        url = config.get("WebServer", "url")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_error(error)
                for error in api_response.errors:
                    message = str(error["code"]) + " - " + error["message"] + "\n"
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_error: %s\n" % e)
        await self.render(
            "error/kratos.html",
            message=message,
            url=url
        )
