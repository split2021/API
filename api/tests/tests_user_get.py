from django.test import TestCase

from api.models import User
from api.views import UserView, UsersView

from . import getJsonFromResponse, emptyRequest, baseKwargs

# Create your tests here.

class UserTestCase(TestCase):
    def setUp(self):
        self.userView = UserView()

        self.kwargs = {
            'request': emptyRequest,
            'return_': 1,
            'limit': 1,
        }

        self.user = User.objects.create_user(email="test@email.fr",
                                            password="testpassword",
                                            phone="+33 1 15 35 95 75",
                                            first_name="testfirstname",
                                            last_name="testlastname",
                                            username="testusername"
                                            )

    def test_get_existing_user(self):
        response = self.userView.get(**baseKwargs, id=self.user.id)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['statuscode'], 200)
        self.assertEqual(content_json['reason'], "user retrieved successfully")

        self.assertEqual(content_json['data']['email'], self.user.email)
        self.assertEqual(content_json['data']['phone'], self.user.phone)
        self.assertEqual(content_json['data']['first_name'], self.user.first_name)
        self.assertEqual(content_json['data']['last_name'], self.user.last_name)
        self.assertEqual(content_json['data']['username'], self.user.username)

    def test_get_nonexisting_user(self):
        response = self.userView.get(baseKwargs, id=42)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['statuscode'], 404)
        self.assertEqual(content_json['reason'], "user not found")
