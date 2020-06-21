from datetime import datetime
from typing import NamedTuple, Union
from uuid import UUID

class Name:
    first: str
    last: str


class User:
    def __init__(self):
        self.name = Name()
    
    id: UUID
    name: Name
    email: str
    phone: str
    city: str
    street: str
    postal_code: str
    country: str
    verified: bool
    
    created: datetime


def user_to_json(user: User) -> dict:
    return {
        'user': {
            'id': user.id.__str__(),
            'name': user.name.first,
            'email': user.email,
            'created': user.created.isoformat(' '),
        }
    }


class Member:
    user: User
    number: int
    given_name: str
    last_name: str
    birth: datetime
    postal_code: str
    city: str
    address: str
    country: str


def member_to_json(member: Member) -> dict:
    return {
        'member': {
            'user': user_to_json(member.user),
            'number': member.number,
            'given_name': member.given_name,
            'last_name': member.last_name,
            'birth': member.birth.isoformat(' '),
            'postal_code': member.postal_code,
            'city': member.city,
            'address': member.address,
            'country': member.country
        }
    }


class Organization:
    id: UUID
    name: str
    description: str
    created: datetime


class Session:
    id: UUID
    user: User
    hash: str
    issued_at: datetime
    expires_at: datetime
    last_ip: str


class PasswordCheckResult(NamedTuple):
    valid: bool
    user: Union[User, None]
