import tornado.web

from app.web.handlers.base import BaseHandler
from app.database.dao.geography import GeographyDao
from app.database.dao.organizations import OrganizationsDao
from app.models import Organization


class EditOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        org_id = self.get_argument("id", None)
        org_id = self.check_uuid(org_id)

        if org_id is None:
            return self.respond("Organization ID was missing or not valid", 400, None, True)

        organization = Organization()
        organization.id = org_id

        org_dao = OrganizationsDao(self.db)
        organizations = await org_dao.get_organizations("", "name", False)

        pos = organizations.index(organization)
        organization = organizations[pos]
        organizations.pop(pos)

        parent_id = organization.path.split('.')
        if len(parent_id) < 2:
            parent_id = org_id.__str__()
        else:
            parent_id = parent_id[-2]

        country_ids = await org_dao.get_recruitment_countries(org_id)
        area_ids = await org_dao.get_recruitment_areas(org_id)
        municipality_ids = await org_dao.get_recruitment_municipalities(org_id)

        geo_dao = GeographyDao(self.db)
        selected_country = await geo_dao.get_default_country()
        municipalities = await geo_dao.get_municipalities_by_country(selected_country.id)
        areas = await geo_dao.get_areas_by_country(selected_country.id)

        await self.render(
            "admin/edit-organization.html",
            admin=True,
            title="Ändra förening",
            organization=organization,
            organizations=organizations,
            parent_id=parent_id,
            country=selected_country,
            areas=areas,
            municipalities=municipalities,
            country_ids=country_ids,
            area_ids=area_ids,
            municipality_ids=municipality_ids
        )
