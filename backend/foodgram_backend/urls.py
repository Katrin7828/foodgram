from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from recipes.views import redirect_to_recipe

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/', include('api.urls')),
    path('s/<str:short_code>/', redirect_to_recipe, name='recipe_short_link'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
