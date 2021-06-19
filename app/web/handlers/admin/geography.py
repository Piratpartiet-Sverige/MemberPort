import tornado.web

from app.database.dao.geography import GeographyDao
from app.web.handlers.base import BaseHandler

from uuid import UUID


class GeographyHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        permission_check = await self.permission_check()

        if permission_check is False:
            self.respond("You don't have permission to edit the geography", 403)

        dao = GeographyDao(self.db)
        countries = await dao.get_countries()
        selected_country = await dao.get_country_by_id(UUID('00000000-0000-0000-0000-000000000000'))
        municipalities = await dao.get_municipalities_by_country(selected_country.id)
        areas = await dao.get_areas_by_country(selected_country.id)

        areas = sorted(areas, key=lambda a: a.path.count('.'))

        await self.render(
            "admin/geography.html",
            admin=permission_check,
            title="Geography",
            selected_country=selected_country,
            countries=countries,
            municipalities=municipalities,
            areas=areas
        )
