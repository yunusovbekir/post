from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth import get_user_model
from user.models import AuthorSocialMediaAccounts
from .news import PublicPostListModelSerializer

User = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'avatar',
            'phone_number',
            'saved_news',
            'preferred_categories',
        )

        read_only_fields = (
            'email',
        )

    def update(self, instance, validated_data):
        if validated_data.get('preferred_categories'):
            categories = validated_data.pop('preferred_categories')
            instance.preferred_categories.clear()
            for each in categories:
                instance.preferred_categories.add(each)

        if validated_data.get('saved_news'):
            saved_news = validated_data.pop('saved_news')
            instance.saved_news.clear()
            for each in saved_news:
                instance.saved_news.add(each)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class PublicUserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        allow_blank=False,
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password',
            'confirm_password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """
        Password must contain at least 6 character + one digit
        """
        password = attrs.get('password')
        password_validation.validate_password(password)

        if password != attrs.pop('confirm_password'):
            raise serializers.ValidationError(_(
                'The two password fields didn’t match.'
            ))

        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError(_(
                'Password must contain at 1 least  digit.'
            ))
        if not len([char for char in password if char.isalpha()]) >= 6:
            raise serializers.ValidationError(_(
                'Password must contain at least 6 letter.'
            ))

        if not attrs.get('first_name'):
            raise serializers.ValidationError(_(
                'First name is required',
            ))

        if not attrs.get('last_name'):
            raise serializers.ValidationError(_(
              'Last name is required',
            ))
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PublicUserPasswordResetSerializer(serializers.Serializer):
    """
    Public User Password Reset Serializer
    """
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_new_password = serializers.CharField(write_only=True,
                                                 required=True)

    def validate(self, attrs):
        user = self.context.get('request').user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        # check old password is True
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                {'old_password': _('Your old password was entered incorrectly.'
                                   ' Please enter it again.')}
            )

        # check new password and confirm new password matches
        if new_password != confirm_new_password:
            raise serializers.ValidationError(
                {'password': _("The two password fields didn't match.")}
            )

        # validate new password
        password_validation.validate_password(new_password, user)

        return attrs

    def save(self, **kwargs):
        new_password = self.validated_data.get('new_password')
        user = self.context.get('request').user
        user.set_password(new_password)
        user.save()
        return user


class PublicUserLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user:
            return user
        raise serializers.ValidationError(_(
            'Incorrect credentials'
        ))


class DefaultUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
        )


class PublicAuthorSocialMediaAccountSerializer(serializers.ModelSerializer):
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


class PublicAuthorProfileSerializer(serializers.ModelSerializer):
    post = PublicPostListModelSerializer(source='post_author', many=True)
    social_media = PublicAuthorSocialMediaAccountSerializer(
        source='social_account',
        many=True
    )

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'user_type',
            'profession',
            'first_name',
            'last_name',
            'avatar',
            'phone_number',
            'email',
            'social_media',
            'post',
        )
