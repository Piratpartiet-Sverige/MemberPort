from app.database.dao.geography import GeographyDao
from app.models import area_to_json
from app.web.handlers.base import BaseHandler


class APIAreaHandler(BaseHandler):
    async def get(self, id: str):
        area_id = id

        if area_id is None or area_id == "":
            return self.respond("AREA UUID IS MISSING", 400)

        geo_dao = GeographyDao(self.db)

        area = await geo_dao.get_area_by_id(area_id)

        if area is None:
            return self.respond("AREA WITH SPECIFIED ID NOT FOUND", 404, None)

        return self.respond("RETRIEVED AREA", 200, area_to_json(area))

    async def put(self, id: str):
        try:
            area_id = int(id)
        except Exception:
            return self.respond("NOT A VALID AREA ID", 400)

        name = self.get_body_argument("name", None)
        country_id = self.get_body_argument("country_id", None)
        path = self.get_body_argument("path", None)

        country_id = self.check_uuid(country_id)

        if name is not None and name == "":
            return self.respond("NOT A VALID NAME", 400)
        elif name is None and country_id is None and path is None:
            return self.respond("NO VALUES WERE GIVEN", 400)

        geo_dao = GeographyDao(self.db)

        result = await geo_dao.update_area(area_id, name, country_id, path)
        if result is False:
            return self.respond("ERROR OCCURRED WHEN TRYING TO UPDATE AREA", 500)

        area = await geo_dao.get_area_by_id(area_id)

        return self.respond("AREA UPDATED", 200, area_to_json(area))
