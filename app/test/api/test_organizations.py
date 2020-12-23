from app.models import Organization
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime
from uuid import UUID
from unittest.mock import patch


class OrganizationsTest(WebTestCase):
    def setUp(self):
        self.org = Organization()
        self.org.id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.org.name = "Piratpartiet"
        self.org.description = "Test"
        self.org.active = True
        self.org.created = datetime(2006, 1, 1)

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_retrieve_organization(self, get_current_user):
        with patch("app.database.dao.member_org.MemberOrgDao.get_organization_by_id", return_value=self.org) as mock_method:
            response = self.fetch('/api/organization/4d2b7c7b-0a9e-4b57-8a92-be29f432f429', method="GET")
            body = response.body.decode()
            mock_method.assert_called_once()
        self.maxDiff = None
        self.assertEqual(
            '{"success": true, "reason": "RETRIEVED ORGANIZATION", "data": {"id": "4d2b7c7b-0a9e-4b57-8a92-be29f432f429",' +
            ' "name": "Piratpartiet", "description": "Test", "active": "true",' +
            ' "created": "2006-01-01 00:00:00"}}', body)
        self.assertEqual(200, response.code)
