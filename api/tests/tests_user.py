from django.test import TestCase
from django.http import HttpRequest, request

from api.models import User
from api.views import UserView

import json
from http import HTTPStatus

from . import getJsonFromResponse, emptyRequest

# Create your tests here.

class NoAuthUserView(UserView):
    enforce_authentification = False

class UserTestCase(TestCase):
    def setUp(self):
        self.userView = NoAuthUserView()

        User.objects.create_user(email="test@email.fr",
                                password="testpassword",
                                phone="+33 1 15 35 95 75",
                                first_name="testfirstname",
                                last_name="testlastname",
                                username="testusername"
                                )

    def test_get_existing_user(self):
        user = User.objects.get(email="test@email.fr")

        emptyRequest.method = "get"
        response = self.userView.dispatch(request=emptyRequest, id=user.id)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Retrieved user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.OK)

        self.assertEqual(content_json['data']['email'], user.email)
        self.assertEqual(content_json['data']['phone'], user.phone)
        self.assertEqual(content_json['data']['first_name'], user.first_name)
        self.assertEqual(content_json['data']['last_name'], user.last_name)
        self.assertEqual(content_json['data']['username'],  user.username)

    def test_get_nonexisting_user(self):
        emptyRequest.method = "get"
        response = self.userView.dispatch(request=emptyRequest, id=42)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "No user with id 42")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NOT_FOUND)


    def test_patch_existing_user_with_content(self):
        user = User.objects.get(email="test@email.fr")

        import copy
        request = copy.deepcopy(emptyRequest)
        request._body = json.dumps({
            'email': "testpatch@email.fr",
            'phone': "+33 2 15 35 95 75",
            'first_name': "patchfirstname",
            'last_name': "patchlastname",
            'username': "patchusername"
        }).encode()
        request.META['CONTENT_LENGTH'] = 42
        request.method = "patch"
        response = self.userView.dispatch(request=request, id=user.id)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Updated user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.OK)

        user = User.objects.get(id=user.id)
        self.assertEqual(user.email, "testpatch@email.fr")
        self.assertEqual(user.phone, "+33 2 15 35 95 75")
        self.assertEqual(user.first_name, "patchfirstname")
        self.assertEqual(user.last_name,  "patchlastname")
        self.assertEqual(user.username,  "patchusername")

    def test_patch_existing_user_without_content(self):
        user = User.objects.get(email="test@email.fr")

        emptyRequest.method = "patch"
        response = self.userView.dispatch(request=emptyRequest, id=user.id)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "A content is required to update user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NO_CONTENT)

    def test_patch_non_existing_user_with_content(self):
        import copy
        request = copy.deepcopy(emptyRequest)
        request._body = json.dumps({
            'email': "testpatch@email.fr",
            'phone': "+33 2 15 35 95 75",
            'first_name': "patchfirstname",
            'last_name': "patchlastname",
            'username': "patchusername"
        }).encode()
        request.META['CONTENT_LENGTH'] = 42
        request.method = "patch"
        response = self.userView.dispatch(request=request, id=42)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "No user with id 42")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NOT_FOUND)


    def test_post_user_with_content(self):
        import copy
        request = copy.deepcopy(emptyRequest)
        request._body = json.dumps({
            'email': "test2@email.fr",
            'password': "test2password",
            'phone': "+33 2 15 35 95 75",
            'first_name': "test2firstname",
            'last_name': "test2lastname",
            'username': "test2username",
        }).encode()
        request.META['CONTENT_LENGTH'] = 42
        request.method = "post"
        response = self.userView.dispatch(request=request)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Created user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.CREATED)

    def test_post_user_without_content(self):
        emptyRequest.method = "post"
        response = self.userView.dispatch(request=emptyRequest)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "A content is required to create user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NO_CONTENT)


    def test_put_existing_user_with_content(self):
        user = User.objects.get(email="test@email.fr")

        import copy
        request = copy.deepcopy(emptyRequest)
        request._body = json.dumps({
            'email': "testput@email.fr",
            'phone': "+33 3 15 35 95 75",
            'first_name': "putfirstname",
            'last_name': "putlastname",
            'username': "putusername"
        }).encode()
        request.META['CONTENT_LENGTH'] = 42
        request.method = "put"
        response = self.userView.dispatch(request=request, id=user.id)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "13 already taken")
        self.assertEqual(content_json['statuscode'], HTTPStatus.CONFLICT)

        updateUser = User.objects.get(id=user.id)
        self.assertTrue(updateUser == user)

    def test_put_nonexisting_user_with_content(self):
        import copy
        request = copy.deepcopy(emptyRequest)
        request._body = json.dumps({
            'email': "testput@email.fr",
            'phone': "+33 3 15 35 95 75",
            'first_name': "putfirstname",
            'last_name': "putlastname",
            'username': "putusername",
            'password': "putpassword"
        }).encode()
        request.META['CONTENT_LENGTH'] = 42
        request.method = "put"
        response = self.userView.dispatch(request=request, id=42)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Created user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.CREATED)

        user = User.objects.get(id=42)
        self.assertEqual(user.email, "testput@email.fr")
        self.assertEqual(user.phone, "+33 3 15 35 95 75")
        self.assertEqual(user.first_name, "putfirstname")
        self.assertEqual(user.last_name,  "putlastname")
        self.assertEqual(user.username,  "putusername")

    def test_put_existing_user_without_content(self):
        user = User.objects.get(email="test@email.fr")

        emptyRequest.method = "put"
        response = self.userView.dispatch(request=emptyRequest, id=user.id)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "14 already taken")
        self.assertEqual(content_json['statuscode'], HTTPStatus.CONFLICT)

    def test_put_nonexisting_user_without_content(self):
        emptyRequest.method = "put"
        response = self.userView.dispatch(request=emptyRequest, id=42)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "A content is required to emplace user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NO_CONTENT)


    def test_delete_existing_user(self):
        user = User.objects.get(email="test@email.fr")

        emptyRequest.method = "delete"
        response = self.userView.dispatch(request=emptyRequest, id=user.id)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Deleted user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.OK)

    def test_delete_nonexisting_user(self):
        emptyRequest.method = "delete"
        response = self.userView.dispatch(request=emptyRequest, id=42)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "No user with id 42")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NOT_FOUND)


