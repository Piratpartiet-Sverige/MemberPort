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


class Organization:
    id: UUID
    name: str
    description: str
    created: datetime


class Membership:
    user: User
    organization: Organization
    created: datetime
    renewal: datetime


class Session:
    id: UUID
    user: User
    hash: str
    issued_at: datetime
    expires_at: datetime
    last_ip: str