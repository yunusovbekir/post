from rest_framework import serializers
from stories.models import Story, StoryContent
from .news import PublicPostListModelSerializer


class PublicStorySerializer(serializers.ModelSerializer):

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
            'views'
        )


class PublicStoryContentSerializer(serializers.ModelSerializer):
    story = PublicStorySerializer(read_only=True)
    post = PublicPostListModelSerializer(read_only=True)

    class Meta:
        model = StoryContent
        fields = (
            'story',
            'post',
        )
