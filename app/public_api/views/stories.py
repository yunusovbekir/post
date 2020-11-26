from rest_framework import viewsets, permissions
from stories.models import Story, StoryContent
from ..serializers.stories import (
    PublicStorySerializer,
    PublicStoryContentSerializer,
)


class PublicStoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly Public API endpoint for a Story

    """

    queryset = Story.objects.filter(status='ACTIVE')
    serializer_class = PublicStorySerializer
    permission_classes = (permissions.AllowAny,)


class StoryContentRetrieveAPIView(viewsets.ReadOnlyModelViewSet):
    """
    Readonly Public API endpoint for Story Contents

    """
    queryset = StoryContent.objects.all()
    serializer_class = PublicStoryContentSerializer
    permission_classes = (permissions.AllowAny,)
