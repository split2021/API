from django.urls import include, path

from api.views import (
                        LoginView,
                        PaymentView, PaymentExecute, PayoutView, PaymentCanceled, RefundView,
                        UserView, UsersView,
                        FriendshipView, FriendshipsView,
                        PaymentGroupMembershipView,
                        PaymentGroupView, PaymentGroupsView
)

urlpatterns = [
    path('login', LoginView.as_view()),

    path('payment', PaymentView.as_view()),
    path('payment/execute', PaymentExecute.as_view()),
    path('payment/cancel', PaymentCanceled.as_view()),
    path('payout', PayoutView.as_view()),
    path('refund/<int:id>', RefundView.as_view()),

    path('users/<int:id>', UserView.as_view()),
    path('users/', UsersView.as_view()),
    path('payment_group_memberships/<int:id>', PaymentGroupMembershipView.as_view()),
    path('friendships/<int:id>', FriendshipView.as_view()),
    path('friendships/', FriendshipsView.as_view()),
    path('payment_groups/<int:id>', PaymentGroupView.as_view()),
    path('payment_groups/', PaymentGroupsView.as_view()),
]
