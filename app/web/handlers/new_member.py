import json

from app.database.dao.users import UsersDao
from app.database.dao.members import MembersDao
from app.logger import logger
from app.web.handlers.base import BaseHandler


class NewMemberHandler(BaseHandler):
    async def prepare(self):
        if 'Content-Type' in self.request.headers.keys() and self.request.headers['Content-Type'] == 'application/json':
            self.args = json.loads(self.request.body)

    def check_xsrf_cookie(_xsrf):
        pass

    async def post(self):
        logger.debug("Setting up new user")
        logger.debug(self.args)
        flow = self.args.get("flow", None)
        flow = self.check_uuid(flow)

        if flow is None:
            return self.respond("INVALID UUID FOR FLOW", 400, None)

        dao = UsersDao(self.db)

        number = await dao.get_new_member_number(flow)

        response = {
            "identity": {
                "metadata_public": {
                    "member_number": str(number)
                }
            }
        }

        self.set_status(200, "SETUP OF NEW USER COMPLETE")

        return self.write(response)


class NewMembershipHandler(BaseHandler):
    async def prepare(self):
        if 'Content-Type' in self.request.headers.keys() and self.request.headers['Content-Type'] == 'application/json':
            self.args = json.loads(self.request.body)

    def check_xsrf_cookie(_xsrf):
        pass

    async def post(self):
        logger.debug("Setting up new membership")
        logger.debug(self.args)
        identity = self.args.get("identity", None)
        identity = self.check_uuid(identity)

        if identity is None:
            return self.respond("INVALID UUID FOR IDENTITY", 400, None)

        organizations = self.args.get("organizations", [])
        logger.debug(organizations)

        if len(organizations) == 0:
            logger.error("Organization ID was not provided")
            return self.respond("ORGANIZATIONS WERE MISSING", 400, None)

        org_ids = []
        for org_id in organizations:
            org_id = self.check_uuid(org_id)

            if org_id is None:
                return self.respond("INVALID UUID FOR ORGANIZATIONS", 400, None)

            org_ids.append(org_id)

        member_dao = MembersDao(self.db)

        for org_id in org_ids:
            membership = await member_dao.create_membership(identity, org_id)
            if membership is None:
                return self.respond("SOMETHING WENT WRONG WHEN TRYING TO ADD USER TO ORGANIZATION", 500, None)

        return self.respond("SETUP OF NEW MEMBERSHIPS COMPLETE", 200, None)
