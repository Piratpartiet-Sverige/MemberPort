from app.models import Country, country_to_json
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

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_update_country_name(self, get_current_user):
        arguments = {
            "name": "Norge"
        }

        # For some reason, headers must be set for PUT requests but not POST
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Content-Length': len(urlencode(arguments))
        }

        with patch("app.database.dao.geography.GeographyDao.rename_country", return_value=self.country) as rename_country:
            with patch("app.database.dao.geography.GeographyDao.get_country_by_id", return_value=self.country) as get_country:
                response = self.fetch(
                    '/api/geography/country/4d2b7c7b-0a9e-4b57-8a92-be29f432f429',
                    method="PUT",
                    body=urlencode(arguments),
                    headers=headers
                )
                body = response.body.decode('raw_unicode_escape')
                get_country.assert_called_once_with(self.country.id)

            rename_country.assert_called_once_with(self.country.id, "Norge")

        self.maxDiff = None

        self.assertEqual(
            '{"success": true, "reason": "COUNTRY UPDATED", "data": ' +
            country_to_json(self.country).__str__().replace("'", "\"") + '}',
            body
        )
        self.assertEqual(200, response.code)
