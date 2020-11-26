from rest_framework import generics
from rest_framework import permissions
from ..serializers.core import (
    PublicSettingsSerializer,
    PublicSocialMediaSerializer,
    PublicContactFormSerializer,
    PublicOpinionSerializer,
)
from core.models import Settings, SocialMedia


class SettingsAPIView(generics.ListAPIView):
    """ Public API endpoint for getting list of Settings data """

    serializer_class = PublicSettingsSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    queryset = Settings.objects.all()


class SocialMediaListAPIView(generics.ListAPIView):
    """
    Public API endpoints for getting list of Social Media accounts
    """

    serializer_class = PublicSocialMediaSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    queryset = SocialMedia.objects.all()


class ContactFormCreateAPIView(generics.CreateAPIView):
    """ Public API endpoint for sending Contact Form. """

    serializer_class = PublicContactFormSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]


class OpinionCreateAPIView(generics.CreateAPIView):
    """ Public API endpoint for sending Contact Form. """

    serializer_class = PublicOpinionSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
