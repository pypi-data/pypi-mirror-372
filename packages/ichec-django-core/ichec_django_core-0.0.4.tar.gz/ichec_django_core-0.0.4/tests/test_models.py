from django.test import TestCase

from ichec_django_core.models import Organization


class OrganizationTestCase(TestCase):
    def setUp(self):
        Organization.objects.create(name="my_org")

    def test_query_model(self):
        org = Organization.objects.get(name="my_org")
        self.assertEqual(org.name, "my_org")
