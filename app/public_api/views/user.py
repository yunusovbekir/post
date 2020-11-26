from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.settings import api_settings
from rest_framework import generics, status
from rest_framework.response import Response

from knox.models import AuthToken
from knox.auth import TokenAuthentication

from news.models import Post
from ..serializers.news import PublicPostListModelSerializer

from ..serializers.user import (
    PublicUserLoginSerializer,
    PublicUserRegisterSerializer,
    PublicUserSerializer,
    PublicUserPasswordResetSerializer,
    PublicAuthorProfileSerializer,
)

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


User = get_user_model()


class PublicUserListAPIView(generics.ListAPIView):
    """
    Public API endpoint for getting a list of `Public` Users
    """
    queryset = User.objects.filter(is_active=True, is_staff=False)
    serializer_class = PublicUserSerializer
    permission_classes = (AllowAny,)


class PublicUserLoginView(generics.CreateAPIView):
    """
    Public API endpoint for `Login View` on website.

    """

    serializer_class = PublicUserLoginSerializer
    authentication_classes = (TokenAuthentication,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        data = PublicUserLoginSerializer(
            user,
            context=self.get_serializer_context()
        ).data
        response_data = {
            'user': data,
            'token': AuthToken.objects.create(user=user)[1]
        }
        return Response(response_data, status=status.HTTP_200_OK)


class PublicUserRegisterAPIView(generics.CreateAPIView):
    """
    Public API endpoint for `Register View` on the website.
    """
    serializer_class = PublicUserRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = PublicUserRegisterSerializer(
            user,
            context=self.get_serializer_context(),
        ).data
        response_data = {
            'user': data,
            'token': AuthToken.objects.create(user=user)[1]
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class PublicUserPasswordResetAPIView(generics.UpdateAPIView):
    """
    Public API endpoint for `Password Reset View` on the website.

    """
    serializer_class = PublicUserPasswordResetSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "message": _("Password reset request was successful"),
                },
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class PublicUserProfileAPIView(viewsets.ModelViewSet):
    """
    Public API endpoint for `Profile View`.

    In order to save add `saved news` and `preferred categories`,
    pass the `ID`s to the appropriate fields.

    Allowed requests:
        `GET` => Anyone
        `PATCH` => Owner only

    """
    serializer_class = PublicUserSerializer
    authentication_classes = (TokenAuthentication,)

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        return Response(
            {
                'message': _('Login required'),
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    def update(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True,
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "data": serializer.data,
                        "message": "Profile update request was successful"
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                'message': _('Login required'),
            },
            status=status.HTTP_401_UNAUTHORIZED
        )


class AuthorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Readonly Public API endpoint for getting Author's data.
    `Author Profile View`
    """
    serializer_class = PublicAuthorProfileSerializer
    queryset = get_user_model().objects.filter(is_active=True, is_staff=True)
    permission_classes = (AllowAny,)


def get_page(request, queryset):
    paginator = Paginator(queryset, 4)
    page = request.GET.get('page') if request.GET.get('page') else 1
    data = paginator.get_page(page)
    return paginator, data


class PublicAuthorPostsAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    def get(self, *args, **kwargs):
        author = get_user_model().objects.get(id=self.kwargs["pk"])
        queryset = Post.objects.filter(
            status='Open',
            is_approved=True,
            author=author
        ).filter(Q(end_date__gte=timezone.now()) | Q(end_date=None))

        paginator, data = get_page(self.request, queryset)

        serializers = PublicPostListModelSerializer(
            data, context={"request": self.request}, many=True
        )
        response = {
            "data": serializers.data,
            "pages": paginator.num_pages,
            "current_page": data.number,
        }

        return JsonResponse(response, safe=False)


class PublicUserSavedPostsAPIView(generics.ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:

            queryset = self.request.user.saved_news.all()

            if 'category' in self.request.GET and self.request.GET['category']:
                category = self.request.GET['category']
                queryset = queryset.filter(category__in=[category])

            paginator, data = get_page(self.request, queryset)

            serializers = PublicPostListModelSerializer(
                data, context={"request": self.request}, many=True
            )
            response = {
                "data": serializers.data,
                "pages": paginator.num_pages,
                "current_page": data.number,
            }

            return JsonResponse(response, safe=False)
