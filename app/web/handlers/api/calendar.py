import tornado

from app.database.dao.calendar import CalendarDao
from app.web.handlers.base import BaseHandler


class APICalendarHandler(BaseHandler):
    async def get(self):
        ics_links = await CalendarDao(self.db).get_ics_links()
        calendar = ""

        for link in ics_links:
            req = tornado.httpclient.HTTPRequest(link, follow_redirects=False)
            client = tornado.httpclient.AsyncHTTPClient()
            response = await client.fetch(req, raise_error=False)

            ical = response.body.decode('UTF-8')

            if len(calendar) == 0:
                end = ical.find("END:VCALENDAR")
                calendar += ical[:end]
            else:
                start = ical.find("BEGIN:VEVENT")
                end = ical.find("END:VCALENDAR")
                calendar += ical[start:end]

        calendar += "END:VCALENDAR"

        self.set_status(200, "CALENDAR RETURNED")
        self.write(calendar)
        self.set_header('Content-Type', 'text/calendar; charset=UTF-8')

        return self.flush()
