import json

from app.models import Membership
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import UUID


class MembershipsTest(WebTestCase):
    def update_membership_id(self, body):
        start_index = body.find('{"id": "') + 8
        end_index = start_index + 36
        self.membership_id = UUID(body[start_index:end_index])
        self.membership.id = self.membership_id

    def setUp(self):
        created = datetime.utcnow()

        self.membership_id = UUID('f161a1d9-03fc-405a-9f11-90beca8c6fd1')
        self.org_id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.user = get_mock_session().user
        self.membership = Membership()
        self.membership.id = self.membership_id
        self.membership.organization_id = self.org_id
        self.membership.user_id = self.user.id
        self.membership.created = created
        self.membership.renewal = datetime(created.year + 1, created.month, created.day)

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_membership(self, get_current_user):
        arguments = {
            "user": self.user.id.__str__(),
            "organization": self.org_id.__str__()
        }

        response = self.fetch(
            '/api/membership',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode('raw_unicode_escape')
        self.update_membership_id(body)
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "MEMBERSHIP CREATED")
        self.assertEqual(json_body["data"]["id"], self.membership_id.__str__())
        self.assertEqual(json_body["data"]["organization_id"], self.membership.organization_id.__str__())
        self.assertEqual(json_body["data"]["user_id"], self.membership.user_id.__str__())
        self.assert_datetime("created", json_body["data"]["created"])
        self.assert_datetime("renewal", json_body["data"]["renewal"])

        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_membership_with_no_user(self, get_current_user):
        arguments = {
            "user": "",
            "organization": self.org_id.__str__()
        }

        response = self.fetch(
            '/api/membership',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode('raw_unicode_escape')
        json_body = json.loads(body)

        self.assertEqual(json_body["success"], False)
        self.assertEqual(json_body["reason"], "ORGANIZATION OR USER NOT SPECIFIED")
        self.assertEqual(json_body["data"], None)
        self.assertEqual(400, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_end_membership(self, get_current_user):
        arguments = {
            "reason": "I was not happy :("
        }

        self.connection.fetchrow.return_value = {
            "organization": self.membership.organization_id,
            "user": self.membership.user_id,
            "created": self.membership.created,
            "renewal": self.membership.renewal
        }

        response = self.fetch(
            '/api/membership/' + self.membership_id.__str__(),
            method="DELETE",
            body=urlencode(arguments),
            allow_nonstandard_methods=True
        )

        self.assertEqual("MEMBERSHIP ENDED", response.reason)
        self.assertEqual(204, response.code)
