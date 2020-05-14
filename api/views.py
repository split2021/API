from django.contrib.auth import authenticate

import time
import json
import random
import string

import paypalrestsdk

from api.classviews import SingleObjectAPIView, MultipleObjectsAPIView, APIView
from api.models import User, Group, GroupMembership, Friendship, Payment
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

        currency = json_data.get('currency') or "EUR"

        group_id = json_data.get('group')
        if group_id is None or Group.objects.filter(id=group_id).count() == 0:
            return APIResponse(400, f"A payment cannot be created without a group")

        users_mail = json_data['users']
        if not users_mail:
            return APIResponse(400, f"A payment cannot be created without at least one user")
        if User.objects.filter(email__in=users_mail).count() != len(users_mail):
            return APIResponse(400, f"At least one user does not exist")

        payments_links = {}
        db_payment = Payment.objects.create(group_id=group_id, payments={}) # TODO: Create Django Issue because payments should be {} by default (according to models) but keeps its old value (concatenation)
        for mail, price in users_mail.items():
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": f"http://{request.get_host()}/api/payment/execute",
                    "cancel_url": f"http://{request.get_host()}/api/payment/cancel"},
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "item",
                            "sku": "item",
                            "price": price,
                            "currency": currency,
                            "quantity": 1
                        }
                    ]},
                    "amount": {
                        "total": price,
                        "currency": currency
                    },
                    "description": "Test payment from Split API"
                }]
            })
            if not payment.create():
                return APIResponse(500, f"Failed to create payment for user {user}")
            payments_links[mail] = list((link.method, link.href, price) for link in payment.links)
            db_payment.payments[payment.id] = False

        db_payment.save()
        return APIResponse(200, "Sucessfully created payments", payments_links)


class PaymentExecute(APIView):
    """
     Execute redirected payment
    """

    authentification = False
    implemented_methods = ('GET',)

    def get(self, request, *args, **kwargs):
        """
        """

        payment_id = request.GET.get("paymentId")
        payment = paypalrestsdk.Payment.find(payment_id)
        db_payment =  Payment.objects.get(payments__contains=[payment_id])
        db_payment.payments[payment_id] = True
        db_payment.save()

#        if payment successful do smth:

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
