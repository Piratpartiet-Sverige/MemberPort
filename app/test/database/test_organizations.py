from tornado.testing import gen_test
from asyncpg import Connection
from unittest.mock import MagicMock

from app.database.dao.organizations import OrganizationsDao
from app.test.web_testcase import WebTestCase


class OrganizationsTest(WebTestCase):
    def test_create_organization(self):
        # dao = OrganizationsDao(self.db)
        con = Connection()
        con.execute = MagicMock(return_value=3)
        con.execute.assert_called_with("TEST", 3, 4, 5, 6)
        response = self.fetch('/api/scan/1', method="POST", body="{}")
        body = response.body.decode()

        self.assertEqual('{"success": false, "reason": "CODE UUID IS MISSING", "data": null}', body)
        self.assertEqual(400, response.code)
