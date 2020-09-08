from asyncpg.pool import Pool

class BaseDao:
    def __init__(self, pool: Pool):
        self.pool = pool