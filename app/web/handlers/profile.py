import tornado.web
import ory_kratos_client

from ory_kratos_client.api import frontend_api
from ory_kratos_client.rest import ApiException
from ory_kratos_client.configuration import Configuration

from app.database.dao.geography import GeographyDao
from app.database.dao.members import MembersDao
from app.database.dao.organizations import OrganizationsDao
from app.logger import logger
from app.models import ui_placeholders, ui_positions
from app.web.handlers.base import BaseHandler


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        flow = self.get_argument("flow", default="")

        if (flow == ""):
            return self.redirect("/kratos/self-service/settings/browser")

        configuration = Configuration(
            host="http://pirate-kratos:4433"
        )

        cookie = self.request.headers['Cookie']
        errors = []
        nodes = []
        action = ""
        method = ""
        state = ""

        with ory_kratos_client.ApiClient(configuration) as api_client:
            api_instance = frontend_api.FrontendApi(api_client)
            try:
                api_response = api_instance.get_settings_flow(flow, cookie=cookie)
                state = api_response.state.value
                errors = api_response.ui.messages.value if hasattr(api_response.ui, 'messages') else []
                nodes = api_response.ui.nodes.value
                action = api_response.ui.action
                method = api_response.ui.method
            except ApiException as e:
                logger.error("Exception when calling FrontendApi->get_settings_flow: %s\n" % e)

                if e.status == 410:
                    return self.redirect("/kratos/self-service/settings/browser")

        placeholders = ui_placeholders("Spara")
        positions = ui_positions()

        permissions_check = await self.permission_check()

        if self.current_user.bot is not None:
            return await self.render(
                "profile.html",
                title="Profil",
                admin=permissions_check,
                action=action,
                method=method,
                state=state,
                errors=errors,
                nodes=sorted(nodes, key=lambda node: positions[node.attributes.name]),
                placeholders=placeholders,
                positions=positions,
                countries=[],
                municipalities=[],
                memberships=[],
                member_orgs=[],
                organizations=[]
            )

        members_dao = MembersDao(self.db)
        memberships = await members_dao.get_memberships_for_user(self.current_user.user_id)
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
            method=method,
            state=state,
            errors=errors,
            nodes=sorted(nodes, key=lambda node: positions[node.attributes.name]),
            placeholders=placeholders,
            positions=positions,
            countries=countries,
            municipalities=municipalities,
            memberships=memberships,
            member_orgs=member_orgs,
            organizations=organizations
        )
