from knox.auth import TokenAuthentication
from rest_framework import viewsets, permissions
from videos.models import Video
from ..serializers.videos import VideoSerializer


class VideoApiViewSet(viewsets.ModelViewSet):
    """
    API endpoints for working on Videos

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PUT` => Staff user
        `PATCH` => Staff user
        `DELETE` => Staff user
    """

    authentication_classes = (TokenAuthentication,)
    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    permission_classes = (permissions.IsAdminUser,)
