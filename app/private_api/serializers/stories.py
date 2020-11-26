from rest_framework import serializers
from stories.models import Story, StoryContent
from ..serializers.news import PostSerializer


class StorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Story
        fields = (
            'id',
            'title',
            'status',
            'description',
            'start_date',
            'end_date',
            'cover_photo',
            'slug',
            'ordering',
            'views',
        )
        read_only_fields = (
            'id',
        )


class StoryContentSerializer(serializers.ModelSerializer):
    story = StorySerializer()
    post = PostSerializer()

    class Meta:
        model = StoryContent
        fields = (
            'story',
            'post',
        )
        depth = 1
