from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.urls import get_resolver
from django.http import HttpRequest
from django.shortcuts import redirect

import time
import json
import random
import string
from http import HTTPStatus

import paypalrestsdk

from api.classviews import SingleObjectAPIView, MultipleObjectsAPIView, APIView
from api.models import User, PaymentGroup, PaymentGroupMembership, Friendship, Payment
from api.responses import APIResponse, ExceptionCaught
from api.token import Token

# Create your views here.

class EndpointsList(APIView):
    """
     Return a json with the list of available endpoints
    """

    authentification = False
    implemented_methods = ('GET',)

    def get(self, request:HttpRequest) -> APIResponse:
        return APIResponse(HTTPStatus.OK, "URLs available", sorted(set(view[1] for view in get_resolver(None).reverse_dict.values())))

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
        if group_id is None or PaymentGroup.objects.filter(id=group_id).count() == 0:
            return APIResponse(400, f"A payment cannot be created without a group")

        total = round(json_data['total'], 2)
        users_mail = json_data['users']
        if not users_mail:
            return APIResponse(400, f"A payment cannot be created without at least one user")
        if User.objects.filter(email__in=users_mail).count() != len(users_mail):
            return APIResponse(400, f"At least one user does not exist")

        user_sum = round(sum(users_mail.values()), 2)
        if user_sum != total:
            return APIResponse(400, f"Total ({total}) does not match users sum ({user_sum})")
        target = json_data['target']

        payments_links = {}
        db_payment = Payment.objects.create(group_id=group_id, currency=currency, total=total, target=target) # TODO: Create Django Issue because payments should be {} by default (according to models) but keeps its old value (concatenation)
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
                return APIResponse(500, f"Failed to create payment for user {mail}")
            payments_links[mail] = list((link.method, link.href, price) for link in payment.links)
            db_payment.payments[payment.id] = {'status': Payment.STATUS.PROCESSING, 'amount': price}

        db_payment.save()
        payments_links['id'] = db_payment.id
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
        try:
            db_payment =  Payment.objects.get(payments__contains={payment_id: {'status': Payment.STATUS.PROCESSING}})
        except ObjectDoesNotExist:
            return APIResponse(404, "Payment does not exist or is not valid")
        db_payment.payments[payment_id]['status'] = Payment.STATUS.COMPLETED
        db_payment.save()

        if payment.execute({'payer_id': request.GET.get("PayerID")}):
            db_payment.payments[payment_id]['sale_id'] = payment.__data__['transactions'][0]['related_resources'][0]['sale']['id']
            db_payment.save()
            if db_payment.is_complete():
                payout = paypalrestsdk.Payout({
                    "sender_batch_header": {
                        "sender_batch_id": ''.join(random.choice(string.ascii_uppercase) for i in range(12)),
                        "email_subject": "You have a payment"
                    },
                    "items": [{
                        "recipient_type": "EMAIL",
                        "amount": {
                            "value": db_payment.calculate_payout_price(),
                            "currency": db_payment.currency
                        },
                        "receiver": db_payment.target,
                        "note": "Take my test money",
                        "sender_item_id": "item_0"
                    }]
                })
                if payout.create(sync_mode=False):
                    return APIResponse(200, "Sucessfully completed payment")
                else:
                    return APIResponse(500, payout.error)
            else:
                return APIResponse(200, "Successfully executed payment")
        else:
            return APIResponse(500, "Failed to execute payment")


class PaymentCanceled(APIView):
    """
    """

    authentification = False
    implemented_methods = ('GET',)

    def get(self, request, *args, **kwargs):
        """
        """

        payment_id = request.GET.get("paymentId")
        payment = paypalrestsdk.Payment.find(payment_id)
        db_payment =  Payment.objects.get(payments__contains=[payment_id])
        if db_payment.payments[payment_id] == Payment.STATUS.COMPLETED:
            return APIResponse(403, "Your payment is already completed")
        db_payment.payments[payment_id] = Payment.STATUS.FAILED
        db_payment.save()
        return APIResponse(200, "Payment canceled")


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


class RefundView(APIView):
    """
     Use to ask a refund for all the users associated with one Payment
    """

    authentification = False
    implemented_methods = ('POST',)

    def post(self, request, id, *args, **kwargs):
        """
        """

        db_payment = Payment.objects.get(id=id)
        failed = list()

        for payment in db_payment.payments.values():
            if payment['status'] != Payment.STATUS.COMPLETED:
                if payment['status'] == Payment.STATUS.PROCESSING:
                    payment['status'] = Payment.STATUS.REFUNDED
                continue

            sale_id = payment['sale_id']
            sale = paypalrestsdk.Sale.find(sale_id)

            refund = sale.refund({
                "amount": {
                    "total": payment['amount'],
                    "currency": db_payment.currency
                }
            })
            if not refund.success():
                failed.append(sale_id)
            else:
                payment['status'] = Payment.STATUS.REFUNDED

        db_payment.save()

        if failed:
            return APIResponse(200, f"Refund failed for {', '.join(failed)}")
        else:
            return APIResponse(200, "Refund successful")

class UserView(SingleObjectAPIView):
    model = User

class UsersView(MultipleObjectsAPIView):
    model = User


class FriendshipView(SingleObjectAPIView):
    model = Friendship

class FriendshipsView(MultipleObjectsAPIView):
    model = Friendship


class PaymentGroupView(SingleObjectAPIView):
    model = PaymentGroup

class PaymentGroupsView(MultipleObjectsAPIView):
    model = PaymentGroup

    def post(self, request, return_=False, *args, **kwargs):
        try:
            data = request.body.decode('utf-8')
            json_data = json.loads(data)
        except JSONDecodeError:
            return APIResponse(204, f"A content is required to create {self.verbose_name}")
        object_ = self.model.objects.create(name=json_data['name'])
        object_.users.add(*User.objects.filter(id__in=json_data['users']))
        return APIResponse(201, f"{self.verbose_name_plural} created successfully", object_.json(request) and return_)


class PaymentGroupMembershipView(SingleObjectAPIView):
    model = PaymentGroupMembership

class PaymentGroupMembershipsView(MultipleObjectsAPIView):
    model = PaymentGroupMembership


def redirect_website(request:HttpRequest):
    return redirect("http://localhost:3000/")
