from rest_framework import viewsets, permissions
from ..serializers.videos import PublicVideoSerializer
from videos.models import Video


class PublicVideosViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly Public API endpoint for Videos

    """
    queryset = Video.objects.all()
    serializer_class = PublicVideoSerializer
    permission_classes = (permissions.AllowAny,)
