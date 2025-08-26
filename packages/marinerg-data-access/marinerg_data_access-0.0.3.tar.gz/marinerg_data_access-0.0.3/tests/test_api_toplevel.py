from rest_framework import status
from rest_framework.test import APITestCase


from ichec_django_core.utils.test_utils import setup_default_users_and_groups


class TopLevelViewTests(APITestCase):
    def setUp(self):

        setup_default_users_and_groups()

    def test_get_org_not_authenticated(self):
        response = self.client.get("/api/", format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
