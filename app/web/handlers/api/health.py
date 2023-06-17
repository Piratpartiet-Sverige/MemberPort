import json

from app.config import Config
from app.database.dao.geography import GeographyDao
from app.database.dao.organizations import OrganizationsDao
from app.database.dao.roles import RolesDao
from app.logger import logger
from app.models import country_to_json, organization_to_json
from app.web.handlers.base import BaseHandler

from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class APIHealthHandler(BaseHandler):
    async def get(self):
        permissions_check = False

        if self.current_user is not None:
            role_dao = RolesDao(self.db)
            permissions_check = await role_dao.check_user_permission(self.current_user.user_id, "global")

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
        kratos_body = ""
        http_client = AsyncHTTPClient()

        health_data = {
            "general": {
                "default_country": country_to_json(default_country),
                "default_org": organization_to_json(default_org),
                "smtp_server": smtp_server,
                "smtp_port": smtp_port
            }
        }

        try:
            http_request_overview = HTTPRequest(
                url=monitor_url + "/api/overview",
                auth_username=monitor_username,
                auth_password=monitor_password
            )
            response = await http_client.fetch(http_request_overview)
            response_json = json.loads(response.body)

            health_data["queue"] = response_json
            health_data["queue"]["broker_url"] = broker_url
            health_data["queue"]["monitor_url"] = monitor_url

            if response.code == 200:
                overview_message = "Queue is active"
            else:
                overview_message = "Queue is down"
        except Exception as e:
            logger.error(e)
            overview_message = str(e)
            return self.respond("HEALTH NOT OK", 500, {"message": overview_message} if permissions_check else None)

        try:
            http_request_kratos = HTTPRequest(
                url="http://pirate-kratos:4433/health/ready"
            )
            kratos_response = await http_client.fetch(http_request_kratos)
            kratos_body = json.loads(kratos_response.body)

            if 'status' not in kratos_body:
                kratos_body = "Error occured when checking health of Kratos service"

            health_data["kratos"] = kratos_body

            http_request_kratos = HTTPRequest(
                url="http://pirate-kratos:4433/admin/identities"
            )
            identities_response = await http_client.fetch(http_request_kratos)
            identities_body = json.loads(identities_response.body)

            identities_len = len(identities_body)
            health_data["kratos"]["identity_count"] = identities_len
        except Exception as e:
            logger.error(e)
            overview_message = str(e)
            return self.respond("HEALTH NOT OK", 500, {"message": overview_message} if permissions_check else None)

        health_data["message"] = overview_message

        self.respond("HEALTH OK", 200, health_data if permissions_check else None)
