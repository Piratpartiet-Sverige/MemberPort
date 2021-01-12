from datetime import datetime
from uuid import UUID


class Name:
    first: str
    last: str


def name_to_json(name: Name):
    return {
        'first': name.first,
        'last': name.last
    }


class PostalAddress:
    street: str
    postal_code: str
    city: str


def postal_address_to_json(postal_address: PostalAddress):
    return {
        'street': postal_address.street,
        'postal_code': postal_address.postal_code,
        'city': postal_address.city
    }


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


def user_to_json(user: User) -> dict:
    return {
        'id': user.id.__str__(),
        'number': user.number.__str__(),
        'name': name_to_json(user.name),
        'email': user.email,
        'phone': user.phone,
        'postal_address': postal_address_to_json(user.postal_address),
        'municipality': user.municipality,
        'country': user.country,
        'verified': user.verified.__str__().lower(),
        'created': user.created.isoformat(' ')
    }


class Organization:
    id: UUID
    name: str
    description: str
    active: bool
    created: datetime


def organization_to_json(organization: Organization) -> dict:
    return {
        'id': organization.id.__str__(),
        'name': organization.name,
        'description': organization.description,
        'active': organization.active.__str__().lower(),
        'created': organization.created.isoformat(' ')
    }


class Membership:
    user: User
    organization: Organization
    created: datetime
    renewal: datetime


def membership_to_json(membership: Membership) -> dict:
    return {
        'organization': organization_to_json(membership.organization),
        'user': user_to_json(membership.user),
        'created': membership.created.isoformat(' '),
        'renewal': membership.renewal.isoformat(' ')
    }


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
    area_id: UUID


def municipality_to_json(municipality: Municipality) -> dict:
    return {
        'id': municipality.id.__str__(),
        'name': municipality.name,
        'created': municipality.created.isoformat(' '),
        'country': municipality.country.name,
        'area_id': municipality.area_id.__str__()
    }