class UsersTestCase(TestCase):
    def setUp(self):
        self.usersView = NoAuthUserView()

        emptyRequest = HttpRequest()
        emptyRequest.META['CONTENT_LENGTH'] = 0
        emptyRequest.META['SERVER_NAME'] = "127.0.0.1"
        emptyRequest.META['SERVER_PORT'] = 8080
        emptyRequest._body = b""

        User.objects.create_user(email="test@email.fr",
                                password="testpassword",
                                phone="+33 1 15 35 95 75",
                                first_name="testfirstname",
                                last_name="testlastname",
                                username="testusername"
                                )

    def test_get_users(self):
        emptyRequest.method = "get"
        response = self.usersView.dispatch(request=emptyRequest)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Retrieved users")
        self.assertEqual(content_json['statuscode'], HTTPStatus.OK)

        self.assertEqual(type(content_json['data']), list)

    def test_patch_users(self):
        emptyRequest.method = "patch"
        response = self.usersView.dispatch(request=emptyRequest)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Verb not allowed")
        self.assertEqual(content_json['statuscode'], HTTPStatus.METHOD_NOT_ALLOWED)

    def test_post_users_with_content(self):
        from copy import deepcopy
        request = deepcopy(emptyRequest)
        request._body = json.dumps({
            'email': "test2@email.fr",
            'password': "test2password",
            'phone': "+33 2 15 35 95 75",
            'first_name': "test2firstname",
            'last_name': "test2lastname",
            'username': "test2username",
        }).encode()
        request.META['CONTENT_LENGTH'] = 42
        request.method = "post"
        response = self.usersView.dispatch(request=request)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Created user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.CREATED)

    def test_post_users_without_content(self):
        emptyRequest.method = "post"
        response = self.usersView.dispatch(request=emptyRequest)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "A content is required to create user")
        self.assertEqual(content_json['statuscode'], HTTPStatus.NO_CONTENT)

    def test_put_users(self):
        emptyRequest.method = "put"
        response = self.usersView.dispatch(request=emptyRequest)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "You are trying to emplace on a collection. Instead use POST to create or use an id")
        self.assertEqual(content_json['statuscode'], HTTPStatus.METHOD_NOT_ALLOWED)

    def test_delete_users(self):
        emptyRequest.method = "delete"
        response = self.usersView.dispatch(request=emptyRequest)
        content_json = getJsonFromResponse(response)

        self.assertEqual(content_json['reason'], "Verb not allowed")
        self.assertEqual(content_json['statuscode'], HTTPStatus.METHOD_NOT_ALLOWED)
