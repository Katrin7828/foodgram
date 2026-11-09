from django.urls import path

from .views import AvatarView, SubscribeView, SubscriptionListView


urlpatterns = [
    path(
        'users/<int:id>/subscribe/',
        SubscribeView.as_view(),
        name='user-subscribe',
    ),
    path(
        'users/subscriptions/',
        SubscriptionListView.as_view(),
        name='user-subscriptions',
    ),
    path(
        'users/me/avatar/',
        AvatarView.as_view(),
        name='user-avatar',
    ),
]
