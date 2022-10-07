from app.logger import logger

from datetime import datetime
from typing import Union
from uuid import UUID, uuid4

from asyncpg import Connection
from asyncpg.exceptions import UniqueViolationError

from app.models import Membership
from app.database.dao.member_org import MemberOrgDao


class MembersDao(MemberOrgDao):
    async def create_membership(self, user_id: UUID, organization_id: UUID) -> Union[Membership, None]:
        sql = "INSERT INTO mp_memberships (id, \"user\", \"organization\", created, renewal) VALUES ($1, $2, $3, $4, $5);"

        membership_id = uuid4()
        created = datetime.utcnow()
        renewal = datetime(created.year + 1, created.month, created.day)

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, membership_id, user_id, organization_id, created, renewal)
        except UniqueViolationError as exc:
            logger.debug(exc.__str__())
            logger.warning("Tried to create membership with user ID: " + str(user_id) +
                           " and organization ID: " + str(organization_id) + " but it already existed")
            return None
        except Exception:
            logger.error("An error occured when trying to create new membership!", exc_info=True)
            return None

        membership = Membership()
        membership.id = membership_id
        membership.user_id = user_id
        membership.organization_id = organization_id
        membership.created = created
        membership.renewal = renewal

        return membership

    async def get_membership_by_id(self, membership_id: UUID) -> Union[UUID, None]:
        sql = 'SELECT "organization", "user", created, renewal FROM mp_memberships WHERE id = $1;'

        try:
            async with self.pool.acquire() as con:  # type: Connection
                row = await con.fetchrow(sql, membership_id)
        except Exception:
            logger.error("An error occured when trying to retrieve membership!", stack_info=True)
            return None

        membership = Membership()
        membership.id = membership_id
        membership.organization_id = row["organization"]
        membership.user_id = row["user"]
        membership.created = row["created"]
        membership.renewal = row["renewal"]

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
        sql = "UPDATE mp_memberships SET ("

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

    async def remove_membership(self, user_id: UUID, organization_id: UUID, reason: Union[str, None]) -> bool:
        sql = 'DELETE FROM mp_memberships WHERE "user" = $1 AND "organization" = $2;'
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, user_id, organization_id)
        except Exception:
            logger.error("An error occured when trying to delete a membership!", stack_info=True)
            return False

        sql = 'INSERT INTO mp_ended_memberships (id, "organization", reason, ended) VALUES ($1, $2, $3, $4);'

        id = uuid4()
        ended = datetime.utcnow()
        reason = "" if reason is None else reason

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, id, organization_id, reason, ended)
        except Exception:
            logger.error("An error occured when trying to delete a membership!", stack_info=True)
            return False

        return True

    async def get_member_count(self, organization_id: UUID) -> int:
        """
        Get how many users are currently registered
        :return: An int with the current user count
        """
        sql = "SELECT count(*) as members FROM mp_memberships WHERE \"organization\" = $1;"

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, organization_id)

        return row["members"]

    async def get_memberships_for_user(self, user_id: UUID) -> list:
        sql = "SELECT id, \"organization\", created, renewal FROM mp_memberships WHERE \"user\" = $1"

        try:
            async with self.pool.acquire() as con:  # type: Connection
                rows = await con.fetch(sql, user_id)
        except Exception:
            logger.error("An error occured when trying to retrieve memberships for an user!", stack_info=True)
            return list()

        if rows is None:
            return list()

        memberships = list()

        for row in rows:
            membership = Membership()
            membership.id = row["id"]
            membership.user_id = user_id
            membership.organization_id = row["organization"]
            membership.created = row["created"]
            membership.renewal = row["renewal"]
            memberships.append(membership)

        return memberships

    async def count_expired_memberships(self) -> int:
        sql = "SELECT COUNT(\"id\") FROM mp_memberships WHERE renewal < $1;"
        current_date = datetime.utcnow()

        try:
            async with self.pool.acquire() as con:  # type: Connection
                count = await con.fetchval(sql, current_date)
        except Exception:
            logger.critical("An error occured when trying to count expired memberships!")
            return 0

        return count

    async def remove_expired_memberships(self):
        sql = "DELETE FROM mp_memberships WHERE renewal < $1;"
        current_date = datetime.utcnow()

        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, current_date)
        except Exception:
            logger.critical("An error occured when trying to delete expired memberships!")
            raise
