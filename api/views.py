from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.urls import get_resolver
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.translation import gettext as _

import time
import json
from json import JSONDecodeError
import random
import string
from http import HTTPStatus

import paypalrestsdk

from django_modelapiview import APIView, ModelAPIView
from django_modelapiview.responses import APIResponse, NotFound, ExceptionCaught

from api.models import User, PaymentGroup, PaymentGroupMembership, Friendship, Payment, Payment

# Create your views here.

class PaymentView(APIView):
    """
     Ask Personal account for payment
    """

    route = "payment"
    enforce_authentification = True

    def post(self, request:HttpRequest, *args, **kwargs) -> APIResponse:
        """
        """

        data = request.body.decode('utf-8')
        json_data = json.loads(data)

        currency = json_data.get('currency') or "EUR"

        group_id = json_data.get('group')
        if group_id is None or not PaymentGroup.objects.filter(id=group_id).exists():
            return APIResponse(400, _("A payment cannot be created without a group"))

        total = round(json_data['total'], 2)
        users_mail = json_data['users']
        if not users_mail:
            return APIResponse(400, _("A payment cannot be created without at least one user"))
        if User.objects.filter(email__in=users_mail).count() != len(users_mail):
            return APIResponse(400, _("At least one user does not exist"))

        user_sum = round(sum(users_mail.values()), 2)
        if user_sum != total:
            return APIResponse(400, _("Total (%(total)d) does not match users sum (%(user_sum)d)") % {'total': total, 'user_sum': user_sum})
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
                return APIResponse(500, _("Failed to create payment for user %(mail)s") % {'mail': mail})
            payments_links[mail] = list((link.method, link.href, price) for link in payment.links)
            db_payment.payments[payment.id] = {'status': Payment.STATUS.PROCESSING, 'amount': price}

        db_payment.save()
        payments_links['id'] = db_payment.id
        return APIResponse(200, _("Sucessfully created payments"), payments_links)


class PaymentExecute(APIView):
    """
     Execute redirected payment
    """

    route = "payment/execute"
    enforce_authentification = True

    def get(self, request:HttpRequest, *args, **kwargs) -> APIResponse:
        """
        """

        payment_id = request.GET.get("paymentId")
        payment = paypalrestsdk.Payment.find(payment_id)
        try:
            db_payment =  Payment.objects.get(payments__contains={payment_id: {'status': Payment.STATUS.PROCESSING}})
        except ObjectDoesNotExist:
            return APIResponse(404, _("Payment does not exist or is not valid"))
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
                    return APIResponse(200, _("Sucessfully completed payment"))
                else:
                    return APIResponse(500, payout.error)
            else:
                return APIResponse(200, _("Successfully executed payment"))
        else:
            return APIResponse(500, _("Failed to execute payment"))


class PaymentCanceled(APIView):
    """
    """

    route = "payment/cancel"
    enforce_authentification = True

    def get(self, request:HttpRequest, *args, **kwargs) -> APIResponse:
        """
        """

        payment_id = request.GET.get("paymentId")
        db_payment = Payment.objects.get(payments__contains=[payment_id])
        if db_payment.payments[payment_id] == Payment.STATUS.COMPLETED:
            return APIResponse(403, _("Your payment is already completed"))
        db_payment.payments[payment_id] = Payment.STATUS.FAILED
        db_payment.save()
        return APIResponse(200, _("Payment canceled"))


class PayoutView(APIView):
    """
     Send money from Business to Business or Personal account
     Business -> Business / Personnal
    """

    route = "payout"
    enforce_authentification = True

    def post(self, request:HttpRequest, *args, **kwargs) -> APIResponse:
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
            return APIResponse(200, _("Payout %(payout_batch_id)d created successfully") % {'payout_batch_id': payout.batch_header.payout_batch_id})
        else:
            return APIResponse(500, payout.error)


class RefundView(APIView):
    """
     Use to ask a refund for all the users associated with one Payment
    """

    route = "refund/<int:id>"
    enforce_authentification = True

    def post(self, request:HttpRequest, id:int, *args, **kwargs) -> APIResponse:
        """
        """

        try:
            db_payment = Payment.objects.get(id=id)
        except ObjectDoesNotExist as e:
            return NotFound(str(e))
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
            return APIResponse(200, _("Refund failed for %(payments_failed)s") % {'payments_faled': ', '.join(failed)})
        else:
            return APIResponse(200, _("Refund successful"))


class UserView(ModelAPIView):
    route = "users"
    model = User
    enforce_authentification = True


class FriendshipView(ModelAPIView):
    route = "friendships"
    model = Friendship
    enforce_authentification = True

class PaymentGroupView(ModelAPIView):
    route = "paymentgroups"
    model = PaymentGroup
    enforce_authentification = True

    def post(self, request:HttpRequest, return_:bool=False, *args, **kwargs) -> APIResponse:
        try:
            data = request.body.decode('utf-8')
            json_data = json.loads(data)
        except JSONDecodeError:
            return APIResponse(204, _("A content is required to create %(verbose_name)s") % {'verbose_name' : self.verbose_name})
        object_ = self.model.objects.create(name=json_data['name'])
        object_.users.add(*User.objects.filter(id__in=json_data['users']))
        return APIResponse(201, _("%(verbose_name_plural)s created successfully") % {'verbose_name_plural': self.verbose_name_plural}, object_.json(request) and return_)


# class PaymentGroupMembershipView(ModelAPIView):
#     route = "paymentgroupmemberships"
#     model = PaymentGroupMembership
#     enforce_authentification = True


class PaymentView(ModelAPIView):
    route = "payments"
    model = Payment
    enforce_authentification = True


def redirect_website(request:HttpRequest):
    return redirect(f"http://{request.get_host().split(':')[0]}:3000/")
