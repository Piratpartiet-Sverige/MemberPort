from datetime import datetime
from typing import NamedTuple, Union
from uuid import UUID


class User:
    id: UUID
    name: str
    email: str
    created: datetime


def user_to_json(user: User) -> dict:
    return {
        'user': {
            'id': user.id.__str__(),
            'name': user.name,
            'email': user.email,
            'created': user.created.isoformat(' '),
        }
    }


class Session:
    id: UUID
    user: User
    hash: str
    created: datetime
    last_used: datetime
    last_ip: str


class PasswordCheckResult(NamedTuple):
    valid: bool
    user: Union[User, None]
