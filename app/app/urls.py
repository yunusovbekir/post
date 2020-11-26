from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="News Website APIs",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.IsAdminUser,),
)

CURRENT_VERSION = 'v1'

URLS = [
    path('admin/', admin.site.urls),
    path('api/' + CURRENT_VERSION + '/auth/', include('knox.urls')),
    path('api/' + CURRENT_VERSION + '/', include('private_api.urls')),
    path('api/' + CURRENT_VERSION + '/', include('public_api.urls')),
    # path('api/' +CURRENT_VERSION+ '/search/', include('search_indexes.urls'))
]

SWAGGER_URLS = [
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'),
    re_path(r'^$', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
]

urlpatterns = URLS + SWAGGER_URLS + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
