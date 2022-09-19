import tornado.web

from app.database.dao.organizations import OrganizationsDao
from app.database.dao.feed import FeedDao
from app.models import post_to_json
from app.web.handlers.base import BaseHandler, has_permissions


class APIPostHandler(BaseHandler):
    @tornado.web.authenticated
    @has_permissions("communicate_newsfeed")
    async def post(self):
        feed_dao = FeedDao(self.db)

        title = self.get_argument("title", None)
        content = self.get_argument("content", None)

        if title is None:
            return self.respond("TITLE PROPERTY IS MISSING", 400, None)
        elif content is None:
            return self.respond("CONTENT PROPERTY IS MISSING", 400, None)
        elif title == "":
            return self.respond("TITLE CAN NOT BE EMPTY", 422, None)
        elif content == "":
            return self.respond("CONTENT CAN NOT BE EMPTY", 422, None)

        org_dao = OrganizationsDao(self.db)
        org = await org_dao.get_default_organization()

        post = await feed_dao.create_post(
            title,
            content,
            self.current_user.user.id,
            [org]
        )

        if post is None:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO CREATE POST", 500, None)

        return self.respond("POST PUBLISHED", 201, post_to_json(post))
