from app.database.dao.base import BaseDao
from app.logger import logger
from app.models import Organization
from uuid import UUID
from typing import Union


# Shared methods used by members and organizations daos
class MemberOrgDao(BaseDao):
    async def remove_memberships_from_org(self, organization_id: UUID) -> bool:
        try:
            async with self.pool.acquire() as con:
                await con.execute("DELETE FROM mp_memberships WHERE organization = $1;", organization_id)
        except Exception:
            return False
        return True

    async def get_organization_by_id(self, id: UUID) -> Union[Organization, None]:
        sql = "SELECT name, description, active, created, show_on_signup, path FROM mp_organizations WHERE id = $1;"

        try:
            async with self.pool.acquire() as con:
                row = await con.fetchrow(sql, id)
        except Exception:
            logger.error("An error occured when trying to retrieve an organization by id!", stack_info=True)
            return None

        if row is None:
            logger.debug("No  organization found with ID: " + str(id))
            return None

        organization = Organization()
        organization.id = id
        organization.name = row["name"]
        organization.description = row["description"]
        organization.active = row["active"]
        organization.created = row["created"]
        organization.show_on_signup = row["show_on_signup"]
        organization.path = self._convert_from_db_path(row["path"])

        return organization

    def _convert_to_db_path(self, path: str) -> str:
        return path.replace('-', '_')

    def _convert_from_db_path(self, path_db: str) -> str:
        return path_db.replace('_', '-')
