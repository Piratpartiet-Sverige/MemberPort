import json
import tornado

from app.database.dao.geography import GeographyDao
from app.logger import logger
from app.models import municipality_to_json
from app.web.handlers.base import BaseHandler, has_permissions
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

        return self.respond("MUNICIPALITIES SUCCESSFULLY RETRIEVED", 200, response)

    @tornado.web.authenticated
    @has_permissions("edit_geography")
    async def put(self):
        try:
            data = json.loads(self.request.body)
        except Exception as exc:
            logger.error("Could not load data into JSON object, bad request?")
            logger.debug(exc)
            return self.respond("WRONG DATA FORMAT", 400)
        finally:
            dao = GeographyDao(self.db)
            updated_municipalities = {}

            for municipality_id in data:
                if "area" not in data[municipality_id]:
                    continue

                try:
                    municipality_id_uuid = UUID(municipality_id)
                except Exception:
                    return self.respond("NOT A VALID MUNICIPALITY ID: " + municipality_id, 400)

                result = await dao.update_municipality(municipality_id_uuid, None, None, int(data[municipality_id]["area"]))
                if not result:
                    return self.respond("SOMETHING WENT WRONG WHEN TRYING TO UPDATE MUNICIPALITIES", 500, updated_municipalities)
                else:
                    municipality = await dao.get_municipality_by_id(municipality_id)
                    if municipality is not None:
                        updated_municipalities[municipality_id] = municipality_to_json(municipality)

            return self.respond("MUNICIPALITIES UPDATED", 200, updated_municipalities)
