import tornado.web
import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration

from app.database.dao.organizations import OrganizationsDao
from app.database.dao.members import MembersDao
from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler
from uuid import UUID


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        request = self.get_argument("request", default="")

        if (request == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/browser/flows/settings")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        csrf_token = ""
        error = ""
        action = ""

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_browser_settings_request(request)

                if api_response.methods["profile"].config.messages != None:
                    error = api_response.methods["profile"].config.messages[0].text
                
                action = api_response.methods["profile"].config.action
                csrf_token = api_response.methods["profile"].config.fields[0].value
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_browser_settings_request: %s\n" % e)

        dao = UsersDao(self.db)
        permissions_check = await dao.check_user_admin(self.current_user.user.id)

        members_dao = MembersDao(self.db)
        memberships = await members_dao.get_memberships_for_user(user=self.current_user.user)

        if len(memberships) == 0:
            logger.debug("Creating membership")
            org_dao = OrganizationsDao(self.db)
            await members_dao.create_membership(self.current_user.user.id, (await org_dao.get_default_organization()).id)

        if error != "":
            logger.error("Error: " + error.message)

        await self.render(
            "profile.html",
            title="Profil",
            admin=permissions_check,
            user=self.current_user.user,
            action=action,
            error=error,
            csrf_token=csrf_token,
            memberships=memberships
        )

    @tornado.web.authenticated
    async def post(self):
        request = self.get_argument("request", default="")

        if request == "":
            self.respond("No request ID was found", 400)
            return

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            body = ory_kratos_client.CompleteSelfServiceBrowserSettingsStrategyProfileFlowPayload()
            try:
                api_instance.complete_self_service_browser_settings_profile_strategy_flow(request, body)
            except ApiException as e:
                logger.error("Exception when calling PublicApi->complete_self_service_browser_settings_profile_strategy_flow: %s\n" % e)
                self.respond("API exception against Kratos", 500)
                return

        self.respond("Profile succesfully updated", 200)