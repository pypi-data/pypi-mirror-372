from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from ichec_django_core.models import Organization

from ichec_django_core.utils.test_utils import (
    setup_default_users_and_groups,
    add_group_permissions,
)


class OgranizationViewTests(APITestCase):
    def setUp(self):

        setup_default_users_and_groups()

        add_group_permissions(
            "consortium_admins",
            Organization,
            ["change_organization", "add_organization"],
        )

    def test_get_org_not_authenticated(self):
        response = self.client.get("/api/organizations/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_org_authenticated(self):
        user = User.objects.get(username="regular_user")

        self.client.force_authenticate(user=user)
        response = self.client.get("/api/organizations/", format="json")
        self.client.force_authenticate(user=None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_org_not_authenticated(self):
        data = {"name": "My Org"}
        response = self.client.post("/api/organizations/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_org_authenticated_no_permission(self):
        user = User.objects.get(username="regular_user")

        self.client.force_authenticate(user=user)
        data = {"name": "My Org"}
        response = self.client.post("/api/organizations/", data, format="json")
        self.client.force_authenticate(user=None)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def xtest_create_org_authenticated_with_permission(self):
        """
        Ensure we can create a new organisation object.
        """

        user = User.objects.get(username="consortium_admin")
        self.client.force_authenticate(user=user)

        data = {
            "name": "My Org",
            "acronym": "MO",
            "description": "An description of the org",
            "address": "The address",
            "website": "www.org.org",
            "country": "",
        }
        response = self.client.post("/api/organizations/", data, format="json")
        self.client.force_authenticate(user=None)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Organization.objects.count(), 1)
        self.assertEqual(Organization.objects.get().name, "My Org")
