import os
import sys

import tornado.web
import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration

from app.database.dao.users import UsersDao
from app.database.dao.settings import SettingsDao
from app.database.dao.organizations import OrganizationsDao
from app.logger import logger
from app.web.handlers.base import BaseHandler
from uuid import uuid4


class SetupHandler(BaseHandler):
    async def get(self):
        logger.debug("Entered setup handler...")

        await self.render("setup.html")

    async def post(self):
        logger.debug("Completing setup...")

        settings_dao = SettingsDao(self.db)

        if await settings_dao.is_initialized():
            return self.respond("Crew DB is already initialized", 400)

        org_name = self.get_argument("org.name")
        org_description = self.get_argument("org.description")

        org_dao = OrganizationsDao(self.db)
        organization = await org_dao.create_organization(org_name, org_description)

        if organization is None:
            return self.respond("Something went wrong when creating organization", 500)

        result = await settings_dao.set_default_organization(organization.id)

        if result is False:
            return self.respond("Something went wrong when setting default organization", 500)

        await settings_dao.set_initialized(True)

        return self.respond("Setup finished", 200)

        """
        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"

        name = self.get_argument("traits.name")
        email = self.get_argument("traits.email")

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = ory_kratos_client.AdminApi(api_client)
            body = ory_kratos_client.Identity(
                id = uuid4().__str__(),
                schema_id = "bot",
                traits = {
                    "name": name,
                    "email": email
                }
            )

            try:
                api_response = api_instance.create_identity(body)
                logger.debug(api_response)

                dao = SettingsDao(self.db)
                await dao.set_initialized(True)

                self.respond("Setup finished", 200)

            except ApiException as e:
                logger.error("Exception when calling AdminApi->create_identity: %s\n" % e)
        
        self.respond("Something went wrong", 500)
        """
