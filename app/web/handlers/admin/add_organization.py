import tornado.web

from app.web.handlers.base import BaseHandler
from app.database.dao.geography import GeographyDao
from app.database.dao.organizations import OrganizationsDao


class AddOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        geo_dao = GeographyDao(self.db)
        selected_country = await geo_dao.get_default_country()
        municipalities = await geo_dao.get_municipalities_by_country(selected_country.id)
        areas = await geo_dao.get_areas_by_country(selected_country.id)

        org_dao = OrganizationsDao(self.db)
        organizations = await org_dao.get_organizations("", "name", False)

        await self.render(
            "admin/add-organization.html",
            admin=True,
            title="Lägg till förening",
            country=selected_country,
            areas=areas,
            municipalities=municipalities,
            organizations=organizations
        )
