from app.models import Country, Organization, Municipality, organization_to_json, municipality_to_json, user_to_json
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
        self.assertEqual(user.created.isoformat(' '), json["created"])

    def test_organization_model(self):
        id = uuid4()
        created = datetime.utcnow()

        org = Organization()
        org.id = id
        org.name = "Piratpartiet"
        org.description = "Omtänksamhet istället för misstänksamhet"
        org.active = True
        org.created = created

        json = organization_to_json(org)
        self.assertEqual(id.__str__(), json["id"])
        self.assertEqual(org.name, json["name"])
        self.assertEqual(org.description, json["description"])
        self.assertEqual("true", json["active"])
        self.assertEqual(created.isoformat(' '), json["created"])

    def test_municipality_model(self):
        id = uuid4()
        created = datetime.utcnow()
        area_id = uuid4()
        sweden = Country()
        sweden.name = "Sverige"

        mun = Municipality()
        mun.id = id
        mun.name = "Lund"
        mun.created = created
        mun.country = sweden
        mun.area_id = area_id

        json = municipality_to_json(mun)
        self.assertEqual(id.__str__(), json["id"])
        self.assertEqual(mun.name, json["name"])
        self.assertEqual(created.isoformat(' '), json["created"])
        self.assertEqual(mun.country.name, json["country"])
        self.assertEqual(area_id.__str__(), json["area_id"])
