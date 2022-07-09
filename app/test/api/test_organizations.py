import json

from app.models import Organization
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime
from urllib.parse import urlencode
from uuid import uuid4, UUID
from unittest.mock import patch


class OrganizationsTest(WebTestCase):
    def update_organization_id(self, body):
        start_index = body.find('{"id": "') + 8
        end_index = start_index + 36
        self.org.id = UUID(body[start_index:end_index])

    def setUp(self):
        self.org = Organization()
        self.org.id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.org.name = "Piratpartiet"
        self.org.description = "Test"
        self.org.active = True
        self.org.created = datetime(2006, 1, 1)

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_organization(self, get_current_user):
        arguments = {
            "name": self.org.name,
            "description": self.org.description,
            "active": "true"
        }

        response = self.fetch(
            '/api/organization',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode()
        self.update_organization_id(body)
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "ORGANIZATION CREATED")
        self.assertEqual(json_body["data"]["id"], self.org.id.__str__())
        self.assertEqual(json_body["data"]["name"], self.org.name)
        self.assertEqual(json_body["data"]["description"], self.org.description)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_retrieve_organization(self, get_current_user):
        self.connection.fetchrow.return_value = {
            "name": self.org.name,
            "description": self.org.description,
            "active": self.org.active,
            "created": self.org.created
        }

        response = self.fetch('/api/organization/' + self.org.id.__str__(), method="GET")
        body = response.body.decode()
        self.update_organization_id(body)
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "RETRIEVED ORGANIZATION")
        self.assertEqual(json_body["data"]["id"], self.org.id.__str__())
        self.assertEqual(json_body["data"]["name"], self.org.name)
        self.assertEqual(json_body["data"]["description"], self.org.description)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)
        self.assertEqual(
            '{"success": true, "reason": "RETRIEVED ORGANIZATION", "data": {"id": "4d2b7c7b-0a9e-4b57-8a92-be29f432f429",' +
            ' "name": "Piratpartiet", "description": "Test", "active": "true",' +
            ' "created": "2006-01-01 00:00:00"}}', body)
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_organization(self, get_current_user):
        new_name = "Ung Pirat"
        new_description = "Pizza, polare, politik"
        self.connection.fetchrow.return_value = {
            "name": new_name,
            "description": new_description,
            "active": self.org.active,
            "created": self.org.created
        }

        arguments = {
            "name": new_name,
            "description": new_description
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(urlencode(arguments))
        }

        response = response = self.fetch(
            '/api/organization/' + self.org.id.__str__(),
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "ORGANIZATION UPDATED")
        self.assertEqual(json_body["data"]["id"], self.org.id.__str__())
        self.assertEqual(json_body["data"]["name"], new_name)
        self.assertEqual(json_body["data"]["description"], new_description)
        self.assertEqual(json_body["data"]["active"], self.org.active.__str__().lower())
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_fail_organization(self, get_current_user):
        new_name = "Ung Pirat"
        new_description = "Pizza, polare, politik"
        self.maxDiff = None

        arguments = {
            "name": new_name,
            "description": new_description
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(urlencode(arguments))
        }

        # Invalid UUID
        response = response = self.fetch(
            '/api/organization/' + self.org.id.__str__() + "1",
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], False)
        self.assertEqual(json_body["reason"], "ORGANIZATION UUID IS MISSING")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(400, response.code)

        # No description
        arguments = {
            "name": new_name
        }

        response = response = self.fetch(
            '/api/organization/' + self.org.id.__str__(),
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], False)
        self.assertEqual(json_body["reason"], "DESCRIPTION IS MISSING")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(422, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_organization_with_recruitment(self, get_current_user):
        new_name = "Ung Pirat"
        new_description = "Pizza, polare, politik"
        self.connection.fetchrow.return_value = {
            "name": new_name,
            "description": new_description,
            "active": self.org.active,
            "created": self.org.created
        }

        country_ids = uuid4().__str__() + "," + uuid4().__str__()

        arguments = {
            "name": new_name,
            "description": new_description,
            "countries": country_ids
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(urlencode(arguments))
        }

        response = response = self.fetch(
            '/api/organization/' + self.org.id.__str__(),
            method="PUT",
            body=urlencode(arguments),
            headers=headers
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "ORGANIZATION UPDATED")
        self.assertEqual(json_body["data"]["id"], self.org.id.__str__())
        self.assertEqual(json_body["data"]["name"], new_name)
        self.assertEqual(json_body["data"]["description"], new_description)
        self.assertEqual(json_body["data"]["active"], self.org.active.__str__().lower())
        self.assert_datetime("created", json_body["data"]["created"])
        self.assertEqual(200, response.code)
