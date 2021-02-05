from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import UUID

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError

from app.models import User, Membership
from app.database.dao.member_org import MemberOrgDao


class MembersDao(MemberOrgDao):
    async def create_membership(self, user_id: UUID, organization_id: UUID) -> Union[Membership, None]:
        sql = "INSERT INTO memberships (\"user\", \"organization\", created, renewal) VALUES ($1, $2, $3, $4);"

        created = datetime.utcnow()
        renewal = datetime(created.year + 1, created.month, created.day)

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, organization_id, created, renewal)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to create membership with user ID: " + str(user_id) +
                           " and organization ID: " + str(organization_id) + " but it already existed")
            return None
        except Exception:
            logger.error("An error occured when trying to create new membership!", stack_info=True)
            return None

        membership = Membership()
        membership.user = user_id
        membership.organization = organization_id
        membership.created = created
        membership.renewal = renewal

        return membership

    async def update_membership(self, user_id: UUID, organization_id: UUID,
                                created: Union[datetime, None] = None, renewal: Union[datetime, None] = None) -> bool:
        sql = self._construct_sql_string_update(created, renewal)

        if sql is None:
            return False

        try:
            if created is not None and renewal is None:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, user_id, organization_id, created)
            elif renewal is not None and created is None:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, user_id, organization_id, renewal)
            else:
                async with self.pool.acquire() as con:  # type: Connection
                    await con.execute(sql, user_id, organization_id, created, renewal)
        except Exception:
            logger.error("An error occured when trying to update a membership!", stack_info=True)
            return False

        return True

    def _construct_sql_string_update(self, created: Union[datetime, None] = None,
                                     renewal: Union[datetime, None] = None) -> Union[str, None]:
        sql = "UPDATE memberships SET ("

        value_count = 0

        if created is not None:
            value_count += 1
            sql += "created"
        if renewal is not None:
            value_count += 1
            if sql.endswith("created"):
                sql += ", "
            sql += "renewal"

        if value_count == 0:
            logger.debug("Nothing to update membership with...")
            return None

        sql += ") VALUES ($1"

        if value_count == 2:
            sql += ", $2"

        sql += ");"

        logger.debug(sql)

        return sql

    async def remove_membership(self, user_id: UUID, organization_id: UUID) -> bool:
        sql = 'DELETE FROM memberships WHERE "user" = $1 AND "organization" = $2;'
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, organization_id)
        except Exception:
            logger.error("An error occured when trying to delete a membership!", stack_info=True)
            return False

        return True

    async def get_member_count(self, organization_id: UUID) -> int:
        """
        Get how many users are currently registered
        :return: An int with the current user count
        """
        sql = "SELECT count(*) as members FROM memberships WHERE \"organization\" = $1;"

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, organization_id)

        return row["members"]

    async def get_memberships_for_user(self, user: User) -> list:
        sql = "SELECT \"organization\", created, renewal FROM memberships WHERE \"user\" = $1"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, user.id)
        except Exception:
            logger.error("An error occured when trying to retrieve memberships for an user!", stack_info=True)
            return list()

        if rows is None:
            return list()

        memberships = list()

        for row in rows:
            membership = Membership()
            membership.user = user
            membership.organization = await self.get_organization_by_id(row["organization"])
            membership.created = row["created"]
            membership.renewal = row["renewal"]
            memberships.append(membership)

        return memberships
