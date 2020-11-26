from knox.auth import TokenAuthentication
from rest_framework import viewsets, permissions
from ..serializers.photos import (
    PhotoSerializer,
    GallerySerializer,
)
from photos.models import Photo, Gallery


class PhotoApiViewSet(viewsets.ModelViewSet):
    """
    API endpoint for working on Photos.
    All photos are controlled with this API.

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PATCH` => Staff user
        `PATCH` => Staff user
        `DELETE` => Staff user

    """

    serializer_class = PhotoSerializer
    authentication_classes = (TokenAuthentication,)
    queryset = Photo.objects.all()
    permission_classes = (permissions.IsAdminUser,)


class GalleryApiViewSet(viewsets.ModelViewSet):
    """
    API endpoint for working on Gallery.

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PATCH` => Staff user
        `PATCH` => Staff user
        `DELETE` => Staff user
    """

    serializer_class = GallerySerializer
    authentication_classes = (TokenAuthentication,)
    queryset = Gallery.objects.all()
    permission_classes = (permissions.IsAdminUser,)
