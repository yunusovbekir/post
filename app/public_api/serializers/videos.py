from rest_framework import serializers
from videos.models import Video


class PublicVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Video
        fields = (
            'id',
            'title',
            'url',
            'text',
        )
        read_only_fields = (
            'id',
        )
