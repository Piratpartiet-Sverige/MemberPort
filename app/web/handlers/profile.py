import tornado.web
import ory_kratos_client

from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration

from app.database.dao.geography import GeographyDao
from app.database.dao.members import MembersDao
from app.database.dao.organizations import OrganizationsDao
from app.database.dao.users import UsersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("http://127.0.0.1:8888/kratos/self-service/settings/browser")

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        csrf_token = ""  # noqa: S105 # nosec
        error = ""
        action = ""
        success = False

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            try:
                api_response = api_instance.get_self_service_settings_flow(flow)

                success = True if api_response.state == "success" else False

                if api_response.methods["profile"].config.messages is not None:
                    error = api_response.methods["profile"].config.messages[0].text
                else:
                    for field in api_response.methods['profile'].config.fields:
                        if field.messages is not None:
                            error = field.messages[0].text
                            break

                action = api_response.methods["profile"].config.action
                csrf_token = api_response.methods["profile"].config.fields[0].value
            except ApiException as e:
                logger.error("Exception when calling PublicApi->get_self_service_settings_flow: %s\n" % e)

        dao = UsersDao(self.db)
        permissions_check = await dao.check_user_admin(self.current_user.user.id)

        members_dao = MembersDao(self.db)
        memberships = await members_dao.get_memberships_for_user(self.current_user.user.id)
        member_orgs = list()

        for membership in memberships:
            member_orgs.append(await members_dao.get_organization_by_id(membership.organization_id))

        geo_dao = GeographyDao(self.db)
        country = await geo_dao.get_country_by_name(self.current_user.user.country)
        countries = await geo_dao.get_countries()
        municipality = await geo_dao.get_municipality_by_name(self.current_user.user.municipality)
        areas = await geo_dao.get_parent_areas_from_municipality(municipality.id)

        org_dao = OrganizationsDao(self.db)
        organizations = await org_dao.get_organizations_in_area(country.id, areas, municipality.id, member_orgs)

        if country is not None:
            municipalities = await geo_dao.get_municipalities_by_country(country.id)

        await self.render(
            "profile.html",
            title="Profil",
            admin=permissions_check,
            action=action,
            success=success,
            error=error,
            csrf_token=csrf_token,
            countries=countries,
            municipalities=municipalities,
            memberships=memberships,
            member_orgs=member_orgs,
            organizations=organizations
        )

    @tornado.web.authenticated
    async def post(self):
        flow = self.get_argument("flow", default="")

        if flow == "":
            self.respond("No flow ID was found", 400)
            return

        configuration = Configuration()
        configuration.host = "http://pirate-kratos:4433"

        with ory_kratos_client.ApiClient(configuration, cookie="ory_kratos_session=" + self.session_hash + ";") as api_client:
            api_instance = ory_kratos_client.PublicApi(api_client)
            body = ory_kratos_client.CompleteSelfServiceBrowserSettingsStrategyProfileFlowPayload()
            try:
                api_instance.complete_self_service_settings_methods_profile(flow, body)
            except ApiException as e:
                logger.error("Exception when calling PublicApi->complete_self_service_browser_settings_profile_strategy_flow: %s\n" % e)
                self.respond("API exception against Kratos", 500)
                return

        self.respond("Profile succesfully updated", 200)
