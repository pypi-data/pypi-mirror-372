import tempfile
import json

from marinerg_facility.models import TestFacility

from ichec_django_core.utils.test_utils import (
    AuthAPITestCase,
    setup_default_users_and_groups,
    add_group_permissions,
    generate_image,
)


class TestFacilityViewTests(AuthAPITestCase):
    def setUp(self):
        self.url = "/api/facilities/"
        setup_default_users_and_groups()

        add_group_permissions(
            "consortium_admins",
            TestFacility,
            ["change_testfacility", "add_testfacility"],
        )

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_create_not_authenticated(self):
        data = {"name": "My Facility"}
        self.assert_401(self.create(data))

    def test_create_authenticated_no_permission(self):
        data = {"name": "My Facility"}
        self.assert_403(self.authenticated_create("regular_user", data))

    def test_create_authenticated_permission(self):
        data = {
            "name": "My Facility",
            "address": "123 street",
            "country": "IE",
            "members": [],
        }
        self.assert_201(self.authenticated_create("consortium_admin", data))

    def test_create_with_image_authenticated_permission(self):
        image = generate_image()
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png")
        image.save(tmp_file, format="PNG")

        tmp_file.seek(0)

        data = {
            "name": "My Facility",
            "address": "123 street",
            "country": "IE",
            "members": [],
        }

        response = self.authenticated_create("consortium_admin", data)
        self.assert_201(response)

        resource_id = json.loads(response.content)["id"]
        self.assert_204(
            self.authenticated_put_file(
                "consortium_admin",
                resource_id,
                "image",
                {"file": tmp_file},
                "test_image.png",
            )
        )
