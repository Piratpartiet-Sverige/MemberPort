import tornado.web

from app.database.dao.calendar import CalendarDao
from app.web.handlers.base import BaseHandler


class CalendarHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        calendar_dao = CalendarDao(self.db)

        calendars = await calendar_dao.get_calendars()

        await self.render(
            "admin/calendar.html",
            admin=True,
            title="Kalender",
            calendars=calendars
        )
