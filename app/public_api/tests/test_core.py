from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..serializers.core import (
    PublicSettingsSerializer,
    PublicSocialMediaSerializer,
)
from core.models import Settings, SocialMedia

"""
TESTED ENDPOINTS:
    1. SettingsAPIView => SettingsApiTests
    1. SocialMediaListAPIView => SocailMediaApiTests
    1. ContactFormCreateAPIView => ContactFormApiTests

"""

SETTINGS_URL = reverse('public_api:settings')
SOCIAL_MEDIA_URL = reverse('public_api:social')
CONTACT_FORM_URL = reverse('public_api:contact-form')


def create_settings(**payload):
    return Settings.objects.create(**payload)


def create_social_media(**payload):
    return SocialMedia.objects.create(**payload)


class SettingsApiTests(APITestCase):
    """
    Testing Settings endpoint
    """

    def setUp(self):
        payload = {
            'copyright': '© 2020 News Website developed by Yunusov',
            'terms_and_conditions': 'text for testing'
        }
        self.settings_model = create_settings(**payload)

    def test_settings_api(self):
        # test serializer
        serializer = PublicSettingsSerializer(
            Settings.objects.all(), many=True
        )
        # test view
        response = self.client.get(SETTINGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class SocailMediaApiTests(APITestCase):
    """
    Testing Social Media Accounts endpoints
    """

    def setUp(self):
        facebook_data = {
            'title': 'Facebook',
            # 'icon': 'icon.png',
            'link': 'facebook.com',
            'position': 'Header'
        }
        instagram_data = {
            'title': 'Instagram',
            # 'icon': 'icon.png',
            'link': 'instagram.com',
            'position': 'Footer'
        }
        self.facebook = create_social_media(**facebook_data)
        self.instagram = create_social_media(**instagram_data)

    def test_social_media(self):
        serializer = PublicSocialMediaSerializer(
            SocialMedia.objects.all(),
            many=True
        )
        response = self.client.get(SOCIAL_MEDIA_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class ContactFormApiTests(APITestCase):
    """ Testing Contact Form """

    def test_contact_form_successful(self):
        payload = {
            "first_name": "user user",
            "last_name": "guest",
            "email": "user@test.az",
            "message": "This is testing",
        }

        response = self.client.post(
            path=CONTACT_FORM_URL,
            data=payload,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('send_date', response.data)

    def test_invalid_first_name(self):
        payload = {
            "first_name": "user1234",
            "last_name": "last",
            "email": "user@test.az",
            "message": "This is testing"
        }

        response = self.client.post(
            path=CONTACT_FORM_URL,
            data=payload
        )
        self.assertEqual(
            response.data.get('non_field_errors')[0],
            'Adınızı düzgün daxil edin'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_last_name(self):
        payload = {
            "first_name": "user",
            "last_name": "last123",
            "email": "user@test.az",
            "message": "This is testing"
        }

        response = self.client.post(
            path=CONTACT_FORM_URL,
            data=payload
        )
        self.assertEqual(
            response.data.get('non_field_errors')[0],
            'Soyadınızı düzgün daxil edin'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        payload = {
            "first_name": "user",
            "last_name": "last",
            "email": "user@az",
            "message": "This is testing"
        }

        response = self.client.post(
            path=CONTACT_FORM_URL,
            data=payload
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_message(self):
        payload = {
            "first_name": "user",
            "last_name": "last",
            "email": "user@az",
            "message": ""
        }

        response = self.client.post(
            path=CONTACT_FORM_URL,
            data=payload
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
