import json
import tornado.web

from app.config import Config
from app.database.dao.geography import GeographyDao
from app.database.dao.organizations import OrganizationsDao
from app.logger import logger
from app.web.handlers.base import BaseHandler

from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        permissions_check = self.permission_check()

        geo_dao = GeographyDao(self.db)
        default_country = await geo_dao.get_default_country()

        org_dao = OrganizationsDao(self.db)
        default_org = await org_dao.get_default_organization()

        config = Config.get_config()
        broker_url = config.get("TaskQueue", "broker_url")
        monitor_url = config.get("TaskQueue", "monitor_url")
        monitor_username = config.get("TaskQueue", "monitor_username")
        monitor_password = config.get("TaskQueue", "monitor_password")
        smtp_server = config.get("Email", "smtp_server")
        smtp_port = config.get("Email", "smtp_port")
        overview_message = ""
        response_json = None
        response_body = None
        kratos_body = ""
        http_client = AsyncHTTPClient()

        try:
            http_request_overview = HTTPRequest(
                url=monitor_url + "/api/overview",
                auth_username=monitor_username,
                auth_password=monitor_password
            )
            response = await http_client.fetch(http_request_overview)
            response_body = response.body.decode('raw_unicode_escape')
            response_json = json.loads(response.body)

            if response.code == 200:
                overview_message = "Kön är aktiv"
            else:
                overview_message = "Något är fel med kön!"
        except Exception as e:
            logger.error(e)
            overview_message = str(e)
            response_json = None
            response_body = None

        try:
            http_request_kratos = HTTPRequest(
                url="http://pirate-kratos:4433/health/ready"
            )
            kratos_response = await http_client.fetch(http_request_kratos)
            kratos_body = json.loads(kratos_response.body)

            if 'status' not in kratos_body:
                kratos_body = "Något är fel med Kratos!"
            else:
                kratos_body = kratos_body["status"]

            http_request_kratos = HTTPRequest(
                url="http://pirate-kratos:4433/admin/identities"
            )
            identities_response = await http_client.fetch(http_request_kratos)
            identities_body = json.loads(identities_response.body)

            identities_len = len(identities_body)
        except Exception as e:
            logger.error(e)
            overview_message = str(e)
            response_json = None
            response_body = None

        await self.render(
            "admin/admin.html",
            title="Admin",
            admin=permissions_check,
            broker_url=broker_url,
            monitor_url=monitor_url,
            overview_message=overview_message,
            response_json=response_json,
            response_body=response_body,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            kratos_body=kratos_body,
            identities_len=identities_len,
            default_country=default_country,
            default_org=default_org
        )
