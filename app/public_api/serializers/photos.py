from rest_framework import serializers
from photos.models import Photo


class PublicPhotoSerializer(serializers.ModelSerializer):

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
