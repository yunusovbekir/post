from django.forms import model_to_dict
from django.contrib.auth import get_user_model

from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method

from news.models import (
    Post,
    Content,
    PostIdentifier,
    Category,
    Comment,
    CommentLike,
    CommentDislike,
)

from .photos import PublicPhotoSerializer
from ..utils.utils import get_comment_count_tool

USER = get_user_model()


# -----------------------------------------------------------------------------


class PublicCategorySerializer(serializers.ModelSerializer):
    """
    Category serializer for category field on Post Model Serializer
    """

    class Meta:
        model = Category
        fields = (
            # 'parent_category',
            'title',
        )


# -----------------------------------------------------------------------------


class PublicKeywordModelSerializer(serializers.ModelSerializer):
    """
    Keyword (Post Identifier ) serializer for keyword field on
    Post Model Serializer
    """

    class Meta:
        model = PostIdentifier
        fields = (
            'title',
        )


# -----------------------------------------------------------------------------


class PublicAuthorSerializer(serializers.ModelSerializer):
    """
    Author serializer for author field on Post Model Serializer
    """

    class Meta:
        model = USER
        fields = (
            'id',
            'user_type',
            'profession',
            'first_name',
            'last_name',
            'avatar',
        )


# -----------------------------------------------------------------------------


class PublicUserModelSerializer(serializers.ModelSerializer):
    """
    User serializer for User ( Commented_by ) field on Comment Model Serializer
    """

    full_name = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_full_name(self, obj):
        return obj.first_name + " " + obj.last_name

    class Meta:
        model = USER
        fields = (
            'avatar',
            'full_name',
        )


# ========================== Content Serializers ==============================


class PublicContentListSerializer(serializers.ListSerializer):
    """
    Overriding 'to_representation" method on Content serializer
    to filter queryset
    """

    def to_representation(self, data):
        data = data.filter(content_type="Main Text", ordering=1)
        return super(
            PublicContentListSerializer, self
        ).to_representation(data=data)


# -----------------------------------------------------------------------------


class PublicContentFilteredModelSerializer(serializers.ModelSerializer):
    """
    Content serializer for content field on Post List Model Serializer
    """

    class Meta:
        model = Content
        fields = '__all__'
        list_serializer_class = PublicContentListSerializer


# -----------------------------------------------------------------------------


class PublicContentModelSerializer(serializers.ModelSerializer):
    """
    Content serializer for content field on Post Detail Model Serializer
    """
    photo = PublicPhotoSerializer()

    class Meta:
        model = Content
        fields = (
            'id',
            'post',
            'photo',
            'video',
            'content_type',
            'ordering',
            'title',
            'text',
        )


# ========================== Comment Serializers ==============================


class PublicChildCommentModelSerializer(serializers.ModelSerializer):
    """ Child Model Serializer for Comment Model Serializer """

    commented_by = PublicUserModelSerializer()

    class Meta:
        model = Comment
        fields = (
            'id',
            'commented_by',
            'comment',
            'post_date',
            'like_count',
            'dislike_count',
            'is_disliked_by_auth_user',
            'is_liked_by_auth_user',
        )
        read_only_fields = (
            'id',
        )
        depth = 1


# -----------------------------------------------------------------------------


class PublicCommentModelSerializer(serializers.ModelSerializer):
    """ Comment Model Serializer for Post Detail Model Serializer """

    reply = serializers.SerializerMethodField(read_only=True)
    commented_by = PublicUserModelSerializer()

    def get_reply(self, obj):
        queryset = Comment.objects.filter(
            is_approved=True, replied_comment=obj.id
        )
        request = self.context.get('request')
        serializer = PublicChildCommentModelSerializer(
            queryset, many=True, context={"request": request}
        )
        return serializer.data

    class Meta:
        model = Comment
        fields = (
            'id',
            'commented_by',
            'comment',
            'post_date',
            'like_count',
            'dislike_count',
            'reply',
            'is_disliked_by_auth_user',
            'is_liked_by_auth_user',
        )
        depth = 1


# -----------------------------------------------------------------------------


