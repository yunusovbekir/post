from django.contrib.auth import get_user_model

from rest_framework import generics, status, viewsets, permissions, pagination
from rest_framework.response import Response

from knox.models import AuthToken
from knox.auth import TokenAuthentication

from user.models import AuthorSocialMediaAccounts
from ..serializers.user import (
    PrivateUserSerializer,
    LoginSerializer,
    UserRegisterSerializer,
    UserSerializerForSuperuser,
    AuthorSocialMediaAccountsSerializer,
    AuthorSocialMediaAccountsCreateSerializer
)
from ..permissions import (
    IsOwner,
    IsProfileOwnerOrCustomAdminUser,
    IsCustomAdminUser,
)

User = get_user_model()


class ExamplePagination(pagination.PageNumberPagination):
    page_size = 10


class ChoiceApiView(generics.ListAPIView):
    def get(self, *args, **kwargs):
        role = [[1, 'User'], [2, 'Reporter'], [3, 'Editor'], [4, 'Admin']]
        status = [[True, 'Active'], [False, 'Inactive']]
        return Response({
            "role": role,
            "status": status
        })


class PrivateUserApiView(viewsets.ModelViewSet):
    """
    API endpoint for `retrieve`, `update` and `delete` users.
    In order to add/update `saved news` or `preferred categories`, pass `ID`s

    Allowed requests:
        `GET` => Staff user
        `PUT` => Owner or Admin user
        `PATCH` => Owner or Admin user
        `DELETE` => Owner or Admin user
    """
    queryset = User.objects.all().order_by('first_name')
    authentication_classes = (TokenAuthentication,)
    pagination_class = ExamplePagination

    def get_serializer_class(self, *args, **kwargs):
        if self.request.user.user_type == 4:
            return UserSerializerForSuperuser
        return PrivateUserSerializer

    def list(self, request, *args, **kwargs):

        serializer = self.get_serializer_class()
        page = self.paginate_queryset(self.queryset)
        serialized_data = serializer(page, many=True)

        return self.get_paginated_response(serialized_data.data)

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            permission_classes = (IsProfileOwnerOrCustomAdminUser,)
        else:
            permission_classes = (permissions.IsAdminUser,)
        return [permission() for permission in permission_classes]


class PrivateUserLoginAPIView(generics.CreateAPIView):
    """
    API endpoint for `Login View` on admin site. `Only Staff` users can log in

    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        data = LoginSerializer(
            user,
            context=self.get_serializer_context()
        ).data
        return Response(
            {
                "user": data,
                "token": AuthToken.objects.create(user=user)[1]
            },
            status=status.HTTP_200_OK
        )


class PrivateUserAddAPIView(generics.CreateAPIView):
    """ API endpoint for adding user. Only Admin user can add a user """

    serializer_class = UserRegisterSerializer
    queryset = User.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsCustomAdminUser,)


class AuthorSocialMediaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Social Media Accounts of Website's Authors.
    Author field for `POST`, `PUT`, `PATCH` request methods is hidden.
    Request user will be passed to the field automatically.

    Allowed requests:
        `GET` => Staff user
        `POST` => Staff user
        `PUT` => Owner only
        `PATCH` => Owner only
        `DELETE` => Owner only

    """

    authentication_classes = (TokenAuthentication,)
    queryset = AuthorSocialMediaAccounts.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return AuthorSocialMediaAccountsCreateSerializer
        else:
            return AuthorSocialMediaAccountsSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create',):
            permission_classes = (permissions.IsAdminUser,)
        else:
            permission_classes = (IsOwner,)
        return [permission() for permission in permission_classes]
