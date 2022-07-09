import json

from app.models import Area, Country, Municipality
from app.test.web_testcase import MagicMockContext, WebTestCase, get_mock_session
from asyncpg.exceptions import ForeignKeyViolationError
from asyncpg.transaction import Transaction
from datetime import datetime
from uuid import uuid4, UUID
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

        self.municipality = Municipality()
        self.municipality.id = UUID('03e3274f-43b4-4a92-8f66-407b3cf55aac')
        self.municipality.name = "Lund"
        self.municipality.created = datetime(2020, 1, 2)
        self.municipality.country_id = self.country.id
        self.municipality.area_id = self.area.id

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_country(self, get_current_user):
        new_country = "Atlantis"
        arguments = {
            "name": new_country
        }

        response = self.fetch(
            '/api/geography/country',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assert_uuid("country_id", json_body["data"]["id"])

        self.connection.execute.assert_called()
        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "COUNTRY CREATED")
        self.assertEqual(json_body["data"]["name"], new_country)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(201, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_retrieve_country(self, get_current_user):
        self.connection.fetchrow.return_value = {
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
    def test_delete_country(self, get_current_user):
        self.connection.transaction.return_value = MagicMockContext(Transaction)

        response = self.fetch(
            '/api/geography/country/' + self.country.id.__str__(),
            method="DELETE"
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.connection.execute.assert_called()
        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "COUNTRY DELETED")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_delete_fail_country(self, get_current_user):
        self.connection.transaction.return_value = MagicMockContext(Transaction)
        self.connection.execute.side_effect = ForeignKeyViolationError()

        response = self.fetch(
            '/api/geography/country/' + self.country.id.__str__(),
            method="DELETE"
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.connection.execute.assert_called_once()
        self.assertEqual(json_body["success"], False)
        self.assertEqual(json_body["reason"], "COULD NOT DELETE COUNTRY! ORGANIZATION COULD BE ACTIVE IN COUNTRY")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(403, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_area(self, get_current_user):
        new_id = 5
        self.connection.fetchval.side_effect = [str(self.area.id), new_id]
        new_area = "Österbotten"
        arguments = {
            "name": new_area,
            "country": str(self.country.id),
            "parent": str(self.area.id)
        }

        response = self.fetch(
            '/api/geography/area',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(int(json_body["data"]["id"]), 5)

        self.connection.fetchval.assert_called()
        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "AREA CREATED")
        self.assertEqual(json_body["data"]["name"], new_area)
        self.assertEqual(json_body["data"]["country_id"], str(self.country.id))
        self.assertEqual(json_body["data"]["path"], str(self.area.id) + "." + str(new_id))
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(201, response.code)

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

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_delete_area(self, get_current_user):
        self.connection.transaction.return_value = MagicMockContext(Transaction)

        response = self.fetch(
            '/api/geography/area/' + self.area.id.__str__(),
            method="DELETE"
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.connection.execute.assert_called()
        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "AREA DELETED")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_delete_fail_area(self, get_current_user):
        self.connection.transaction.return_value = MagicMockContext(Transaction)
        self.connection.execute.side_effect = ForeignKeyViolationError()

        response = self.fetch(
            '/api/geography/area/' + self.area.id.__str__(),
            method="DELETE"
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.connection.execute.assert_called_once()
        self.assertEqual(json_body["success"], False)
        self.assertEqual(json_body["reason"], "COULD NOT DELETE AREA! ORGANIZATION COULD BE ACTIVE IN AREA")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(403, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_municipality(self, get_current_user):
        new_municipality = "Oslo"
        arguments = {
            "name": new_municipality,
            "country": str(self.country.id),
            "area": str(self.area.id)
        }

        response = self.fetch(
            '/api/geography/municipality',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assert_uuid("municipality_id", json_body["data"]["id"])
        self.connection.execute.assert_called()
        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "MUNICIPALITY CREATED")
        self.assertEqual(json_body["data"]["name"], new_municipality)
        self.assertEqual(json_body["data"]["country_id"], str(self.country.id))
        self.assertEqual(json_body["data"]["area_id"], str(self.area.id))
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(201, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_retrieve_municipality(self, get_current_user):
        self.connection.fetchrow.return_value = {
            "name": self.municipality.name,
            "created": self.municipality.created,
            "country": self.municipality.country_id,
            "area": self.municipality.area_id
        }

        response = self.fetch('/api/geography/municipality/' + self.municipality.id.__str__(), method="GET")

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "RETRIEVED MUNICIPALITY")
        self.assertEqual(json_body["data"]["id"], self.municipality.id.__str__())
        self.assertEqual(json_body["data"]["name"], self.municipality.name)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(json_body["data"]["country_id"], self.municipality.country_id.__str__())
        self.assertEqual(json_body["data"]["area_id"], self.municipality.area_id.__str__())
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_municipality_name(self, get_current_user):
        new_name = "Luleå"
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
            "created": self.municipality.created,
            "country": self.municipality.country_id,
            "area": self.municipality.area_id
        }

        response = self.fetch(
            '/api/geography/municipality/' + self.municipality.id.__str__(),
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "MUNICIPALITY UPDATED")
        self.assertEqual(json_body["data"]["id"], self.municipality.id.__str__())
        self.assertEqual(json_body["data"]["name"], new_name)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(json_body["data"]["country_id"], self.municipality.country_id.__str__())
        self.assertEqual(json_body["data"]["area_id"], self.municipality.area_id.__str__())
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_delete_municipality(self, get_current_user):
        response = self.fetch(
            '/api/geography/municipality/' + self.municipality.id.__str__(),
            method="DELETE"
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.connection.execute.assert_called_once()
        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "MUNICIPALITY DELETED")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_delete_fail_municipality(self, get_current_user):
        self.connection.execute.side_effect = ForeignKeyViolationError()

        response = self.fetch(
            '/api/geography/municipality/' + self.municipality.id.__str__(),
            method="DELETE"
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.connection.execute.assert_called_once()
        self.assertEqual(json_body["success"], False)
        self.assertEqual(json_body["reason"], "COULD NOT DELETE MUNICIPALITY! ORGANIZATION COULD BE ACTIVE IN MUNICIPALITY")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(403, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_areas_path(self, get_current_user):
        self.connection.fetchrow.side_effect = [
            {"name": self.area.name, "created": self.area.created, "country": self.country.id, "path": "3.2.1"},
            {"name": "Östra distriktet", "created": self.area.created, "country": self.country.id, "path": "3.2"}
        ]
        self.connection.fetchval.side_effect = [
            1,
            "4.5.1",
            1,
            "2"
        ]

        arguments = {
            "1": {"path": "2.1"},
            "2": {"path": "3.2"}
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(json.dumps(arguments))
        }

        response = self.fetch(
            '/api/geography/areas',
            method="PUT",
            body=json.dumps(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(self.connection.execute.call_count, 2)
        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "AREAS UPDATED")
        self.assertEqual(json_body["data"]["2"]["path"], "3.2")
        self.assertEqual(json_body["data"]["1"]["path"], "3.2.1")
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_municipalities_areas(self, get_current_user):
        municipality_id = uuid4()

        self.connection.fetchrow.side_effect = [
            {"name": self.municipality.name, "created": self.municipality.created, "country": self.country.id, "area": self.area.id},
            {"name": "Luleå", "created": self.municipality.created, "country": self.country.id, "area": "3"}
        ]

        arguments = {
            self.municipality.id.__str__(): {"area": self.area.id.__str__()},
            municipality_id.__str__(): {"area": "3"}
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(json.dumps(arguments))
        }

        response = self.fetch(
            '/api/geography/municipalities',
            method="PUT",
            body=json.dumps(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "MUNICIPALITIES UPDATED")
        self.assertEqual(200, response.code)
        self.assertEqual(json_body["data"][municipality_id.__str__()]["area_id"], "3")
        self.assertEqual(json_body["data"][self.municipality.id.__str__()]["area_id"], self.area.id.__str__())
        self.assertEqual(self.connection.execute.call_count, len(arguments))
