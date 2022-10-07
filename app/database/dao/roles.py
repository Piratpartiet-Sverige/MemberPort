from app.logger import logger

from uuid import UUID
from app.models import Role
from app.models import Permission

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError
from app.database.dao.base import BaseDao


class RolesDao(BaseDao):
    async def get_roles(self) -> list:
        sql = "SELECT id, name, description FROM mp_roles;"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        except Exception:
            logger.error("An error occured when trying to retrieve roles!", stack_info=True)
            return list()

        roles = list()

        for row in rows:
            role = Role()
            role.id = row["id"]
            role.name = row["name"]
            role.description = row["description"]
            roles.append(role)

        return roles

    async def get_permissions(self) -> list:
        sql = "SELECT id, name FROM mp_permissions;"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql)
        except Exception:
            logger.error("An error occured when trying to retrieve permissions!", stack_info=True)
            return list()

        permissions = list()

        for row in rows:
            permission = Permission()
            permission.id = row["id"]
            permission.name = row["name"]
            permissions.append(permission)

        return permissions

    async def get_permissions_by_role(self, role_id: UUID) -> list:
        sql = 'SELECT "permission" FROM mp_role_permissions WHERE "role" = $1;'

        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, role_id)
        except Exception:
            logger.error("An error occured when trying to retrieve permissions by role!", stack_info=True)
            return list()

        permissions = list()

        for row in rows:
            logger.debug(row["permission"])
            sql = 'SELECT id, name FROM mp_permissions WHERE id = $1;'

            async with self.pool.acquire() as con:  # type: Connection
                p_rows = await con.fetch(sql, row["permission"])

            for p_row in p_rows:
                permission = Permission()
                permission.id = p_row["id"]
                permission.name = p_row["name"]
                permissions.append(permission)

        return permissions

    async def add_permission_to_role(self, role_id: UUID, permission_id: str):
        sql = 'INSERT INTO mp_role_permissions ("role", "permission") VALUES ($1, $2);'
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, role_id, permission_id)
        except UniqueViolationError:
            logger.debug("Permission " + permission_id + " was already added to role: " + str(role_id))
        except Exception:
            logger.error("An error occured when trying to add permission to role!", stack_info=True)

    async def remove_permission_from_role(self, role_id: UUID, permission_id: str):
        sql = 'DELETE FROM mp_role_permissions WHERE "role" = $1 AND "permission" = $2;'
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, role_id, permission_id)
        except Exception:
            logger.error("An error occured when trying to remove permission from role!", stack_info=True)

    async def check_user_permission(self, user_id: UUID, permission_id: str) -> bool:
        sql = 'SELECT "role" FROM mp_user_roles WHERE "user" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            rows = await con.fetch(sql, user_id)

        for role in rows:
            sql = 'SELECT "permission" FROM mp_role_permissions WHERE "role" = $1;'

            async with self.pool.acquire() as con:  # type: Connection
                permissions = await con.fetch(sql, role["role"])

            for p in permissions:
                if permission_id == p["permission"]:
                    return True

        return False
