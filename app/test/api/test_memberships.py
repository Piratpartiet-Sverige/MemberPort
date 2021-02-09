from app.models import Membership, membership_to_json
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import UUID


class MembershipsTest(WebTestCase):
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

        with patch("app.database.dao.members.MembersDao.create_membership", return_value=self.membership) as mock_method:
            response = self.fetch(
                '/api/membership',
                method="POST",
                body=urlencode(arguments)
            )

            body = response.body.decode('raw_unicode_escape')
            mock_method.assert_called_once()

        self.assertEqual(
            '{"success": true, "reason": "MEMBERSHIP CREATED", "data": ' +
            membership_to_json(self.membership).__str__().replace("'", "\"") + '}',
            body
        )
        self.assertEqual(200, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_membership_with_no_user(self, get_current_user):
        arguments = {
            "user": "",
            "organization": self.org_id.__str__()
        }

        with patch("app.database.dao.members.MembersDao.create_membership", return_value=self.membership) as mock_method:
            response = self.fetch(
                '/api/membership',
                method="POST",
                body=urlencode(arguments)
            )

            body = response.body.decode('raw_unicode_escape')
            mock_method.assert_not_called()

        self.assertEqual(
            '{"success": false, "reason": "ORGANIZATION OR USER NOT SPECIFIED", "data": null}',
            body
        )
        self.assertEqual(400, response.code)

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_end_membership(self, get_current_user):
        arguments = {
            "reason": "I was not happy :("
        }

        with patch("app.database.dao.members.MembersDao.get_membership_by_id", return_value=self.membership) as get_mock_method:
            with patch("app.database.dao.members.MembersDao.remove_membership", return_value=True) as remove_mock_method:
                response = self.fetch(
                    '/api/membership/' + UUID('f161a1d9-03fc-405a-9f11-90beca8c6fd1').__str__(),
                    method="DELETE",
                    body=urlencode(arguments),
                    allow_nonstandard_methods=True
                )

                get_mock_method.assert_called_once()
                remove_mock_method.assert_called_once()

        self.assertEqual("MEMBERSHIP ENDED", response.reason)
        self.assertEqual(204, response.code)
