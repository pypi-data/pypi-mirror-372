from ichec_django_core.models import PortalMember

from ichec_django_core.utils.test_utils import (
    AuthAPITestCase,
    setup_default_users_and_groups,
)

from .test_utils import setup_access_call


class AccessCallViewTests(AuthAPITestCase):
    def setUp(self):
        self.url = "/api/access_calls/"
        setup_default_users_and_groups()
        setup_access_call()

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_regular_user(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_detail_regular_user(self):
        self.assert_200(self.authenticated_detail("regular_user", 1))

    def test_create_not_authenticated(self):
        data = {"title": "My Access Call"}
        self.assert_401(self.create(data))

    def test_create_regular_user(self):
        data = {"title": "My Access Call"}
        self.assert_403(self.authenticated_create("regular_user", data))

    def test_create_consortium_admin(self):
        consortium_admin = PortalMember.objects.get(username="consortium_admin")
        data = {
            "title": "My Access Call",
            "description": "Description of my access call",
            "coordinator": f"http://testserver/api/members/{consortium_admin.id}/",
            "board_chair": f"http://testserver/api/members/{consortium_admin.id}/",
            "board_members": [],
            "closing_date": "2024-11-11",
        }
        reponse = self.authenticated_create("consortium_admin", data)

        self.assert_201(reponse)
