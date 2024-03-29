from datetime import datetime
from uuid import UUID
from typing import Union


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


class Bot:
    id: UUID
    name: str
    email: str

    verified: bool
    created: datetime


def bot_to_json(bot: Bot) -> dict:
    return {
        'id': bot.id.__str__(),
        'name': bot.name,
        'email': bot.email,
        'verified': bot.verified.__str__().lower(),
        'created': bot.created.isoformat(' ', 'seconds')
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
    show_on_signup: bool
    path: str

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
        'created': organization.created.isoformat(' ', 'seconds'),
        'show_on_signup': organization.show_on_signup.__str__().lower(),
        'path': organization.path
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

    user_id: UUID  # This is the ID of the user/bot model
    verified: bool  # This is the verified state of the user/bot model
    created: datetime  # This is the created time of the user/bot model

    user: Union[User, None]
    bot: Union[Bot, None]

    hash: str
    issued_at: datetime
    expires_at: datetime
    logout_url: str
    last_ip: str


class Country:
    id: UUID
    name: str
    created: datetime


def country_to_json(country: Country) -> dict:
    return {
        'id': country.id.__str__(),
        'name': country.name.__str__(),
        'created': country.created.isoformat(' ', 'seconds')
    }


class Area:
    id: int
    name: str
    created: datetime
    country_id: UUID
    path: str


def area_to_json(area: Area) -> dict:
    return {
        'id': area.id.__str__(),
        'name': area.name.__str__(),
        'created': area.created.isoformat(' ', 'seconds'),
        'country_id': area.country_id.__str__(),
        'path': area.path
    }


class Municipality:
    id: UUID
    name: str
    created: datetime
    country_id: UUID
    area_id: int


def municipality_to_json(municipality: Municipality) -> dict:
    return {
        'id': municipality.id.__str__(),
        'name': municipality.name,
        'created': municipality.created.isoformat(' ', 'seconds'),
        'country_id': municipality.country_id.__str__(),
        'area_id': municipality.area_id.__str__()
    }


class Post:
    id: UUID
    title: str
    content: str
    author: UUID
    created: datetime
    updated: datetime


def post_to_json(post: Post) -> dict:
    return {
        'id': post.id.__str__(),
        'title': post.title,
        'content': post.content,
        'author': post.author.__str__(),
        'created': post.created.isoformat(' ', 'seconds'),
        'updated': post.updated.isoformat(' ', 'seconds'),
    }


class Event:
    id: Union[UUID, None]
    title: str
    description: str
    host: Union[UUID, None]
    start: datetime
    end: datetime
    created: datetime
    all_day: False
    url: str


def event_to_json(event: Event) -> dict:
    return {
        'id': event.id.__str__() if event.id is not None else '',
        'title': event.title,
        'description': event.description,
        'host': event.host.__str__() if event.host is not None else '',
        'start': event.start.isoformat(' ', 'seconds'),
        'end': event.end.isoformat(' ', 'seconds'),
        'created': event.created.isoformat(' ', 'seconds'),
        'allDay': event.all_day.__str__().lower(),
        'url': event.url
    }


class Calendar:
    id: UUID
    description: str
    ics_url: Union[UUID, None]
    created: datetime


def calendar_to_json(calendar: Calendar) -> dict:
    return {
        'id': calendar.id.__str__(),
        'description': calendar.description,
        'ics_url': calendar.ics_url,
        'created': calendar.created.isoformat(' ', 'seconds')
    }


def ui_placeholders(button_label: str) -> dict:
    return {
        "password": "Lösenord",
        "traits.name": "Namn",
        "traits.name.first": "Förnamn",
        "traits.name.last": "Efternamn",
        "traits.postal_address.street": "Gatuadress",
        "traits.postal_address.postal_code": "Postnummer",
        "traits.postal_address.city": "Postort",
        "traits.phone": "Telefonnummer",
        "traits.email": "E-post",
        "email": "E-post",
        "traits.municipality": "Kommun",
        "traits.country": "Land",
        "traits.gender": "Självupplevt kön",
        "traits.birthday": "Födelsedag",
        "code": "Kod",
        "method": button_label
    }


def ui_positions() -> dict:
    return {
        "csrf_token": 0,
        "traits.name": 1,
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
        "traits.birthday": 11,
        "traits.gender": 12,
        "code": 13,
        "method": 14
    }
