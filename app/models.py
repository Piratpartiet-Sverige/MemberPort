from datetime import datetime
from uuid import UUID


class Name:
    first: str
    last: str


class PostalAddress:
    street: str
    postal_code: str
    city: str


class User:
    def __init__(self):
        self.name = Name()
        self.postal_address = PostalAddress()

    id: UUID
    number: int
    name: Name
    email: str
    phone: str
    postal_address: PostalAddress
    municipality: str
    country: str
    verified: bool

    created: datetime


class Organization:
    id: UUID
    name: str
    description: str
    active: bool
    created: datetime


def organization_to_json(organization: Organization) -> dict:
    return {
        'organization': {
            'id': organization.id.__str__(),
            'name': organization.name,
            'description': organization.description,
            'created': organization.created.isoformat(' ')
        }
    }


class Membership:
    user: User
    organization: Organization
    created: datetime
    renewal: datetime


class Role:
    id: UUID
    name: str
    description: str


class Permission:
    id: str
    name: str

    def __eq__(self, other):
        return self.id == other.id


class Session:
    id: UUID
    user: User
    hash: str
    issued_at: datetime
    expires_at: datetime
    last_ip: str


class Country:
    id: UUID
    name: str
    created: datetime


class Area:
    id: int
    name: str
    created: datetime
    country: Country
    path: str


class Municipality:
    id: UUID
    name: str
    created: datetime
    country: Country
    area_id: Area
