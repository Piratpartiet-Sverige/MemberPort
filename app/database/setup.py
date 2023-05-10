from asyncpg import UndefinedTableError
from asyncpg.pool import Pool
from app.logger import logger
from app.web.handlers.error import ErrorDatabase
from app.web.handlers.kratos import KratosHandler
from app.web.handlers.setup import SetupHandler


async def db_setup(pool: Pool, handlers: list):
    new_version = get_new_version_number()
    current_version = 0

    sql = """SELECT s.version FROM mp_settings s JOIN (
                SELECT version, MAX(created) AS created
                FROM mp_settings se
                GROUP BY version
            ) lastEntry ON s.version = lastEntry.version AND s.created = lastEntry.created;"""

    try:
        async with pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql)

        if row["version"] is None:
            logger.info("No version info in database found, initializing new database")
            await initialize_db(pool, handlers)
        else:
            current_version = row["version"]
            if new_version > current_version:
                logger.info("Upgrading database from version " + str(current_version) + " to version " + str(new_version))
                await upgrade_db(pool, current_version, new_version)
            elif new_version < current_version:
                logger.critical(
                    "Database numbers mismatch, the \"new\" version number is older than the current one." +
                    "This could be because of a failed downgrade!"
                )
                raise RuntimeError(
                    "Database numbers mismatch, the \"new\" version number is older than the current one." +
                    "This could be because of a failed downgrade!"
                )
            else:
                logger.info("No action required for database")
    except UndefinedTableError:
        logger.info("No version info in database found, initializing new database")
        await initialize_db(pool, handlers)


async def first_setup(pool, handlers):
    sql = """SELECT s.initialized FROM mp_settings s JOIN (
                SELECT initialized, MAX(created) AS created
                FROM mp_settings se
                GROUP BY initialized
            ) lastEntry ON s.initialized = lastEntry.initialized AND s.created = lastEntry.created;"""

    try:
        async with pool.acquire() as con:
            row = await con.fetchrow(sql)
    except Exception:
        logger.critical("Could not retrieve settings from database!", exc_info=1)
        show_db_error(handlers)
        return

    if row["initialized"] is False:
        logger.info("Starting first time setup")
        handlers.clear()
        handlers.append((r"/kratos/(.*)", KratosHandler))
        handlers.append((r"/", SetupHandler))


def get_new_version_number():
    version = ""
    last_line = ""
    with open('app/database/sql/db.sql', 'r') as sql_file:
        last_line = sql_file.readlines()[-1]

    for char in last_line:
        if char.isdigit():
            version += char

    return int(version)


async def initialize_db(pool: Pool, handlers: list):
    result = await initialize_tables(pool)
    if result is True:
        result = await initialize_geography(pool)
    if result is True:
        logger.info("Succesfully initialized new database!")
    else:
        logger.critical("Something went wrong when initializing new database!")
        show_db_error(handlers)


async def initialize_tables(pool: Pool) -> bool:
    with open('app/database/sql/db.sql', 'r') as sql_file:
        sql = sql_file.read()
        try:
            async with pool.acquire() as con:  # type: Connection
                await con.execute(sql)
            logger.info("Succesfully initialized essential data and tables!")
        except Exception:
            logger.critical("Could not initialize database due to SQL error!", exc_info=1)
            return False

    return True


async def initialize_geography(pool: Pool) -> bool:
    with open('app/database/sql/geography.sql', 'r') as sql_file:
        sql = sql_file.read()
        try:
            async with pool.acquire() as con:  # type: Connection
                await con.execute(sql)
            logger.info("Succesfully initialized geography data!")
        except Exception:
            logger.critical("Could not initialize database due to SQL error!", exc_info=1)
            return False

    return True


async def upgrade_db(pool: Pool, current_version: int, new_version: int):
    for version in range(current_version, new_version):
        try:
            with open('app/database/sql/upgrades/' + str(version) + '_to_' + str(version + 1) + '.sql', 'r') as sql_file:
                sql = sql_file.read()
                try:
                    async with pool.acquire() as con:  # type: Connection
                        await con.execute(sql)
                    logger.info("Succesfully upgraded database from version " + str(version) + " to " + str(version + 1))
                except Exception:
                    logger.critical(
                        "Could not upgrade database from version " + str(version) + " to " + str(version + 1) + " due to SQL error!",
                        exc_info=1
                    )
        except FileNotFoundError:
            logger.critical(
                "Could not upgrade database from version " + str(version) + " to " + str(version + 1) + " due to no upgrade script found!",
                exc_info=1
            )
            break


def show_db_error(handlers: list) -> None:
    handlers.clear()
    handlers.append((r"/", ErrorDatabase))
