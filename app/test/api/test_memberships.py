from app.models import Membership, membership_to_json
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import UUID


class MembershipsTest(WebTestCase):
    def setUp(self):
        created = datetime.utcnow()

        self.org_id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.user = get_mock_session().user
        self.membership = Membership()
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
