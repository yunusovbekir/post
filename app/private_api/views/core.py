from knox.auth import TokenAuthentication
from rest_framework import viewsets, parsers, pagination

from ..serializers.core import (
    SettingsSerializer,
    SocialMediaSerializer,
    ContactFormSerializer,
)
from ..permissions import IsCustomAdminUser
from core.models import Settings, SocialMedia, ContactForm


class ExamplePagination(pagination.PageNumberPagination):
    page_size = 10


class SettingsAPIView(viewsets.ModelViewSet):
    """
    API endpoint for working on Website Settings.

    Allowed requests:
        `GET` => Admin user,
        `POST` => Admin user,
        `PUT` => Admin user,
        `PATCH` => Admin user,
        `DELETE` => Admin user,
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsCustomAdminUser,)
    serializer_class = SettingsSerializer
    queryset = Settings.objects.all()
    parser_classes = (parsers.MultiPartParser,)


class SocialMediaAPIView(viewsets.ModelViewSet):
    """
    API endpoint for working on Website's Social Media accounts.

    Allowed requests:
        `GET` => Admin user,
        `POST` => Admin user,
        `PUT` => Admin user,
        `PATCH` => Admin user,
        `DELETE` => Admin user,
    """
    queryset = SocialMedia.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsCustomAdminUser,)
    serializer_class = SocialMediaSerializer


class ContactFormAPIView(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for getting Contact Forms sent by users.

    Allowed requests:
        `GET` => Admin user
        `POST` => Nobody
        `PUT` => Nobody
        `PATCH` => Nobody
        `DELETE` => Nobody
    """
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsCustomAdminUser,)
