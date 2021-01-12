from app.models import Membership, Organization, membership_to_json
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime, timedelta
from unittest.mock import patch
from urllib.parse import urlencode
from uuid import UUID


class MembershipsTest(WebTestCase):
    def setUp(self):
        self.org = Organization()
        self.org.id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.org.name = "Piratpartiet"
        self.org.description = "Test"
        self.org.active = True
        self.org.created = datetime(2006, 1, 1)
        self.user = get_mock_session().user
        self.membership = Membership()
        self.membership.user = self.user
        self.membership.organization = self.org
        self.membership.created = datetime.utcnow()
        self.membership.renewal = datetime.utcnow() + timedelta(days=365)

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_membership(self, get_current_user):
        arguments = {
            "user": self.user.id.__str__(),
            "organization": self.org.id.__str__()
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
