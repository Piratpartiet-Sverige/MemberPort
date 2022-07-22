from app.database.dao.geography import GeographyDao
from app.models import municipality_to_json
from app.web.handlers.base import BaseHandler


class APIMunicipalityHandler(BaseHandler):
    async def get(self, id: str):
        municipality_id = self.check_uuid(id)

        if municipality_id is None:
            return self.respond("MUNICIPALITY UUID IS MISSING", 400)

        geo_dao = GeographyDao(self.db)

        municipality = await geo_dao.get_municipality_by_id(municipality_id)

        if municipality is None:
            return self.respond("MUNICIPALITY WITH SPECIFIED ID NOT FOUND", 404, None)

        return self.respond("RETRIEVED MUNICIPALITY", 200, municipality_to_json(municipality))

    async def post(self):
        municipality_name = self.get_argument("name", None)
        country_id = self.get_argument("country", None)
        area_id = self.get_argument("area", "")

        if municipality_name is None or country_id is None or len(municipality_name) < 1:
            return self.respond("MUNICIPALITY OR COUNTRY ID IS MISSING", 400)

        try:
            if area_id != "":
                area_id = int(area_id)
            else:
                area_id = None
        except ValueError:
            return self.respond("AREA ID MUST BE AN INTEGER", 400)

        geo_dao = GeographyDao(self.db)
        municipality = await geo_dao.create_municipality(municipality_name, country_id, area_id)

        if municipality is None:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO CREATE MUNICIPALITY", 500)

        return self.respond("MUNICIPALITY CREATED", 201, municipality_to_json(municipality))

    async def put(self, id: str):
        municipality_id = self.check_uuid(id)

        if municipality_id is None:
            return self.respond("MUNICIPALITY UUID IS MISSING", 400)

        name = self.get_body_argument("name")

        if name == "":
            return self.respond("NOT A VALID NAME", 400)

        geo_dao = GeographyDao(self.db)

        result = await geo_dao.update_municipality(municipality_id, name, None, None)
        if result is False:
            self.respond("ERROR OCCURRED WHEN TRYING TO UPDATE MUNICIPALITY", 500)

        municipality = await geo_dao.get_municipality_by_id(municipality_id)

        return self.respond("MUNICIPALITY UPDATED", 200, municipality_to_json(municipality))

    async def delete(self, id: str):
        municipality_id = self.check_uuid(id)

        if municipality_id is None:
            return self.respond("MUNICIPALITY UUID IS MISSING", 400)

        geo_dao = GeographyDao(self.db)

        result = await geo_dao.delete_municipality(municipality_id)
        if result is False:
            return self.respond("COULD NOT DELETE MUNICIPALITY! ORGANIZATION COULD BE ACTIVE IN MUNICIPALITY", 403)

        return self.respond("MUNICIPALITY DELETED", 204)
