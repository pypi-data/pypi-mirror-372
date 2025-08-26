from functools import partial

import PIL

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from ichec_django_core.models import PortalMember


def generate_image():
    return PIL.Image.linear_gradient("L")


def setup_default_users_and_groups():
    PortalMember.objects.create(username="regular_user")
    PortalMember.objects.create(username="test_applicant")
    PortalMember.objects.create(username="access_call_board_member")
    PortalMember.objects.create(username="access_call_coordinator")
    PortalMember.objects.create(username="consortium_admin")

    Group.objects.create(name="consortium_admins")
    consortium_admins = Group.objects.get(name="consortium_admins")
    consortium_admin = PortalMember.objects.get(username="consortium_admin")
    consortium_admin.groups.add(consortium_admins)
    consortium_admin.save()


def add_group_permissions(group_name: str, model: type, permissions: list):

    group = Group.objects.get(name=group_name)
    content_type = ContentType.objects.get_for_model(model)
    for permission_name in permissions:
        permission = Permission.objects.get(
            codename=permission_name, content_type=content_type
        )
        group.permissions.add(permission)
    group.save()


class AuthAPITestCase(APITestCase):
    def authenticate(self, username: str):
        user = User.objects.get(username=username)
        self.client.force_authenticate(user=user)

    def deauthenticate(self):
        self.client.force_authenticate(user=None)

    def authenticated_op(self, username: str, op):
        self.authenticate(username)
        response = op()
        self.deauthenticate()
        return response

    def do_list(self):
        return self.client.get(self.url, format="json")

    def authenticated_list(self, username: str):
        return self.authenticated_op(username, self.do_list)

    def detail(self, resource_id: int):
        return self.client.get(self.url + f"{resource_id}/", format="json")

    def authenticated_detail(self, username: str, resource_id: int):
        return self.authenticated_op(username, partial(self.detail, resource_id))

    def create(self, data: dict, format="json"):
        return self.client.post(self.url, data, format=format)

    def update(self, data: dict, format="json"):
        return self.client.put(self.url, data, format=format)

    def put_file(self, resource_id: int, field: str, data, filename):
        return self.client.put(
            f"{self.url}{resource_id}/{field}/upload",
            data,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    def authenticated_create(self, username: str, data: dict, format="json"):
        return self.authenticated_op(username, partial(self.create, data, format))

    def authenticated_put_file(
        self, username: str, resource_id: int, field: str, data, filename: str
    ):
        return self.authenticated_op(
            username, partial(self.put_file, resource_id, field, data, filename)
        )

    def assert_200(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def assert_201(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def assert_204(self, response):
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def assert_401(self, response):
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assert_403(self, response):
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
