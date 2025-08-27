import tempfile

from ichec_django_core.utils.test_utils import (
    AuthAPITestCase,
    setup_default_users_and_groups,
)

from .test_utils import setup_access_call, setup_application


class AccessApplicationViewTests(AuthAPITestCase):
    def setUp(self):
        self.url = "/api/access_applications/"
        setup_default_users_and_groups()
        call = setup_access_call()
        setup_application(call, "test_applicant")

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_detail_regular_user(self):
        self.assert_403(self.authenticated_detail("regular_user", 1))

    def test_detail_test_applicant(self):
        self.assert_200(self.authenticated_detail("test_applicant", 1))

    def test_detail_consortium_admin(self):
        self.assert_200(self.authenticated_detail("consortium_admin", 1))

    def test_create_not_authenticated(self):
        data = {"title": "My Access Application"}
        self.assert_401(self.create(data))

    def test_create_regular_user(self):
        data = {
            "call": "http://testserver/api/access_calls/1/",
            "trl_stage": 1,
            "facilities": [],
        }
        self.assert_201(self.authenticated_create("regular_user", data))

    def test_create_with_file_regular_user(self):

        tmp_file = tempfile.NamedTemporaryFile(suffix=".txt")
        tmp_file.write(b"Hello world")
        tmp_file.seek(0)

        data = {
            "call": "http://testserver/api/access_calls/1/",
            "trl_stage": 1,
            "facilities": [],
        }
        self.assert_201(self.authenticated_create("regular_user", data, "multipart"))
