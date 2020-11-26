from rest_framework import serializers
from core.models import Settings, SocialMedia, ContactForm


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = "__all__"
        read_only_fields = (
            'id',
        )


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = "__all__"


class ContactFormSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContactForm
        fields = "__all__"
