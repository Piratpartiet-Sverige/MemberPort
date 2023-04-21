from app.models import (
    Membership,
    Organization,
    Municipality,
    Country,
    Area,
    Post,
    Calendar,
    organization_to_json,
    membership_to_json,
    municipality_to_json,
    user_to_json,
    country_to_json,
    area_to_json,
    post_to_json,
    calendar_to_json
)
from app.test.web_testcase import get_mock_session
from datetime import datetime
from unittest import TestCase
from uuid import uuid4


class ModelsTest(TestCase):
    def test_user_model(self):
        user = get_mock_session().user
        json = user_to_json(user)

        self.assertEqual(user.id.__str__(), json["id"])
        self.assertEqual(user.number, int(json["number"]))
        self.assertEqual(user.name.first, json["name"]["first"])
        self.assertEqual(user.name.last, json["name"]["last"])
        self.assertEqual(user.email, json["email"])
        self.assertEqual(user.phone, json["phone"])
        self.assertEqual(user.postal_address.street, json["postal_address"]["street"])
        self.assertEqual(user.postal_address.postal_code, json["postal_address"]["postal_code"])
        self.assertEqual(user.postal_address.city, json["postal_address"]["city"])
        self.assertEqual(user.municipality, json["municipality"])
        self.assertEqual(user.country, json["country"])
        self.assertEqual("true", json["verified"])
        self.assertEqual(user.created.isoformat(' ', 'seconds'), json["created"])

    def test_organization_model(self):
        id = uuid4()
        created = datetime.utcnow()

        org = Organization()
        org.id = id
        org.name = "Piratpartiet"
        org.description = "Omtänksamhet istället för misstänksamhet"
        org.active = True
        org.created = created
        org.show_on_signup = False
        org.path = id.__str__()

        json = organization_to_json(org)
        self.assertEqual(id.__str__(), json["id"])
        self.assertEqual(org.name, json["name"])
        self.assertEqual(org.description, json["description"])
        self.assertEqual("true", json["active"])
        self.assertEqual(created.isoformat(' ', 'seconds'), json["created"])
        self.assertEqual("false", json["show_on_signup"])
        self.assertEqual(id.__str__(), json["path"])

    def test_membership_model(self):
        id = uuid4()
        org_id = uuid4()
        created = datetime.utcnow()
        renewal = datetime(created.year + 1, created.month, created.day)
        user = get_mock_session().user

        membership = Membership()
        membership.id = id
        membership.organization_id = org_id
        membership.user_id = user.id
        membership.created = created
        membership.renewal = renewal

        json = membership_to_json(membership)
        self.assertEqual(id.__str__(), json["id"])
        self.assertEqual(org_id.__str__(), json["organization_id"])
        self.assertEqual(user.id.__str__(), json["user_id"])
        self.assertEqual(created.isoformat(' ', 'seconds'), json["created"])
        self.assertEqual(renewal.isoformat(' ', 'seconds'), json["renewal"])

    def test_municipality_model(self):
        id = uuid4()
        created = datetime.utcnow()
        area_id = uuid4()
        sweden_id = uuid4()

        mun = Municipality()
        mun.id = id
        mun.name = "Lund"
        mun.created = created
        mun.country_id = sweden_id
        mun.area_id = area_id

        json = municipality_to_json(mun)
        self.assertEqual(id.__str__(), json["id"])
        self.assertEqual(mun.name, json["name"])
        self.assertEqual(created.isoformat(' ', 'seconds'), json["created"])
        self.assertEqual(mun.country_id.__str__(), json["country_id"])
        self.assertEqual(area_id.__str__(), json["area_id"])

    def test_country_model(self):
        id = uuid4()
        created = datetime.utcnow()

        country = Country()
        country.id = id
        country.name = "Sverige"
        country.created = created

        json = country_to_json(country)
        self.assertEqual(id.__str__(), json["id"])
        self.assertEqual(country.name, json["name"])
        self.assertEqual(created.isoformat(' ', 'seconds'), json["created"])

    def test_area_model(self):
        id = 1
        created = datetime.utcnow()
        sweden_id = uuid4()

        area = Area()
        area.id = id
        area.name = "Norra distriktet"
        area.created = created
        area.country_id = sweden_id
        area.path = "1"

        json = area_to_json(area)
        self.assertEqual(area.id.__str__(), json["id"])
        self.assertEqual(area.name, json["name"])
        self.assertEqual(created.isoformat(' ', 'seconds'), json["created"])
        self.assertEqual(area.country_id.__str__(), json["country_id"])
        self.assertEqual(area.path, json["path"])

    def test_post_model(self):
        created = datetime.utcnow()
        id = uuid4()
        author = uuid4()
        updated = datetime.utcnow()

        post = Post()
        post.id = id
        post.title = "Rubrik"
        post.content = "<p>Innehåll här</p>"
        post.author = author
        post.created = created
        post.updated = updated

        json = post_to_json(post)
        self.assertEqual(post.id.__str__(), json["id"])
        self.assertEqual(post.title, json["title"])
        self.assertEqual(post.content, json["content"])
        self.assertEqual(post.author.__str__(), json["author"])
        self.assertEqual(post.created.isoformat(' ', 'seconds'), json["created"])
        self.assertEqual(post.updated.isoformat(' ', 'seconds'), json["updated"])

    def test_calendar_model(self):
        created = datetime.utcnow()
        id = uuid4()

        calendar = Calendar()
        calendar.id = id
        calendar.description = "Kalender"
        calendar.ics_url = "https://www.example.com"
        calendar.created = created

        json = calendar_to_json(calendar)
        self.assertEqual(calendar.id.__str__(), json["id"])
        self.assertEqual(calendar.description, json["description"])
        self.assertEqual(calendar.ics_url, json["ics_url"])
        self.assertEqual(calendar.created.isoformat(' ', 'seconds'), json["created"])
