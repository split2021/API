from django.contrib.auth import authenticate

import time
import json

import paypalrestsdk

from api.classviews import SingleObjectAPIView, MultipleObjectsAPIView, APIView
from api.models import User, Group, GroupMembership, Friendship
from api.responses import APIResponse, ExceptionCaught
from api.token import Token

# Create your views here.

class LoginView(APIView):
    """
    """

    authentification = False
    implemented_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        """
        """

        data = request.body.decode('utf-8')
        json_data = json.loads(data)

        user = authenticate(username=json_data['email'], password=json_data['password'])
        if user is not None:
            return APIResponse(200, "User logged in", {
                'token': str(Token({
                                'time': int(time.time()),
                                'uid': user.id
                            })),
                'user': user.json(request)
            })
        else:
            return APIResponse(401, "Wrong user credentials")


class PaymentView(APIView):
    """
    """

    authentification = False
    implemented_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        """
        """

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://localhost:8080/api/payment/execute",
                "cancel_url": "http://localhost:8080/api/payment/cancel"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "item",
                        "sku": "item",
                        "price": "5.00",
                        "currency": "USD",
                        "quantity": 1
                    }
                ]},
                "amount": {
                    "total": "5.00",
                    "currency": "EUR"
                },
                "description": "Test payment from Split API"
            }]
        })
        if not payment.create():
            return APIResponse(200, "Failed to create payment")

        return APIResponse(200, "Sucessfully created payment", {'links': list((link.method, link.href) for link in payment.links)})


class PaymentExecute(APIView):
    """
    """

    authentification = False
    implemented_methods = ('GET',)

    def get(self, request, *args, **kwargs):
        """
        """

        payment = paypalrestsdk.Payment.find(request.GET.get("paymentId"))

        if payment.execute({'payer_id': request.GET.get("PayerID")}):
            return APIResponse(200, "Sucessfully executed payment")
        else:
            return APIResponse(200, "Failed to execute payment")

class UserView(SingleObjectAPIView):
    model = User

class UsersView(MultipleObjectsAPIView):
    model = User


class GroupMembershipView(SingleObjectAPIView):
    model = GroupMembership


class FriendshipView(SingleObjectAPIView):
    model = Friendship

class FriendshipsView(MultipleObjectsAPIView):
    model = Friendship


class GroupView(SingleObjectAPIView):
    model = Group

class GroupsView(MultipleObjectsAPIView):
    model = Group
