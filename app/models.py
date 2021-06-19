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
        'created': user.created.isoformat(' ', 'seconds')
    }


class Organization:
    id: UUID
    name: str
    description: str
    active: bool
    created: datetime

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


def organization_to_json(organization: Organization) -> dict:
    return {
        'id': organization.id.__str__(),
        'name': organization.name,
        'description': organization.description,
        'active': organization.active.__str__().lower(),
        'created': organization.created.isoformat(' ', 'seconds')
    }


class Membership:
    id: UUID
    organization_id: UUID
    user_id: UUID
    created: datetime
    renewal: datetime


def membership_to_json(membership: Membership) -> dict:
    return {
        'id': membership.id.__str__(),
        'organization_id': membership.organization_id.__str__(),
        'user_id': membership.user_id.__str__(),
        'created': membership.created.isoformat(' ', 'seconds'),
        'renewal': membership.renewal.isoformat(' ', 'seconds')
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
    logout_url: str
    last_ip: str


class Country:
    id: UUID
    name: str
    created: datetime


class Area:
    id: int
    name: str
    created: datetime
    country_id: UUID
    path: str


class Municipality:
    id: UUID
    name: str
    created: datetime
    country_id: UUID
    area_id: UUID


def municipality_to_json(municipality: Municipality) -> dict:
    return {
        'id': municipality.id.__str__(),
        'name': municipality.name,
        'created': municipality.created.isoformat(' ', 'seconds'),
        'country_id': municipality.country_id.__str__(),
        'area_id': municipality.area_id.__str__()
    }


def ui_placeholders(button_label: str) -> dict:
    return {
        "password": "Lösenord",
        "traits.name.first": "Förnamn",
        "traits.name.last": "Efternamn",
        "traits.postal_address.street": "Gatuadress",
        "traits.postal_address.postal_code": "Postnummer",
        "traits.postal_address.city": "Stad",
        "traits.phone": "Telefonnummer",
        "traits.email": "E-post",
        "traits.municipality": "Kommun",
        "traits.country": "Land",
        "method": button_label
    }


def ui_positions() -> dict:
    return {
        "csrf_token": 0,
        "traits.name.first": 1,
        "traits.name.last": 2,
        "traits.email": 3,
        "traits.phone": 4,
        "password": 5,
        "traits.postal_address.street": 6,
        "traits.postal_address.postal_code": 7,
        "traits.postal_address.city": 8,
        "traits.municipality": 9,
        "traits.country": 10,
        "method": 11
    }
