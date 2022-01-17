import json

from app.database.dao.geography import GeographyDao
from app.logger import logger
from app.models import area_to_json
from app.web.handlers.base import BaseHandler


class APIAreasHandler(BaseHandler):
    async def put(self):
        try:
            data = json.loads(self.request.body)
        except Exception as exc:
            logger.error("Could not load data into JSON object, bad request?")
            logger.debug(exc)
            return self.respond("WRONG DATA FORMAT", 400)
        finally:
            dao = GeographyDao(self.db)
            updated_areas = {}

            for area_id in data:
                if "path" not in data[area_id]:
                    continue

                try:
                    area_id_int = int(area_id)
                except Exception:
                    return self.respond("NOT A VALID AREA ID: " + area_id, 400)

                result = await dao.update_area(area_id_int, None, None, data[area_id]["path"])
                if not result:
                    return self.respond("SOMETHING WENT WRONG WHEN TRYING TO UPDATE AREAS", 500, None)

            for area_id in data:
                area = await dao.get_area_by_id(int(area_id))
                if area is not None:
                    updated_areas[area_id] = area_to_json(area)
                else:
                    return self.respond("COULD NOT RETRIEVE UPDATED AREAS, SOMETHING COULD HAVE GONE WRONG", 500, None)

            return self.respond("AREAS UPDATED", 200, updated_areas)
