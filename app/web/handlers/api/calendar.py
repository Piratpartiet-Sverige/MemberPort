import tornado

from app.database.dao.calendar import CalendarDao
from app.logger import logger
from app.models import calendar_to_json
from app.web.handlers.base import BaseHandler


class APICalendarHandler(BaseHandler):
    async def get(self, id: str = None):
        if id is None:
            return await self.return_ical()

        calendar_id = self.check_uuid(id)
        if calendar_id is None:
            return self.respond("INVALID UUID", 400)
        else:
            calendar = await CalendarDao(self.db).get_calendar_by_id(calendar_id)

            if calendar is None:
                return self.respond("COULD NOT FIND CALENDAR WITH ID: " + calendar_id.__str__(), 404)
            else:
                return self.respond("RETRIEVED CALENDAR", 200, calendar_to_json(calendar))

    async def return_ical(self):
        calendars = await CalendarDao(self.db).get_calendars()
        ical = ""

        for calendar in calendars:
            req = tornado.httpclient.HTTPRequest(calendar.ics_url, follow_redirects=False)
            client = tornado.httpclient.AsyncHTTPClient()

            try:
                response = await client.fetch(req, raise_error=False)
            except Exception as exc:
                logger.debug(exc.__str__())
                logger.error("Calendar with URL: " + calendar.ics_url + " caused an exception when doing a request. Is the URL correct?")
                continue

            ical_response = response.body.decode('UTF-8')

            if len(ical) == 0:
                end = ical_response.find("END:VCALENDAR")
                ical += ical_response[:end]
            else:
                start = ical_response.find("BEGIN:VEVENT")
                end = ical_response.find("END:VCALENDAR")
                ical += ical_response[start:end]

            ical_response = ""

        ical += "END:VCALENDAR"

        self.set_status(200, "CALENDAR RETURNED")
        self.write(ical)
        self.set_header('Content-Type', 'text/calendar; charset=UTF-8')

        return self.flush()

    async def post(self):
        description = self.get_argument("description", None)
        url = self.get_argument("url", None)

        if description is None or url is None:
            return self.respond("DESCRIPTION OR URL IS MISSING", 400)

        req = tornado.httpclient.HTTPRequest(url, follow_redirects=False)
        client = tornado.httpclient.AsyncHTTPClient()

        try:
            await client.fetch(req, raise_error=False)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("Exception raised when trying URL: " + url + ". Is the URL correct?")
            return self.respond("INVALID URL", 400)

        calendar = await CalendarDao(self.db).create_calendar(description, url)

        if calendar is None:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO CREATE CALENDAR", 500)

        return self.respond("CALENDAR CREATED", 201, calendar_to_json(calendar))

    async def put(self, id: str):
        calendar_id = self.check_uuid(id)
        if calendar_id is None:
            return self.respond("INVALID UUID", 400)

        description = self.get_argument("description", None)
        url = self.get_argument("url", None)

        if description is None and url is None:
            return self.respond("DESCRIPTION OR URL IS MISSING", 400)

        calendar = await CalendarDao(self.db).update_calendar(calendar_id, description, url)

        if calendar is None:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO UPDATE CALENDAR", 500)

        return self.respond("CALENDAR UPDATED", 201, calendar_to_json(calendar))

    async def delete(self, id: str):
        calendar_id = self.check_uuid(id)
        if calendar_id is None:
            return self.respond("INVALID UUID", 400)

        calendar_dao = CalendarDao(self.db)

        calendar = await calendar_dao.get_calendar_by_id(calendar_id)

        if calendar is None:
            return self.respond("CALENDAR DOES NOT EXIST", 404)

        result = await calendar_dao.delete_calendar(calendar_id)

        if result is True:
            return self.respond("CALENDAR DELETED", 204)
        else:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO DELETE CALENDAR", 500)
