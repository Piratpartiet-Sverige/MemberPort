
from app.database.dao.organizations import OrganizationsDao
from app.database.dao.roles import RolesDao
from app.database.dao.settings import SettingsDao
from app.logger import logger
from app.web.handlers.base import BaseHandler

from datetime import datetime, timezone

import ory_kratos_client
from ory_kratos_client.api import identity_api
from ory_kratos_client.configuration import Configuration
from ory_kratos_client.model.create_identity_body import CreateIdentityBody
from ory_kratos_client.model.identity_state import IdentityState
from ory_kratos_client.model.identity_with_credentials import IdentityWithCredentials
from ory_kratos_client.model.identity_with_credentials_password import IdentityWithCredentialsPassword
from ory_kratos_client.model.identity_with_credentials_password_config import IdentityWithCredentialsPasswordConfig
from ory_kratos_client.model.recovery_identity_address import RecoveryIdentityAddress
from ory_kratos_client.model.verifiable_identity_address import VerifiableIdentityAddress

from uuid import uuid4, UUID


class SetupHandler(BaseHandler):
    async def get(self):
        logger.debug("Entered setup handler...")

        await self.render("setup.html")

    async def post(self):
        logger.debug("Completing setup...")

        settings_dao = SettingsDao(self.db)

        if await settings_dao.is_initialized():
            return self.respond("MemberPort is already initialized", 400)

        org_name = self.get_argument("org.name")
        org_description = self.get_argument("org.description")
        feed_url = self.get_argument("feed_url")
        name = self.get_argument("name")
        email = self.get_argument("email")
        password = self.get_argument("password")

        countries = list()
        countries.append(UUID('00000000-0000-0000-0000-000000000000'))

        org_dao = OrganizationsDao(self.db)
        organization = await org_dao.create_organization(org_name, org_description, True, True, None, countries)

        if organization is None:
            return self.respond("Something went wrong when creating organization", 500)

        result = await settings_dao.set_default_organization(organization.id)

        if result is False:
            return self.respond("Something went wrong when setting default organization", 500)

        result = await settings_dao.set_feed_url(feed_url)

        if result is False:
            return self.respond("Something went wrong when setting the feed url", 500)

        logger.debug("Creating first admin user...")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4434"
        created = datetime.now(timezone.utc)

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = identity_api.IdentityApi(api_client)

            create_identity_body = CreateIdentityBody(
                credentials=IdentityWithCredentials(
                    password=IdentityWithCredentialsPassword(
                        config=IdentityWithCredentialsPasswordConfig(
                            password=password
                        ),
                    ),
                ),
                metadata_admin=None,
                metadata_public=None,
                recovery_addresses=[
                    RecoveryIdentityAddress(
                        id=uuid4().__str__(),
                        created_at=created,
                        updated_at=created,
                        value=email,
                        via="email",
                    ),
                ],
                schema_id="bot",
                state=IdentityState("active"),
                traits={
                    "name": name,
                    "email": email
                },
                verifiable_addresses=[
                    VerifiableIdentityAddress(
                        created_at=created,
                        status="verified",
                        updated_at=created,
                        value=email,
                        verified=True,
                        verified_at=created,
                        via="email",
                    ),
                ],
            )

            try:
                api_response = api_instance.create_identity(create_identity_body=create_identity_body)
                logger.debug(api_response)

                admin_id = UUID(api_response.id)
                roles_dao = RolesDao(self.db)

                result = await roles_dao.add_role_to_user(admin_id, UUID('00000000-0000-0000-0000-000000000000'))

                if result is False:
                    return self.respond("Something went wrong when adding permissions to the admin account", 500)
            except ory_kratos_client.ApiException as e:
                logger.debug("Exception when calling IdentityApi->create_identity: %s\n" % e)
                return self.respond("Something went wrong when creating the admin user", 500)

        await settings_dao.set_initialized(True)

        return self.respond("Setup finished", 200)
