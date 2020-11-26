from drf_yasg.utils import swagger_auto_schema
from knox.auth import TokenAuthentication
from rest_framework import status, viewsets, permissions, pagination
from django.utils.translation import ugettext_lazy as _
from news.models import (
    Post,
    Category,
    Content,
    Comment,
    Feedback,
    PostIdentifier,
    PostLike,
    PostDislike,
    CommentLike,
    CommentDislike,
)

from rest_framework.decorators import action
from rest_framework.response import Response
from .. import permissions as perm
from ..serializers.news import (
    PostCreateSerializer,
    NonApprovedPostUpdateSerializer,
    ApprovedPostUpdateSerializer,
    PostSerializer,
    ContentModelSerializer,
    ContentUpdateModelSerializer,
    CategorySerializer,
    FeedbackSerializer,
    FeedbackGetSerializer,
    PostIdentifierSerializer,
    PostLikeSerializer,
    PostDislikeSerializer,
    CommentSerializer,
    CommentLikeSerializer,
    CommentDislikeSerializer,
)

from news.options.tools import (
    NEWS_STATUS,
    TITLE_TYPES,
    TOP_NEWS,
    CONTENT_TYPES,
)


class ExamplePagination(pagination.PageNumberPagination):
    page_size = 10


class PostApiView(viewsets.ModelViewSet):
    """
    API endpoint for working on Posts.
    `Post` and `Post's Contents` are different endpoints.

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PATCH` => Reporter user (if Post has not been approved)
        `PATCH` => Editor or Superuser user (if Post has been approved)
        `DELETE` => Admin user
    """
    authentication_classes = (TokenAuthentication,)
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ExamplePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        if self.action == 'update_non_approved':
            return NonApprovedPostUpdateSerializer
        if self.action == 'update_approved':
            return ApprovedPostUpdateSerializer
        return PostSerializer

    def get_permissions(self):
        """
        Post CREATE , POST => Any Staff User
        Post PATCH limited fields => Reporter user is allowed
        Post PATCH all fields => Editor user is allowed
        Post DELETE => Only Admin is allowed
        """
        if self.action == 'destroy':
            permission_classes = (perm.IsCustomAdminUser,)
        elif self.action == 'update_non_approved':
            permission_classes = (permissions.IsAdminUser,)
        elif self.action == 'update_approved':
            permission_classes = (perm.IsEditorUserOrCustomAdmin,)
        else:
            permission_classes = (permissions.IsAdminUser,)
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description='Anyone can create a post, '
                              'including `Reporters`. \n'

                              ' Response: \n'
                              ' `201` => CREATED\n'
                              ' `401` => Unauthenticated user\n'
                              ' `403` => Not Staff user\n'
                              ' `400` => Invalid data\n'
    )
    def create(self, request, *args, **kwargs):

        if self.request.user.user_type == 4:
            request.data['is_approved'] = True

        serializer = PostCreateSerializer(
            data=request.data,
            context={"request": self.request},
        )
        if serializer.is_valid(raise_exception=True):

            category = serializer.validated_data.pop('category')
            obj = Post.objects.create(
                **serializer.validated_data
            )
            for category in category:
                category, created = Category.objects.get_or_create(
                    id=category.id
                )
                obj.category.add(category)
            obj.save()
            return Response(
                {
                    'post_id': obj.id,
                    'status': _('Post is created successfully')
                },
                status=status.HTTP_201_CREATED
            )

    @swagger_auto_schema(
        operation_description='Allow update the post by reporter, '
                              'if the post has not been published. \n'

                              'Response: \n'
                              ' `201` => CREATED\n'
                              ' `401` => Unauthenticated user\n'
                              ' `403` => Not Staff user\n'
                              ' `400` => Invalid data\n'
    )
    @action(detail=True, methods=['patch'],
            url_name='update-non-approved-post',
            url_path='<int:pk>/update-non-approved')
    def update_non_approved(self, request, *args, **kwargs):
        """

        """
        obj = self.get_object()
        if not obj.is_approved:
            serializer = NonApprovedPostUpdateSerializer(
                obj,
                data=request.data,
                partial=True,
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        'data': serializer.data,
                        'status': _('Post is updated successfully')
                    },
                    status=status.HTTP_200_OK,
                )
        return Response(
            {"status": "You are not allowed to update approved posts"},
            status=status.HTTP_403_FORBIDDEN,
        )

    @swagger_auto_schema(
        operation_description='Allow update the post by reporter, '
                              'if the post has not been published. \n'

                              'Response: \n'
                              ' `201` => CREATED\n'
                              ' `401` => Unauthenticated user\n'
                              ' `403` => Not Staff user or is Reporter user\n'
                              ' `400` => Invalid data\n'
    )
    @action(detail=True, methods=['patch'],
            url_name='update-approved-post',
            url_path='<int:pk>/update-approved/')
    def update_approved(self, request, *args, **kwargs):

        obj = self.get_object()
        serializer = ApprovedPostUpdateSerializer(
            obj,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    'data': serializer.data,
                    'status': _('Post is updated successfully')
                },
                status=status.HTTP_200_OK,
            )


