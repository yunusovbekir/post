from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from knox.auth import TokenAuthentication

from news.models import (
    Post,
    Category,
    Comment,
    CommentLike,
    CommentDislike,
    PostLike,
    PostDislike,
)

from ..permissions import CommentOwner, CommentOwnerOrIsAdmin
from ..serializers.news import (
    PublicPostListModelSerializer,
    PublicPostDetailModelSerializer,
    PublicCommentCreateSerializer,
    PublicCommentUpdateDestroySerializer,
    PublicCategoryListModelSerializer,
)

User = get_user_model()


# =========================== Post API Views ==================================


class PublicPostViewSet(viewsets.ModelViewSet):
    """
    Public API endpoint for `retrieving` a Post, getting `list` of Posts,
     and for making `Post Like` and `Post Dislike` request.
    Retrieve only those which have status 'OPEN', and Approved by Editor

    Allowed Requests:
        `GET` => All users
    """
    queryset = Post.objects.filter(
        status='Open', is_approved=True
    )
    authentication_classes = (TokenAuthentication,)

    def retrieve(self, request, pk):
        post = self.get_object()
        post.views = post.views + 1

        if request.user.is_authenticated:
            auth_user = self.request.user
            liked_posts = PostLike.objects.filter(user=auth_user, post=post)
            disliked_posts = PostDislike.objects.filter(user=auth_user,
                                                        post=post)
            saved_posts = self.request.user.saved_news.filter(id=post.id)

            if liked_posts.count() > 0:
                post.is_liked_by_auth_user = True
            else:
                post.is_liked_by_auth_user = False

            if disliked_posts.count() > 0:
                post.is_disliked_by_auth_user = True
            else:
                post.is_disliked_by_auth_user = False

            if saved_posts.count() > 0:
                post.is_saved_by_auth_user = True
            else:
                post.is_saved_by_auth_user = False
        else:
            post.is_liked_by_auth_user = False
            post.is_disliked_by_auth_user = False
            post.is_saved_by_auth_user = False

        post.save()

        serializer = PublicPostDetailModelSerializer(
            post, context={"request": self.request}
        )
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'list':
            return PublicPostListModelSerializer

        return PublicPostDetailModelSerializer

    def get_permissions(self):
        if self.action in ('retrieve', 'list',):
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description='Any authenticated user is allowed to'
                              ' make a `PATCH` request for'
                              '`post like request`.'
    )
    @action(detail=True, methods=['PATCH'],
            url_path='posts/pk/like/', url_name='public-post-like-request')
    def like_request(self, request, *args, **kwargs):
        """
        Get authenticated user, add to users field in PostLike model, and
        remove from PostDislike model, if it exists.
        """

        if request.user.is_authenticated:
            post = self.get_object()

            # get Post Dislike models
            obj_dislike = PostDislike.objects.all()

            # if request user is among the ones who disliked the same post,
            # remove from disliked users list
            if obj_dislike.filter(post=post.id, user=request.user.id):
                post.post_dislike.user.remove(request.user)

            # add request user and save
            post.post_like.user.add(request.user)
            post.post_like.save()

            return Response(
                {'message': 'Like request was successful'},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                'message': 'Bad request',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_description='Any authenticated user is allowed to'
                              ' make a `PATCH` request for'
                              '`post dislike request`.'
    )
    @action(detail=True, methods=['PATCH'],
            url_path='posts/pk/dislike/',
            url_name='public-post-dislike-request')
    def dislike_request(self, request, *args, **kwargs):
        """
        Get authenticated user, add to users field in PostDislike model, and
        remove from PostLike model if it exists
        """

        if request.user.is_authenticated:
            post = self.get_object()

            # get Post Like models
            obj_like = PostLike.objects.all()

            # if request user is among the ones who liked the same post,
            # remove from liked users list
            if obj_like.filter(post=post.id, user=request.user.id):
                post.post_like.user.remove(request.user)

            # add request user and save
            post.post_dislike.user.add(request.user)
            post.post_dislike.save()

            return Response(
                {'message': 'Dislike request was successful'},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                'message': 'Bad request',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ========================== Comment API Views ================================


class CommentViewSet(viewsets.ModelViewSet):
    """
    Public API endpoint for commenting on a post, making like / dislike request
    on a comment.

    Allowed requests:
        `GET` => Any authenticated user
        `POST` => Any authenticated user
        `PATCH` => update comment => Owner only
        `PATCH` => like request => Any authenticated user
        `PATCH` => dislike request => Any authenticated user
        `DELETE` => Owner and admin user
    """
    queryset = Comment.objects.all()
    serializer_class = PublicCommentCreateSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = []
        if self.action in ['create', 'like_request', 'dislike_request']:
            permission_classes = (IsAuthenticated,)
        elif self.action == 'update_comment':
            permission_classes = (CommentOwner,)
        elif self.action == 'destroy':
            permission_classes = (CommentOwnerOrIsAdmin,)
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description='Any authenticated user is allowed to'
                              ' make a `POST` request for'
                              '`adding a Comment on a Post`.'
    )
    @action(detail=True, methods=['post'],
            url_path='comments', url_name='comment-create')
    def create(self, request, *args, **kwargs):
        """
        Create a new comment, Authenticated user is allowed
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            Comment.objects.create(**serializer.validated_data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                'status': 'Bad Request',
                'message': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_description='Only owner of the comment is allowed to'
                              ' make a `PATCH` request for'
                              '`the comment`.'
    )
    @action(detail=True, methods=['patch'],
            url_path='comments/pk/',
            url_name='update-comment')
    def update_comment(self, request, *args, **kwargs):
        """
        Update Comment endpoint, only Comment Owner is allowed

        """
        serializer = PublicCommentUpdateDestroySerializer(
            self.get_object(),
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'status': 'Bad Request',
                'message': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        operation_description='Any authenticated user is allowed to'
                              ' make a `PATCH` request for'
                              '`comment like request`.'
    )
    @action(detail=True, methods=['PATCH'],
            url_path='comments/pk/like/',
            url_name='like-request')
    def like_request(self, request, *args, **kwargs):
        """
        Get authenticated user, add to users field in CommentLike model,
        and remove from CommentDislike model, if it exists
        """

        if request.user.is_authenticated:
            comment = self.get_object()

            # get Comment Dislike models
            obj_dislike = CommentDislike.objects.all()

            # if request user is among the ones who liked the same comment,
            # remove from disliked users list
            if obj_dislike.filter(comment=comment.id, user=request.user.id):
                comment.comment_dislike.user.remove(request.user)

            # add request user and save
            comment.comment_like.user.add(request.user)
            comment.comment_like.save()

            return Response(
                {'message': 'Like request was successful'},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                'message': 'Bad request',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @swagger_auto_schema(
        operation_description='Any authenticated user is allowed to'
                              ' make a `PATCH` request for'
                              '`comment dislike request`.'
    )
    @action(detail=True, methods=['PATCH'],
            url_path='comments/pk/dislike/',
            url_name='dislike-request')
    def dislike_request(self, request, *args, **kwargs):
        """
        Get authenticated user, add to users field in CommentDislike model,
        and remove from CommentLike model, if it exists.
        """

        if request.user.is_authenticated:
            comment = self.get_object()

            # get Comment Dislike models
            obj_like = CommentLike.objects.all()

            # if request user is among the ones who disliked the same comment,
            # remove from liked users list
            if obj_like.filter(comment=comment.id, user=request.user.id):
                comment.comment_like.user.remove(request.user)

            # add request user and save
            comment.comment_dislike.user.add(request.user)
            comment.comment_dislike.save()

            return Response(
                {'message': 'Dislike request was successful'},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                'message': 'Bad request',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# -----------------------------------------------------------------------------

class CategoryListApiView(generics.ListAPIView):
    """
    Public API endpoint for getting a list of News Categories

    Allowed requests:
        `GET` => Any user
    """

    serializer_class = PublicCategoryListModelSerializer
    authentication_classes = []
    permission_classes = (AllowAny,)
    queryset = Category.objects.filter(parent_category=None)
