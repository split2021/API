from django.http.response import JsonResponse
from django.test import TestCase, Client
from django.http import HttpRequest

import json
import copy
from http import HTTPStatus

from . import getJsonFromResponse, emptyRequest

from api.views import PaymentGroupView
from api.models import User


class NoAuthPaymentGroupView(PaymentGroupView):
    enforce_authentification = False

class PaymentGroupViewTest(TestCase):
    def setUp(self):
        self.view = NoAuthPaymentGroupView()

        User.objects.create_user(email="test@email.fr",
                                password="testpassword",
                                phone="+33 1 15 35 95 75",
                                first_name="testfirstname",
                                last_name="testlastname",
                                username="testusername"
                                )

    def test_post_no_content(self):
        response = self.view.post(request=emptyRequest)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "A content is required to create payment group")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NO_CONTENT)

    def test_post(self):
        user = User.objects.get(email="test@email.fr")

        request = copy.deepcopy(emptyRequest)
        request.META['SERVER_NAME'] = "testserver"
        request.META['SERVER_PORT'] = 8080
        request.META['QUERY_STRING'] = f"/api/{PaymentGroupView.route}/"
        request._body = json.dumps({
            'name': "Test",
            'users': str(user.id)
        }).encode('utf-8')
        request.method = "post"

        response = self.view.dispatch(request=request)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "payment groups created successfully")
        self.assertEqual(content_json['statuscode'], HTTPStatus.CREATED)

        self.assertEqual(content_json['data'].get('name'), "Test")
        self.assertTrue(content_json['data'].get('users', None) != None)
