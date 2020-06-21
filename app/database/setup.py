from uuid import uuid4, UUID
from asyncpg import Connection, UniqueViolationError, UndefinedTableError
from asyncpg.pool import Pool
from app.logger import logger


async def db_setup(pool: Pool):
    new_version = get_new_version_number()
    current_version = 0

    sql = """SELECT s.version FROM settings s JOIN (
                SELECT version, MAX(created) AS created
                FROM settings se
            ) lastEntry ON s.version = lastEntry.version AND s.created = lastEntry.created;"""
    
    try:
        async with pool.acquire() as con:  # type: Connection
            row = await con.fetchrow(sql)
    
        if row["version"] is None:
            logger.info("No version info in database found, initializing new database")
            initialize_db()
        else:
            current_version = row["version"]
            if new_version > current_version:
                logger.info("Upgrading database from version " + str(current_version) + " to version " + str(new_version))
                upgrade_db(current_version, new_version)
            elif new_version < current_version:
                logger.critical("Database numbers mismatch, the \"new\" version number is older than the current one. This could be because of a failed downgrade!")
                raise RuntimeError("Database numbers mismatch, the \"new\" version number is older than the current one. This could be because of a failed downgrade!")
            else:
                logger.info("No action required for database")
    except UndefinedTableError as e:
        logger.info("No version info in database found, initializing new database")
        initialize_db()

def get_new_version_number():
    version = ""
    last_line = ""
    with open('db.sql', 'r') as sql_file:
        last_line = sql_file.readlines()[-1]

    for char in last_line:
        if char.isdigit():
            version += char
    
    return int(version)

def initialize_db():
    pass

def upgrade_db(current_version, new_version):
    pass