class ContentApiView(viewsets.ModelViewSet):
    """
    API endpoints for Post Contents.
    All staff users can perform all requests.
    Exception:
        If post is approved, reporter user is allowed only for SAFE_METHODS.

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PUT` and `PATCH`=> Staff user if Post is not approved
        `PUT` and `PATCH` => Editor and Admin user if Post is approved
        `DELETE` => Admin
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (perm.ContentPermission,)
    queryset = Content.objects.all()

    def get_serializer_class(self):
        if self.action in (
                'create', 'update', 'perform_update', 'partial_update'
        ):
            return ContentUpdateModelSerializer
        return ContentModelSerializer


class CategoryApiView(viewsets.ModelViewSet):
    """
    API endpoint for Categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)


class FeedbackApiView(viewsets.ModelViewSet):
    """
    API endpoints for giving Feedback on Posts by Editor, Admin users.
    Reporter is allowed only for `SAFE METHODS`

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PUT` => Feedback owner only
        `PATCH` => Feedback owner only
        `DELETE` => Feedback owner only
    """

    authentication_classes = (TokenAuthentication,)
    queryset = Feedback.objects.all()
    permission_classes = (perm.FeedbackPermission,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return FeedbackGetSerializer
        return FeedbackSerializer


class PostIdentifierApiView(viewsets.ModelViewSet):
    """
    API endpoints for working on PostIdentifier ( keyword )

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PATCH` => Staff user
        `PATCH` => Staff user
        `DELETE` => Staff user
    """

    authentication_classes = (TokenAuthentication,)
    queryset = PostIdentifier.objects.all()
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = PostIdentifierSerializer


class PostLikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly API endpoint for working on "Likes" given to Posts

    Allowed requests:
        `GET` => Staff user
    """
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)


class PostDislikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly API endpoint for working on "Dislikes" given to Posts

    Allowed requests:
        `GET` => Admin user
    """

    queryset = PostDislike.objects.all()
    serializer_class = PostDislikeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)


class CommentApiViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Comments.
    All admin user can get and delete comments
    Update, Create methods are not allowed to anyone

    Allowed requests:
        `GET` => Staff user
        `POST` => Nobody
        `PUT` => Nobody
        `PATCH` => Nobody
        `DELETE` => Admin user
    """

    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication,)
    queryset = Comment.objects.all()

    def get_permissions(self):
        permission_classes = []
        if self.action in ('retrieve', 'list'):
            permission_classes = (permissions.IsAdminUser,)
        elif self.action == 'destroy':
            permission_classes = (perm.IsCustomAdminUser,)
        return [permission() for permission in permission_classes]


class CommentLikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly API endpoint for working on "Likes" given to Comments

    Allowed requests:
        `GET` => Staff user
    """

    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)


class CommentDislikeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly API endpoint for working on "Dislikes" given to Comments

    Allowed requests:
        `GET` => Staff user
    """

    queryset = CommentDislike.objects.all()
    serializer_class = CommentDislikeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)


class OptionsApiView(viewsets.ReadOnlyModelViewSet):
    """
        Readonly API endpoint for working on "Dislikes" given to Comments

        Allowed requests:
            `GET` => Staff user
        """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    @swagger_auto_schema(
        operation_description='Allow update the post by reporter, '
                              'if the post has not been published. \n'

                              'Response: \n'
                              ' `201` => CREATED\n'
                              ' `401` => Unauthenticated user\n'
                              ' `403` => Not Staff user or is Reporter user\n'
                              ' `400` => Invalid data\n'
    )
    @action(detail=False, methods=['get'],
            url_name='post-options',
            url_path='/options')
    def options(self, request, *args, **kwargs):
        return Response(
            {
                'NEWS_STATUS': NEWS_STATUS,
                'TOP_NEWS': TOP_NEWS,
                'TITLE_TYPES': TITLE_TYPES,
                'CONTENT_TYPES': CONTENT_TYPES
            },
            status=status.HTTP_200_OK,
        )