class PublicCommentCreateSerializer(serializers.ModelSerializer):
    """ Comment Create Model Serializer """

    commented_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'post',
            'replied_comment',
            'comment',
            'commented_by',
        )


# -----------------------------------------------------------------------------


class PublicCommentUpdateDestroySerializer(serializers.ModelSerializer):
    """ Comment Update Destroy Serializer """

    class Meta:
        model = Comment
        fields = (
            'comment',
        )
        read_only_fields = (
            'id',
        )


# ======================== Post Serializers ===================================


class PublicRelatedPostListModelSerializer(serializers.ModelSerializer):
    """ Serializer for returning related posts as objects """

    class Meta:
        model = Post


class PublicPostListModelSerializer(serializers.ModelSerializer):
    """ Post List Model Serializer """

    content = PublicContentModelSerializer(source='post_content', many=True)
    keyword = PublicKeywordModelSerializer(required=False)
    category = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    author = PublicAuthorSerializer()

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'slug',
            'author',
            'short_description',
            'title_type',
            'keyword',
            'category',
            'is_advertisement',
            'publish_date',
            'views',
            'content',
        )
        read_only_fields = (
            'id',
        )
        depth = 1


# -----------------------------------------------------------------------------


class PublicPostDetailModelSerializer(serializers.ModelSerializer):
    """ Post Detail ( Retrieve ) Model Serializer """

    content = PublicContentModelSerializer(source='post_content', many=True)
    keyword = PublicKeywordModelSerializer(required=False)
    category = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    author = PublicAuthorSerializer()
    comment = serializers.SerializerMethodField(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    related_posts_list = serializers.SerializerMethodField(read_only=True)

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_comment_count(self, post):
        """ Get total count of comments on a post and their replies """

        return get_comment_count_tool(post)

    def get_related_posts_list(self, obj):
        related_category = [category.id for category in obj.category.all()]
        posts = Post.objects.filter(
            category__in=related_category,
        ).exclude(id=obj.id)[:12]
        request = self.context.get('request')
        serializer = PublicPostListModelSerializer(
            posts, context={"request": request}, many=True
        )
        return serializer.data

    def get_comment(self, obj):
        comments = Comment.objects.filter(
            replied_comment=None, post=obj.id, is_approved=True
        )
        all_comments = Comment.objects.filter(post=obj.id)
        request = self.context.get('request')

        for comment in all_comments:
            if request.user.is_authenticated:
                auth_user = request.user
                liked_comments = CommentLike.objects.filter(
                    user=auth_user, comment=comment
                )
                disliked_comments = CommentDislike.objects.filter(
                    user=auth_user, comment=comment
                )

                if liked_comments.count() > 0:
                    comment.is_liked_by_auth_user = True
                else:
                    comment.is_liked_by_auth_user = False
                if disliked_comments.count() > 0:
                    comment.is_disliked_by_auth_user = True
                else:
                    comment.is_disliked_by_auth_user = False

            else:
                comment.is_liked_by_auth_user = False
                comment.is_disliked_by_auth_user = False
            comment.save()
        serializer = PublicCommentModelSerializer(
            comments, context={"request": request}, many=True
        )
        return serializer.data

    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'author',
            'slug',
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
            'publish_date',
            'like_count',
            'dislike_count',
            'comment_count',
            'comment',
            'related_posts_list',
            'is_liked_by_auth_user',
            'is_disliked_by_auth_user',
            'is_saved_by_auth_user',

        )
        depth = 1
        read_only_fields = (
            'id',
        )


# -----------------------------------------------------------------------------


class PublicPostLikeDislikeUpdateSerializer(serializers.ModelSerializer):
    """
    Update only Like or Dislike count by a user
    """

    class Meta:
        model = Post
        fields = (
            'like_count',
            'dislike_count',
        )


# -----------------------------------------------------------------------------


class PublicCategoryListModelSerializer(serializers.ModelSerializer):
    child_category = serializers.SerializerMethodField('get_child_categories')

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'child_category',
            'ordering',
            'url',
        )
        depth = 1
        read_only_fields = (
            'id',
        )

    def get_child_categories(self, obj):
        categories = Category.objects.filter(parent_category=obj.id)
        return [model_to_dict(category) for category in categories]
