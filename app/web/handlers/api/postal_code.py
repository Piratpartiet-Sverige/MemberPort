import tornado.web
import ast

from app.config import Config
from app.logger import logger
from app.web.handlers.base import BaseHandler


class APIPostalCodeHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self, postal_code: str):
        config = Config.get_config()
        pap_api_key = config.get("PAP-API", "key")

        if postal_code is None:
            return self.respond("Postal code is missing", 400)
        elif len(postal_code) != 5 or postal_code.isnumeric() is False:
            return self.respond("Badly formatted postal code", 400)

        url = "https://api.papapi.se/lite/?query=" + postal_code + "&format=json&apikey=" + pap_api_key

        req = tornado.httpclient.HTTPRequest(url, follow_redirects=False)
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield client.fetch(req, raise_error=False)

        if response.code == 404:
            return self.respond("Postal code doesn't exist", 404)
        elif response.code == 403:
            return self.respond("Maximum amount of requests has been sent to PAP-API Lite for today", 500)

        dict_str = response.body.decode("UTF-8")
        data = ast.literal_eval(dict_str)
        logger.debug(data)

        result = {
            'postal_code': {
                'city': data["results"][0]["city"],
                'municipality': data["results"][0]["county"]
            }
        }

        return self.respond("Postal code succesfully retrieved", 200, result)
