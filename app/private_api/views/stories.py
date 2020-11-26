from knox.auth import TokenAuthentication
from rest_framework import viewsets
from rest_framework import permissions

from ..serializers.stories import StorySerializer, StoryContentSerializer
from stories.models import Story, StoryContent


class StoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for working on Stories.

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PATCH` => Staff user
        `PATCH` => Staff user
        `DELETE` => Staff user
    """

    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = (permissions.IsAdminUser,)
    authentication_classes = (TokenAuthentication,)


class StoryContentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for working on Story Contents.

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PATCH` => Staff user
        `PATCH` => Staff user
        `DELETE` => Staff user
    """

    queryset = StoryContent.objects.all()
    serializer_class = StoryContentSerializer
    permission_classes = (permissions.IsAdminUser,)
    authentication_classes = (TokenAuthentication,)
