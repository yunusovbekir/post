from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from news.models import (
    Post,
    Content,
    Category,
    Comment,
    PostIdentifier,
    Feedback,
    PostLike,
    PostDislike,
    CommentLike,
    CommentDislike,
)

from .photos import PhotoSerializer
from public_api.utils.utils import get_comment_count_tool

User = get_user_model()


class SelectCategorySerializer(serializers.ModelSerializer):
    """
    Category serializer for category field on Post Model Serializer
    """

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
        )
        read_only_fields = (
            'id',
        )

# -----------------------------------------------------------------------------


class UserModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name'
        )
        read_only_fields = (
            'id',
        )


# -----------------------------------------------------------------------------


class KeywordModelSerializer(serializers.ModelSerializer):
    """
    Keyword (Post Identifier ) serializer for keyword field on
    Post Model Serializer
    """

    class Meta:
        model = PostIdentifier
        fields = (
            'id',
            'title',
        )
        read_only_fields = (
            'id',
        )


# -----------------------------------------------------------------------------


class ContentUpdateModelSerializer(serializers.ModelSerializer):
    """
    Content serializer for content field on Post Detail Model Serializer
    """

    class Meta:
        model = Content
        fields = "__all__"
        read_only_fields = (
            'id',
        )


class ContentModelSerializer(serializers.ModelSerializer):
    """
    Content serializer for content field on Post Detail Model Serializer
    """

    photo = PhotoSerializer()

    class Meta:
        model = Content
        fields = "__all__"
        read_only_fields = (
            'id',
        )


# -----------------------------------------------------------------------------


class ChildCommentModelSerializer(serializers.ModelSerializer):
    """ Child Model Serializer for Comment Model Serializer """

    commented_by = UserModelSerializer()

    class Meta:
        model = Comment
        fields = (
            'id',
            'commented_by',
            'is_approved',
            'comment',
            'post_date',
            'like_count',
            'dislike_count',
        )
        read_only_fields = (
            'id',
        )
        depth = 1


class CommentModelSerializer(serializers.ModelSerializer):
    """ Comment Model Serializer for Post Detail Model Serializer """

    commented_by = UserModelSerializer()
    reply = ChildCommentModelSerializer(many=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'commented_by',
            'is_approved',
            'comment',
            'post_date',
            'like_count',
            'dislike_count',
            'reply',
        )
        read_only_fields = (
            'id',
        )
        depth = 1


# ========================== POST Serializers =================================


class PostCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'slug',
            'custom_slug',
            'category',
            'short_description',
            'title_type',
            'is_approved',
            'is_advertisement',
            'status',
            'social_meta_title',
            'social_meta_description',
            'seo_meta_title',
            'seo_meta_description',
            'seo_meta_keywords',
            'keyword',
            'author',
            'publish_date',
            'end_date',
            'top_news',
            'show_in_home_page',
            'is_editors_choice'
        )
        read_only_fields = (
            'id',
        )


# -----------------------------------------------------------------------------


class NonApprovedPostUpdateSerializer(serializers.ModelSerializer):
    """
    Model serializer for Post Update by Reporter
    """
    category = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Post
        exclude = (
            'is_approved',
            'views',
            'publish_date',
            'created_at',
            'updated_at',
            'deleted_at',
        )
        read_only_fields = (
            'id',
        )

    def update(self, instance, validated_data):
        if validated_data.get('category'):
            categories = validated_data.pop('category')
            instance.category.clear()
            for category in categories:
                category, created = Category.objects.get_or_create(
                    id=category.id
                )
                instance.category.add(category)
        for key in validated_data.keys():
            setattr(instance, key, validated_data.get(key))
        instance.save()
        return instance


# -----------------------------------------------------------------------------


class ApprovedPostUpdateSerializer(serializers.ModelSerializer):
    """
    Model serializer for Post Update by Editor
    """
    category = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
    )

    class Meta:
        model = Post
        exclude = (
            'created_at',
            'updated_at',
            'deleted_at',
        )
        read_only_fields = (
            'publish_date',
            'views',
            'id',
        )

    def update(self, instance, validated_data):
        categories = validated_data.pop('category')
        instance.category.clear()
        for category in categories:
            category, created = Category.objects.get_or_create(
                id=category.id
            )
            instance.category.add(category)
        for key in validated_data.keys():
            setattr(instance, key, validated_data.get(key))
        instance.save()
        return instance


# -----------------------------------------------------------------------------


class PostSerializer(serializers.ModelSerializer):
    content = ContentModelSerializer(source='post_content', many=True)
    keyword = KeywordModelSerializer(required=False)
    category = SelectCategorySerializer(many=True)
    author = UserModelSerializer()
    comment = CommentModelSerializer(source='post_commented',
                                     many=True, required=False)
    comment_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'author',
            'slug',
            'custom_slug',
            'short_description',
            'title_type',
            'keyword',
            'category',
            'is_advertisement',
            'publish_date',
            'content',
            'social_meta_title',
            'social_meta_description',
            'seo_meta_title',
            'seo_meta_description',
            'seo_meta_keywords',
            'views',
            'status',
            'is_approved',
            'publish_date',
            'like_count',
            'dislike_count',
            'comment_count',
            'comment',
            'end_date',
            'top_news',
            'show_in_home_page',
            'is_editors_choice'
        )
        depth = 1
        read_only_fields = (
            'id',
        )

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_comment_count(self, post):
        """ Get total count of comments on a post and their replies """

        return get_comment_count_tool(post)


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category API View
    """

    class Meta:
        model = Category
        fields = (
            'id',
            'parent_category',
            'title',
            'ordering',
        )
        read_only_fields = (
            'id',
        )


class FeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for `Create`, `Update`, `Destroy` requests
    """
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    post_date = serializers.ReadOnlyField()

    class Meta:
        model = Feedback
        fields = (
            'id',
            'post',
            'owner',
            'text',
            'post_date',
        )
        read_only_fields = (
            'id',
        )


class FeedbackGetSerializer(serializers.ModelSerializer):
    """
    Serializer for `Retrieve` and `List` requests
    """

    class Meta:
        model = Feedback
        fields = (
            'id',
            'post',
            'owner',
            'text',
            'post_date',
        )
        read_only_fields = (
            'id',
        )


class PostIdentifierSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostIdentifier
        fields = (
            'id',
            "title",
        )
        read_only_fields = (
            'id',
        )


class PostLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostLike
        fields = (
            'id',
            'post',
            'user',
        )
        read_only_fields = (
            'id',
        )


class PostDislikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostDislike
        fields = (
            'id',
            'post',
            'user',
        )
        read_only_fields = (
            'id',
        )


class CommentSerializer(serializers.ModelSerializer):
    commented_by = UserModelSerializer()

    class Meta:
        model = Comment
        fields = (
            'id',
            'post',
            'replied_comment',
            'is_approved',
            'commented_by',
            'comment',
            'like_count',
            'dislike_count',
            'post_date',
        )
        read_only_fields = (
            'id',
            'post',
            'replied_comment',
            'commented_by',
            'comment',
            'like_count',
            'dislike_count',
            'post_date',
        )


class CommentLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentLike
        fields = (
            'id',
            'comment',
            'user',
        )
        read_only_fields = (
            'id',
            'comment',
            'user',
        )


class CommentDislikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentDislike
        fields = (
            'id',
            'comment',
            'user',
        )
        read_only_fields = (
            'id',
            'comment',
            'user',
        )
