import json

from app.models import Area, Country
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime
from uuid import UUID
from unittest.mock import patch
from urllib.parse import urlencode


class GeographyTest(WebTestCase):
    def setUp(self):
        self.country = Country()
        self.country.id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.country.name = "Sverige"
        self.country.created = datetime(2020, 1, 1)

        self.area = Area()
        self.area.id = 1
        self.area.name = "Norra distriktet"
        self.area.created = datetime(2020, 1, 2)
        self.area.country_id = self.country.id
        self.area.path = "1"

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_retrieve_country(self, get_current_user):
        self.connection.fetchrow.return_value = {
            "id": self.country.id.__str__(),
            "name": self.country.name,
            "created": self.country.created,
        }

        response = self.fetch('/api/geography/country/' + self.country.id.__str__(), method="GET")

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "RETRIEVED COUNTRY")
        self.assertEqual(json_body["data"]["id"], self.country.id.__str__())
        self.assertEqual(json_body["data"]["name"], self.country.name)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_country_name(self, get_current_user):
        new_name = "Norge"
        arguments = {
            "name": new_name
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(urlencode(arguments))
        }

        self.connection.fetchrow.return_value = {
            "name": new_name,
            "created": self.country.created,
        }

        response = self.fetch(
            '/api/geography/country/4d2b7c7b-0a9e-4b57-8a92-be29f432f429',
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "COUNTRY UPDATED")
        self.assertEqual(json_body["data"]["id"], self.country.id.__str__())
        self.assertEqual(json_body["data"]["name"], new_name)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_retrieve_area(self, get_current_user):
        self.connection.fetchrow.return_value = {
            "name": self.area.name,
            "created": self.area.created,
            "country": self.area.country_id,
            "path": self.area.path
        }

        response = self.fetch('/api/geography/area/' + self.area.id.__str__(), method="GET")

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "RETRIEVED AREA")
        self.assertEqual(json_body["data"]["id"], self.area.id.__str__())
        self.assertEqual(json_body["data"]["name"], self.area.name)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_area_name(self, get_current_user):
        new_name = "Södra distriktet"
        arguments = {
            "name": new_name
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(urlencode(arguments))
        }

        self.connection.fetchrow.return_value = {
            "name": new_name,
            "created": self.area.created,
            "country": self.area.country_id,
            "path": self.area.path
        }

        response = self.fetch(
            '/api/geography/area/1',
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "AREA UPDATED")
        self.assertEqual(json_body["data"]["id"], self.area.id.__str__())
        self.assertEqual(json_body["data"]["name"], new_name)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)
