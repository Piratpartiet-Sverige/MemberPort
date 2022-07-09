import tornado.web

from app.web.handlers.base import BaseHandler
from app.database.dao.geography import GeographyDao


class AddOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        geo_dao = GeographyDao(self.db)
        selected_country = await geo_dao.get_default_country()
        municipalities = await geo_dao.get_municipalities_by_country(selected_country.id)
        areas = await geo_dao.get_areas_by_country(selected_country.id)

        await self.render(
            "admin/add-organization.html",
            admin=True,
            title="Lägg till förening",
            country=selected_country,
            areas=areas,
            municipalities=municipalities,
        )
