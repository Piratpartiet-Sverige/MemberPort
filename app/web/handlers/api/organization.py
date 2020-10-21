import tornado.web

from app.web.handlers.base import BaseHandler
from app.database.dao.organizations import OrganizationsDao
from app.models import organization_to_json


class APIOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        name = self.get_argument("name")
        description = self.get_argument("description")
        organization = await (OrganizationsDao(self.db).create_organization(name, description))
        return self.respond("ORGANIZATION CREATED", 200, organization_to_json(organization))
