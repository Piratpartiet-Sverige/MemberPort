import tornado

from app.database.dao.geography import GeographyDao
from app.models import country_to_json
from app.web.handlers.base import BaseHandler, has_permissions


class APICountryHandler(BaseHandler):
    async def get(self, id: str):
        country_id = self.check_uuid(id)

        if country_id is None:
            return self.respond("COUNTRY UUID IS MISSING", 400)

        geo_dao = GeographyDao(self.db)

        country = await geo_dao.get_country_by_id(country_id)

        if country is None:
            return self.respond("COUNTRY WITH SPECIFIED ID NOT FOUND", 404, None)

        return self.respond("RETRIEVED COUNTRY", 200, country_to_json(country))

    @tornado.web.authenticated
    @has_permissions("edit_geography")
    async def post(self):
        country_name = self.get_argument("name", None)

        if country_name is None or len(country_name) < 1:
            return self.respond("COUNTRY NAME IS MISSING", 400)

        geo_dao = GeographyDao(self.db)
        country = await geo_dao.create_country(country_name)

        if country is None:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO CREATE COUNTRY", 500)

        return self.respond("COUNTRY CREATED", 201, country_to_json(country))

    @tornado.web.authenticated
    @has_permissions("edit_geography")
    async def put(self, id: str):
        country_id = self.check_uuid(id)

        if country_id is None:
            return self.respond("COUNTRY UUID IS MISSING", 400)

        name = self.get_body_argument("name")

        if name == "":
            return self.respond("NOT A VALID NAME", 400)

        geo_dao = GeographyDao(self.db)

        result = await geo_dao.rename_country(country_id, name)
        if result is False:
            self.respond("ERROR OCCURRED WHEN TRYING TO UPDATE COUNTRY", 500)

        country = await geo_dao.get_country_by_id(country_id)

        return self.respond("COUNTRY UPDATED", 200, country_to_json(country))

    @tornado.web.authenticated
    @has_permissions("edit_geography")
    async def delete(self, id: str):
        country_id = self.check_uuid(id)

        if country_id is None:
            return self.respond("MUNICIPALITY UUID IS MISSING", 400)

        geo_dao = GeographyDao(self.db)

        result = await geo_dao.delete_country(country_id)
        if result is False:
            return self.respond("COULD NOT DELETE COUNTRY! ORGANIZATION COULD BE ACTIVE IN COUNTRY", 403)

        return self.respond("COUNTRY DELETED", 204)
