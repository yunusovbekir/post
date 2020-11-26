from rest_framework import viewsets, permissions
from ..serializers.photos import PublicPhotoSerializer
from photos.models import Photo


class PublicPhotoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly Public API endpoint for Photos

    """
    queryset = Photo.objects.all()
    serializer_class = PublicPhotoSerializer
    permission_classes = (permissions.AllowAny,)
