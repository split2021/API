from django.contrib.auth import authenticate

import time
import json
import random
import string

import paypalrestsdk

from api.classviews import SingleObjectAPIView, MultipleObjectsAPIView, APIView
from api.models import User, Group, GroupMembership, Friendship
from api.responses import APIResponse, ExceptionCaught
from api.token import Token

# Create your views here.

class LoginView(APIView):
    """
     Receive email and password and try to authenticate the user then
     If successful, send back user information
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
     Ask Personal account for payment
    """

    authentification = False
    implemented_methods = ('POST',)

    def post(self, request, *args, **kwargs):
        """
        """

        data = request.body.decode('utf-8')
        json_data = json.loads(data)

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
                        "price": json_data['price'],
                        "currency": "EUR",
                        "quantity": 1
                    }
                ]},
                "amount": {
                    "total": json_data['price'],
                    "currency": "EUR"
                },
                "description": "Test payment from Split API"
            }]
        })
        if not payment.create():
            return APIResponse(500, "Failed to create payment")

        return APIResponse(200, "Sucessfully created payment", {'links': list((link.method, link.href) for link in payment.links)})


class PaymentExecute(APIView):
    """
     Execute redirected payment
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
            return APIResponse(500, "Failed to execute payment")


class PayoutView(APIView):
    """
     Send money from Business to Business or Personal account
     Business -> Business / Personnal
    """

    authentification = False
    implemented_methods = ('GET',)

    def post(self, request, *args, **kwargs):
        """
        """

        data = request.body.decode('utf-8')
        json_data = json.loads(data)

        payout = paypalrestsdk.Payout({
            "sender_batch_header": {
                "sender_batch_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                "email_subject": "You have a payment"
            },
            "items": [{
                "recipient_type": "EMAIL",
                "amount": {
                    "value": json_data["amount"],
                    "currency": "EUR"
                },
                "receiver": json_data["receiver"],
                "note": "Take my test money",
                "sender_item_id": "item_0"
            }]
        })

        if payout.create(sync_mode=False):
            return APIResponse(200, f"payout {payout.batch_header.payout_batch_id} created successfully")
        else:
            return APIResponse(500, payout.error)


class NotificationView(APIView):
    """
     Return the notification associated with the group if existing
    """

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
