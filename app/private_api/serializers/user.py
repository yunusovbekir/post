from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from user.models import AuthorSocialMediaAccounts


User = get_user_model()


class PrivateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = (
            'password',
            'user_permissions',
            'groups',
            'is_superuser',
        )
        read_only_fields = (
            'id',
            'is_staff',
            'date_joined',
            'last_login',
        )
        depth = 1


class UserSerializerForSuperuser(serializers.ModelSerializer):
    role_name = serializers.ReadOnlyField(source='user_type_name')

    class Meta:
        model = User
        exclude = (
            'password',
            'groups',
            'is_superuser',
        )
        read_only_fields = (
            'id',
            'date_joined',
            'last_login',
        )


class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        allow_blank=False,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'confirm_password',
            'first_name',
            'last_name',
            'avatar',
            'user_type',
            'is_staff',
            'is_superuser',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }
        read_only_fields = (
            'id',
        )

    def validate(self, attrs):
        if not attrs.get('first_name'):
            raise serializers.ValidationError(_(
                'First name is required.'
            ))

        if not attrs.get('last_name'):
            raise serializers.ValidationError(_(
                'Last name is required.'
            ))

        password_validation.validate_password(attrs.get('password'))

        if attrs.get('password') != attrs.pop('confirm_password'):
            raise serializers.ValidationError(_(
                'The two password fields didn’t match.'
            ))
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.get('email')
        first_name = validated_data.get('first_name')
        last_name = validated_data.get('last_name')
        avatar = validated_data.get('avatar')
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            avatar=avatar,

        )
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.CharField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    user_type = serializers.CharField(required=False)
    avatar = serializers.CharField(required=False)

    def validate(self, data):
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError('Incorrect credentials')
        if not user.is_staff:
            raise serializers.ValidationError('You are not allowed to login')
        return user


class AuthorSocialMediaAccountsSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthorSocialMediaAccounts
        fields = (
            'id',
            'author',
            'social_media',
            'url',
        )
        read_only_fields = (
            'id',
            'author',
        )


class AuthorSocialMediaAccountsCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AuthorSocialMediaAccounts
        fields = (
            'author',
            'social_media',
            'url',
        )
