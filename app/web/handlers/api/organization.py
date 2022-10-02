import tornado.web

from app.web.handlers.base import BaseHandler, has_permissions
from app.database.dao.organizations import OrganizationsDao
from app.logger import logger
from app.models import organization_to_json
from uuid import UUID


class APIOrganizationHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, id: str):
        org_id = self.check_uuid(id)
        if org_id is None:
            return self.respond("ORGANIZATION UUID IS MISSING", 400)

        organization = await OrganizationsDao(self.db).get_organization_by_id(org_id)
        return self.respond("RETRIEVED ORGANIZATION", 200, organization_to_json(organization))

    @tornado.web.authenticated
    @has_permissions("create_organizations")
    async def post(self):
        name = self.get_argument("name")
        description = self.get_argument("description")
        parent_id = self.get_argument("parent_id", None)
        parent_id = self.check_uuid(parent_id)
        active = self.get_argument("active", False)
        active = active == 'true'

        org_dao = OrganizationsDao(self.db)

        organization = await org_dao.create_organization(name, description, active, parent_id)

        if organization is None:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO CREATE ORGANIZATION", 500, None)

        countries_id = self.get_argument("countries", None)
        areas_id = self.get_argument("areas", None)
        municipalities_id = self.get_argument("municipalities", None)

        if countries_id is not None or areas_id is not None or municipalities_id is not None:
            try:
                countries_id = list(map(UUID, countries_id.split(','))) if countries_id != "" and countries_id is not None else list()
                areas_id = list(map(int, areas_id.split(','))) if areas_id != "" and areas_id is not None else list()

                if municipalities_id and municipalities_id is not None != "":
                    municipalities_id = list(map(UUID, municipalities_id.split(',')))
                else:
                    municipalities_id = list()

            except ValueError:
                logger.error(
                    "Recruitment areas contained invalid UUID when trying to set them for org: %s",
                    organization.id.__str__(),
                    stack_info=True
                )
                return self.respond("INVALID UUID IN RECRUITMENT AREAS", 400, None)

            success = await org_dao.set_recruitment_areas(organization.id, countries_id, areas_id, municipalities_id)
            if success is False:
                return self.respond("SOMETHING WENT WRONG WHEN TRYING TO SET RECRUITMENT AREAS", 500, None)

        return self.respond("ORGANIZATION CREATED", 200, organization_to_json(organization))

    @tornado.web.authenticated
    @has_permissions("edit_organizations")
    async def put(self, id: UUID = None):
        org_id = self.check_uuid(id)
        if org_id is None:
            return self.respond("ORGANIZATION UUID IS MISSING", 400)

        name = self.get_argument("name", None)
        description = self.get_argument("description", None)
        active = self.get_argument("active", False)
        active = active == 'true'
        update_parent = False

        parent_id = self.get_argument("parent_id", None)
        if parent_id is not None:
            update_parent = True
        parent_id = self.check_uuid(parent_id)

        if name is None:
            return self.respond("NAME IS MISSING", 422)
        if description is None:
            return self.respond("DESCRIPTION IS MISSING", 422)

        countries_id = self.get_argument("countries", None)
        areas_id = self.get_argument("areas", None)
        municipalities_id = self.get_argument("municipalities", None)

        org_dao = OrganizationsDao(self.db)

        if countries_id is not None or areas_id is not None or municipalities_id is not None:
            try:
                countries_id = list(map(UUID, countries_id.split(','))) if countries_id != "" and countries_id is not None else list()
                areas_id = list(map(int, areas_id.split(','))) if areas_id != "" and areas_id is not None else list()

                if municipalities_id and municipalities_id is not None != "":
                    municipalities_id = list(map(UUID, municipalities_id.split(',')))
                else:
                    municipalities_id = list()

            except ValueError:
                logger.error(
                    "Recruitment areas contained invalid UUID when trying to set them for org: %s",
                    org_id.__str__(),
                    stack_info=True
                )
                return self.respond("INVALID UUID IN RECRUITMENT AREAS", 400, None)

            success = await org_dao.set_recruitment_areas(org_id, countries_id, areas_id, municipalities_id)
            if success is False:
                return self.respond("SOMETHING WENT WRONG WHEN TRYING TO SET RECRUITMENT AREAS", 500, None)

        organization = await org_dao.update_organization(org_id, name, description, active, update_parent, parent_id)
        if organization is None:
            return self.respond("SOMETHING WENT WRONG WHEN TRYING TO UPDATE ORGANIZATION", 500, None)

        return self.respond("ORGANIZATION UPDATED", 200, organization_to_json(organization))

    @tornado.web.authenticated
    @has_permissions("delete_organizations")
    async def delete(self, id: str = None):
        org_id = self.check_uuid(id)
        if org_id is None:
            return self.respond("ORGANIZATION UUID IS MISSING", 400)
        if not await OrganizationsDao(self.db).delete_organization(org_id):
            return self.respond("INTERNAL SERVER ERROR", 500)
        return self.respond("ORGANIZATION DELETED", 204)
