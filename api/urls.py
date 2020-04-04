from django.urls import include, path

from api.views import (
                        LoginView,
                        PaymentView, PaymentExecute,
                        UserView, UsersView,
                        FriendshipView, FriendshipsView,
                        GroupMembershipView,
                        GroupView, GroupsView
)

urlpatterns = [
    path('login', LoginView.as_view()),
    path('payment', PaymentView.as_view()),
    path('payment/execute', PaymentExecute.as_view()),

    path('users/<int:id>', UserView.as_view()),
    path('users/', UsersView.as_view()),
    path('group_memberships/<int:id>', GroupMembershipView.as_view()),
    path('friendships/<int:id>', FriendshipView.as_view()),
    path('friendships/', FriendshipsView.as_view()),
    path('groups/<int:id>', GroupView.as_view()),
    path('groups/', GroupsView.as_view()),
]
