import json

from app.models import Calendar
from app.test.web_testcase import WebTestCase, get_mock_session, set_permissions
from datetime import datetime
from urllib.parse import urlencode
from uuid import UUID
from unittest.mock import patch


class CalendarsTest(WebTestCase):
    def setUp(self):
        self.calendar = Calendar()
        self.calendar.id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.calendar.description = "Kalender"
        self.calendar.ics_url = "https://www.example.com"
        self.calendar.created = datetime(2022, 4, 10)

        return super().setUp()

    @set_permissions("edit_calendar")
    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_calendar(self, get_current_user):
        arguments = {
            "description": self.calendar.description,
            "url": self.calendar.ics_url
        }

        response = self.fetch(
            '/api/calendar',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode()
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "CALENDAR CREATED")
        self.assertNotEqual(json_body["data"]["id"], self.calendar.id.__str__())
        self.assertEqual(json_body["data"]["description"], self.calendar.description)
        self.assertEqual(json_body["data"]["ics_url"], self.calendar.ics_url)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(201, response.code)
        self.connection.execute.assert_called_once()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_get_calendar_by_id(self, get_current_user):
        self.connection.fetchrow.return_value = {
            "id": self.calendar.id,
            "description": self.calendar.description,
            "ics_url": self.calendar.ics_url,
            "created": self.calendar.created
        }

        response = self.fetch(
            '/api/calendar/' + self.calendar.id.__str__(),
            method="GET"
        )

        body = response.body.decode()
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "RETRIEVED CALENDAR")
        self.assertEqual(json_body["data"]["id"], self.calendar.id.__str__())
        self.assertEqual(json_body["data"]["description"], self.calendar.description)
        self.assertEqual(json_body["data"]["ics_url"], self.calendar.ics_url)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)
        self.connection.fetchrow.assert_called_once()

    @set_permissions("edit_calendar")
    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_delete_calendar(self, get_current_user):
        self.connection.fetchrow.return_value = {
            "id": self.calendar.id,
            "description": self.calendar.description,
            "ics_url": self.calendar.ics_url,
            "created": self.calendar.created
        }

        response = self.fetch(
            '/api/calendar/' + self.calendar.id.__str__(),
            method="DELETE"
        )

        body = response.body.decode()
        self.assertEqual(len(body), 0)

        self.maxDiff = None

        self.assertEqual(response.reason, "CALENDAR DELETED")
        self.assertEqual(204, response.code)
        self.connection.execute.assert_called_once()

    @set_permissions("edit_calendar")
    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_calendar(self, get_current_user):
        new_description = "New description here"

        arguments = {
            "description": new_description
        }

        self.connection.fetchrow.return_value = {
            "id": self.calendar.id,
            "description": new_description,
            "ics_url": self.calendar.ics_url,
            "created": self.calendar.created
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(urlencode(arguments))
        }

        response = self.fetch(
            '/api/calendar/' + self.calendar.id.__str__(),
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode()
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "CALENDAR UPDATED")
        self.assertEqual(json_body["data"]["id"], self.calendar.id.__str__())
        self.assertEqual(json_body["data"]["description"], new_description)
        self.assertEqual(json_body["data"]["ics_url"], self.calendar.ics_url)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)
        self.connection.execute.assert_called_once()
        self.connection.fetchrow.assert_called_once()
