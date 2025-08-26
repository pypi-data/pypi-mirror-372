from ichec_django_core.utils.test_utils import (
    AuthAPITestCase,
    setup_default_users_and_groups,
)


class PortalMemberViewTests(AuthAPITestCase):
    def setUp(self):
        self.url = "/api/members/"
        setup_default_users_and_groups()

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_detail_authenticated(self):
        self.assert_200(self.authenticated_detail("regular_user", 1))

    def test_create_not_authenticated(self):
        data = {"username": "test_user"}
        self.assert_401(self.create(data))

    def test_create_authenticated_no_permission(self):
        data = {"username": "test_user"}
        self.assert_403(self.authenticated_create("regular_user", data))
