from uuid import uuid4, UUID

from asyncpg import Connection, UniqueViolationError
from asyncpg.pool import Pool

from app.logger import logger


class EmailDao:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create_email_verify_link(self, email: str) -> str:
        sql = 'INSERT INTO email_verify_links ("email", link) VALUES ($1, $2)'

        confirm_link_uid = uuid4()

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, email, confirm_link_uid)

        return '/api/user/email/' + confirm_link_uid.__str__()

    async def create_password_reset_link(self, email: str) -> str:
        sql = 'INSERT INTO password_reset_links ("email", link) VALUES ($1, $2)'

        confirm_link_uid = uuid4()

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, email, confirm_link_uid)

        return '/api/password/' + confirm_link_uid.__str__()

    async def get_verify_link_for_email(self, email: str) -> str:
        sql = 'SELECT link FROM email_verify_links WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, email)

        if row is None or row["link"] is None or row["link"] == "":
            logger.warning("No verify link found for e-mail: " + email)
            logger.warning("Returning empty string...")
            return ""

        return '/api/user/email/' + row["link"].__str__()

    async def get_password_reset_link(self, email: str) -> str:
        sql = 'SELECT link FROM password_reset_links WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, email)

        if row is None or row["link"] is None or row["link"] == "":
            logger.warning("No password reset link found for e-mail: " + email)
            logger.warning("Returning empty string...")
            return ""

        return '/api/password/' + row["link"].__str__()

    async def get_email_by_password_reset_link(self, link: UUID) -> str:
        sql = 'SELECT "email" FROM password_reset_links WHERE link = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, link)

        if row is None or row["email"] is None or row["email"] == "":
            logger.warning("No e-mail found for password reset link: " + link.__str__())
            logger.warning("Returning empty string...")
            return ""

        return row["email"]

    async def remove_verify_link_for_email(self, email: str):
        sql = 'DELETE FROM email_verify_links WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, email)

        logger.info("Verify link for e-mail: " + email + " was removed")

    async def remove_password_reset_link_for_email(self, email: str):
        sql = 'DELETE FROM password_reset_links WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, email)

        logger.info("Password reset link for e-mail: " + email + " was removed")

    async def verify_email_by_link(self, link: UUID) -> bool:
        sql = 'SELECT "email" FROM email_verify_links WHERE link = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql, link)

        if row is None or row["email"] is None or row["email"] == "":
            logger.debug('Verify ID: "' + link.__str__() + '" was not associated with any email')
            return False

        email = row["email"]

        sql = 'INSERT INTO verified_emails ("email") VALUES ($1);'
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, email)
        except Exception as e:
            logger.error('Failed to insert email "' + email + '" into database table "verified_emails"')
            logger.error(str(e))
            return False

        logger.debug('E-mail: "' + email + '" was verified')

        sql = 'DELETE FROM email_verify_links WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, email)

        return True

    async def verify_email(self, email: str) -> bool:
        sql = 'INSERT INTO verified_emails ("email") VALUES ($1);'
        try:
            async with self.pool.acquire() as con:  # type: Connection
                await con.execute(sql, email)
        except UniqueViolationError as exc:
            logger.debug(exc)
            logger.warning('E-mail: ' + email + ' was already verified')
        except Exception as e:
            logger.error('Failed to insert email "' + email + '" into database table "verified_emails"')
            logger.error(str(e))
            return False

        logger.info('E-mail: "' + email + '" was verified')

        sql = 'DELETE FROM email_verify_links WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, email)

        return True

    async def unverify_email(self, email: str):
        sql = 'DELETE FROM verified_emails WHERE "email" = $1;'

        async with self.pool.acquire() as con:  # type: Connection
            await con.execute(sql, email)

        logger.info("E-mail: " + email + " was unverified")
