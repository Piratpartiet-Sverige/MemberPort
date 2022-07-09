import tornado.web

from app.web.handlers.base import BaseHandler
from app.database.dao.geography import GeographyDao
from app.database.dao.organizations import OrganizationsDao
from uuid import UUID


class EditOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        id = UUID(self.get_argument("id"))
        org_dao = OrganizationsDao(self.db)
        organization = await org_dao.get_organization_by_id(id)
        country_ids = await org_dao.get_recruitment_countries(id)
        area_ids = await org_dao.get_recruitment_areas(id)
        municipality_ids = await org_dao.get_recruitment_municipalities(id)

        geo_dao = GeographyDao(self.db)
        selected_country = await geo_dao.get_default_country()
        municipalities = await geo_dao.get_municipalities_by_country(selected_country.id)
        areas = await geo_dao.get_areas_by_country(selected_country.id)

        await self.render(
            "admin/edit-organization.html",
            admin=True,
            title="Ändra förening",
            organization=organization,
            country=selected_country,
            areas=areas,
            municipalities=municipalities,
            country_ids=country_ids,
            area_ids=area_ids,
            municipality_ids=municipality_ids
        )
