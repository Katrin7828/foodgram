from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import FoodgramUserViewSet


router = SimpleRouter()
router.register(
    'users',
    FoodgramUserViewSet,
    basename='users',
)

urlpatterns = [
    path('', include(router.urls)),
]
