from app.database.dao.geography import GeographyDao
from app.models import municipality_to_json
from app.web.handlers.base import BaseHandler
from uuid import UUID


class APIMunicipalitiesHandler(BaseHandler):
    async def get(self):
        country = self.get_argument("country", None)

        geo_dao = GeographyDao(self.db)

        if country is None:
            municipalities = await geo_dao.get_municipalities()
        else:
            if self.check_uuid(country):
                country = await geo_dao.get_country_by_id(UUID(country))
            elif country is not None:
                country = await geo_dao.get_country_by_name(country)
            municipalities = await geo_dao.get_municipalities_by_country(country.id)

        response = {}

        for municipality in municipalities:
            response[municipality.id.__str__()] = municipality_to_json(municipality)

        return self.respond("Municipalities succesfully retrieved", 200, response)
