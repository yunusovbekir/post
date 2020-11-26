from rest_framework import serializers
from photos.models import Photo, Gallery


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Photo
        fields = (
            'id',
            'title',
            'photo',
        )
        read_only_fields = (
            'id',
        )


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = Gallery
        fields = (
            'id',
            'photo',
            'description',
        )
        read_only_fields = (
            'id',
        )
