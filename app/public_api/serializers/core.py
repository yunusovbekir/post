from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from core.models import Settings, SocialMedia, ContactForm, Opinion
from ..utils.utils import name_validation


class PublicSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Settings
        fields = '__all__'
        read_only_fields = (
            'id',
        )


class PublicSocialMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialMedia
        fields = "__all__"
        read_only_fields = (
            'id',
        )


class PublicContactFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactForm
        fields = "__all__"
        read_only_fields = (
            "id",
            "send_date",
        )

    def validate(self, attrs):
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        message = attrs.get('message')

        name_validation(
            value=first_name,
            error_message_1=_('Adınızı daxil edin'),
            error_message_2=_('Adınızı düzgün daxil edin'),
        )
        name_validation(
            value=last_name,
            error_message_1=_('Soyadınızı daxil edin'),
            error_message_2=_('Soyadınızı düzgün daxil edin'),
        )
        if not message:
            raise ValidationError(_(
                'Mesajınızı daxil edin'
            ))
        return attrs


class PublicOpinionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Opinion
        fields = "__all__"
        read_only_fields = (
            "id",
            "send_date",
        )

    def validate(self, attrs):
        first_name = attrs.get('first_name')
        last_name = attrs.get('last_name')
        message = attrs.get('message')

        name_validation(
            value=first_name,
            error_message_1=_('Adınızı daxil edin'),
            error_message_2=_('Adınızı düzgün daxil edin'),
        )
        name_validation(
            value=last_name,
            error_message_1=_('Soyadınızı daxil edin'),
            error_message_2=_('Soyadınızı düzgün daxil edin'),
        )
        if not message:
            raise ValidationError(_(
                'Mesajınızı daxil edin'
            ))
        return attrs
