from datetime import datetime
from typing import Union
from uuid import uuid4, UUID

from app.logger import logger
from app.models import Post
from app.database.dao.base import BaseDao


class FeedDao(BaseDao):
    async def create_post(
        self,
        title: str,
        content: str,
        author: UUID,
        organizations: Union[list, None] = None,
        countries: Union[list, None] = None,
        areas: Union[list, None] = None,
        municipalities: Union[list, None] = None
    ) -> Union[Post, None]:
        sql = "INSERT INTO posts (id, title, content, author, created, updated) VALUES ($1, $2, $3, $4, $5, $5);"

        post_id = uuid4()
        created = datetime.utcnow()

        try:
            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(sql, post_id, title, content, author, created)
                    post = Post()
                    post.id = post_id
                    post.title = title
                    post.content = content
                    post.author = author
                    post.created = created
                    post.updated = created
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO CREATE POST", stack_info=True)
            return None

        return post

    async def get_posts(self) -> list:
        posts = list()
        sql = "SELECT id, title, content, author, created, updated FROM posts ORDER BY created DESC;"

        try:
            async with self.pool.acquire() as con:
                rows = await con.fetch(sql)
                for row in rows:
                    post = Post()
                    post.id = row["id"]
                    post.title = row["title"]
                    post.content = row["content"]
                    post.author = row["author"]
                    post.created = row["created"]
                    post.updated = row["updated"]
                    posts.append(post)
        except Exception as exc:
            logger.debug(exc.__str__())
            logger.error("SOMETHING WENT WRONG WHEN TRYING TO RETRIEVE POSTS", stack_info=True)

        return posts
