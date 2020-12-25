from app.models import Country, Organization, Municipality, organization_to_json, municipality_to_json
from datetime import datetime
from unittest import TestCase
from uuid import uuid4


class ModelsTest(TestCase):
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
