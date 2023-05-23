import bleach
from bleach.css_sanitizer import CSSSanitizer

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
        sql = "INSERT INTO mp_posts (id, title, content, author, created, updated) VALUES ($1, $2, $3, $4, $5, $5);"

        post_id = uuid4()
        created = datetime.utcnow()

        attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES
        attributes['a'] = ['href', 'title', 'target', 'rel']
        attributes['*'] = ['style']
        attributes['img'] = ['src', 'alt', 'width', 'height']

        css_sanitizer = CSSSanitizer()

        try:
            sanitized_content = bleach.clean(
                content,
                tags={
                    'a',
                    'abbr',
                    'acronym',
                    'b',
                    'br',
                    'blockquote',
                    'code',
                    'div',
                    'em',
                    'h1',
                    'h2',
                    'h3',
                    'h4',
                    'h5',
                    'h6',
                    'hr',
                    'i',
                    'img',
                    'li',
                    'ol',
                    'p',
                    'pre',
                    'span',
                    'strong',
                    'ul'
                },
                attributes=attributes,
                css_sanitizer=css_sanitizer
            )

            if sanitized_content != content:
                logger.warning(
                    "Sanitized content is not equal to the original content, someone could have tried to sneak malicious HTML in\n" +
                    "Author: %s\n" +
                    "Post: %s, %s",
                    author.__str__(),
                    title,
                    post_id.__str__()
                )
                logger.debug("Sanitized: " + sanitized_content)
                logger.debug("Original: " + content)

            async with self.pool.acquire() as con:
                async with con.transaction():
                    await con.execute(sql, post_id, title, sanitized_content, author, created)
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
        sql = "SELECT id, title, content, author, created, updated FROM mp_posts ORDER BY created DESC;"

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
