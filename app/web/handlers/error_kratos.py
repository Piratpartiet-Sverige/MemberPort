import ory_kratos_client

from app.config import Config
from app.logger import logger
from app.web.handlers.base import BaseHandler
from ory_kratos_client.api import v0alpha2_api
from ory_kratos_client.configuration import Configuration


class ErrorKratosHandler(BaseHandler):
    async def get(self):
        error = self.get_argument("id", "")
        logger.debug(error)
        if (error == ""):
            return self.redirect("/")

        code = 0
        message = ""
        status = ""
        error_id = ""

        config = Config.get_config()
        url = config.get("WebServer", "url")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = v0alpha2_api.V0alpha2Api(api_client)
            try:
                api_response = api_instance.get_self_service_error(error)
                code = str(int(api_response["error"]["code"]))
                message = api_response["error"]["message"]
                status = api_response["error"]["status"]
                error_id = api_response["id"]
            except ory_kratos_client.ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_error: %s\n" % e)
            except Exception as exc:
                logger.error(exc.__str__())

        await self.render(
            "error/kratos.html",
            code=code,
            message=message,
            status=status,
            error_id=error_id,
            url=url
        )
