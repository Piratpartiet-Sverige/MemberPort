import json

from app.models import Post
from app.test.web_testcase import WebTestCase, get_mock_session
from datetime import datetime
from urllib.parse import urlencode
from uuid import uuid4, UUID
from unittest.mock import patch


class FeedsTest(WebTestCase):
    def setUp(self):
        self.post = Post()
        self.post.id = UUID('4d2b7c7b-0a9e-4b57-8a92-be29f432f429')
        self.post.title = "Nytt material"
        self.post.content = "<p>Nytt material är tillgängligt nu</p>"
        self.post.author = UUID('94983a62-8b07-4446-9753-8ba3a80d6000')
        self.post.created = datetime(2022, 4, 10)
        self.post.updated = datetime(2022, 5, 11)

        return super().setUp()

    @patch('app.web.handlers.base.BaseHandler.get_current_user', return_value=get_mock_session())
    def test_create_post(self, get_current_user):
        arguments = {
            "title": self.post.title,
            "content": self.post.content
        }

        # User permissions
        self.connection.fetch.side_effect = [[{"role": uuid4()}], ["admin"]]

        response = self.fetch(
            '/api/feed/post',
            method="POST",
            body=urlencode(arguments)
        )

        body = response.body.decode()
        json_body = json.loads(body)

        self.maxDiff = None

        self.assertEqual(json_body["success"], True)
        self.assertEqual(json_body["reason"], "POST PUBLISHED")
        self.assertNotEqual(json_body["data"]["id"], self.post.id.__str__())
        self.assertEqual(json_body["data"]["title"], self.post.title)
        self.assertEqual(json_body["data"]["content"], self.post.content)
        self.assert_datetime("created", json_body["data"]["created"])
        self.assert_datetime("updated", json_body["data"]["updated"])
        self.assertEqual(json_body["data"]["created"], json_body["data"]["updated"])
        self.assertEqual(201, response.code)
        self.connection.execute.assert_called_once()
