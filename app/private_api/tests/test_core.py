import io
import os
import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from core.models import Settings, SocialMedia, ContactForm
from PIL import Image
from ..serializers.core import ContactFormSerializer

USER = get_user_model()
BASE_DIR = settings.BASE_DIR
PATH = os.path.join(BASE_DIR, 'private_api/tests/default.png')
SOCIALMEDIA_LIST_URL = reverse("private_api:socialmedia-list")

"""
TESTED ENDPOINTS:
    Settings => SettingsAPIView
    Social Media => SocialMediaAPIView
    Contact Form => ContactFormAPITest
"""

MEDIA_ROOT = tempfile.mkdtemp()


def create_user(**payload):
    return USER.objects.create(**payload)


def create_social_media(**data):
    return SocialMedia.objects.create(**data)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SettingsApiTests(APITestCase):
    """
    Testing Settings requests with 3 different users

    basic user => 401 Unauthenticated
    logged user => 403 Forbidden
    logged staff user => 200 OK
    """

    def setUp(self):
        user_data = {
            "email": "test@user.az",
            "first_name": "Test",
            "last_name": "User"
        }
        self.user = create_user(**user_data)

        self.settings_data = {
            "copyright": "Lorem ipsum",
            "footer_social_media_text": "Lorem ipsum",
            "search_placeholder": "Lorem ipsum",
            "author_widget_title": "Lorem ipsum",
            "slider_video_title": "Lorem ipsum",
            "slider_button_title": "Lorem ipsum",
            "item_now_playing_text": "Lorem ipsum",
            "terms_and_conditions": "Lorem ipsum",
        }
        self.settings = Settings.objects.create(**self.settings_data)
        self.url_list = reverse('private_api:settings-api-list')
        self.url_detail = reverse(
            'private_api:settings-api-detail',
            kwargs={'pk': self.settings.id}
        )

        # create temporary image
        image = Image.new('RGB', (100, 100))
        self.tmp_img = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(self.tmp_img)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_settings_list_request(self):
        """
        Testing list request with 3 different users:
        """

        client = APIClient()
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_settings_retrieve_request(self):
        """
        Testing retrieve request with 3 different users
        """

        client = APIClient()
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_settings_create_request(self):
        """
        Testing create request with 3 different users
        """
        client = APIClient()
        with open(self.tmp_img.name, 'rb') as file:
            self.settings_data['logo'] = file
            response = client.post(
                self.url_list,
                data=self.settings_data,
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        with open(self.tmp_img.name, 'rb') as file:
            self.settings_data['logo'] = file
            response = client.post(
                self.url_list,
                data=self.settings_data,
                format='multipart'
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        with open(self.tmp_img.name, 'rb') as file:
            self.settings_data['logo'] = file
            response = client.post(
                self.url_list,
                data=self.settings_data,
                format='multipart'
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        with open(self.tmp_img.name, 'rb') as file:
            self.settings_data['logo'] = file
            response = client.post(
                self.url_list,
                data=self.settings_data,
                format='multipart'
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        with open(self.tmp_img.name, 'rb') as file:
            self.settings_data['logo'] = file
            response = client.post(
                self.url_list,
                data=self.settings_data,
                format='multipart'
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_settings_update_request(self):
        """
         Testing update, partial_update request with 3 different users
        """
        client = APIClient()

        new_data = {
            "copyright": "Lorem",
            "footer_social_media_text": "Lorem",
            "search_placeholder": "Lorem",
            "author_widget_title": "Lorem",
            "slider_video_title": "Lorem",
            "slider_button_title": "Lorem",
            "item_now_playing_text": "Lorem",
            "terms_and_conditions": "Lorem"
        }

        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            put_response = client.put(
                self.url_detail,
                data=new_data,
                format='multipart'
            )

        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            patch_response = client.patch(
                self.url_detail,
                data=new_data,
                format='multipart'
            )
        self.assertEqual(
            put_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            patch_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        client.force_authenticate(user=self.user)
        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            put_response = client.put(
                self.url_detail,
                data=new_data,
                format='multipart'
            )

        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            patch_response = client.patch(
                self.url_detail,
                data=new_data,
                format='multipart'
            )
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            patch_response.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.is_staff = True

        self.user.user_type = 2
        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            put_response = client.put(
                self.url_detail,
                data=new_data,
                format='multipart'
            )

        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            patch_response = client.patch(
                self.url_detail,
                data=new_data,
                format='multipart'
            )
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            put_response = client.put(
                self.url_detail,
                data=new_data,
                format='multipart'
            )

        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            patch_response = client.patch(
                self.url_detail,
                data=new_data,
                format='multipart'
            )
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            put_response = client.put(
                self.url_detail,
                data=new_data,
                format='multipart'
            )

        with open(self.tmp_img.name, 'rb') as file:
            new_data['logo'] = file
            patch_response = client.patch(
                self.url_detail,
                data=new_data,
                format='multipart'
            )
        self.assertEqual(
            put_response.data.get('copyright'),
            new_data.get('copyright')
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            patch_response.data.get('copyright'),
            new_data.get('copyright')
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SocialMediaAPITest(TestCase):

    def generate_photo_file(self):

        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def setUp(self):
        payload = {
            "email": "test@testing.com",
            "password": "sdhd62863%&fcd",
            "first_name": "test first name",
            "last_name": "test last name",
        }
        self.user = create_user(**payload)
        self.user.set_password(payload["password"])
        self.user.save()

        social_data = {
            "title": "test_category",
            "link": "https://www.facebook.com/",
            "position": "Header",
            "icon": self.generate_photo_file().name
        }

        self.social = create_social_media(**social_data)
        self.social.save()
        self.url_detail = reverse(
            'private_api:socialmedia-detail',
            kwargs={'pk': self.social.id}
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_api_returns_social_media_list_to_only_admin_users(self):

        client = APIClient()
        response = client.get(SOCIALMEDIA_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.get(SOCIALMEDIA_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response = client.get(SOCIALMEDIA_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        response = client.get(SOCIALMEDIA_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        response = client.get(SOCIALMEDIA_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_returns_socialmedia_retrieve_to_only_adminusers(self):

        client = APIClient()
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_adminusers_can_update(self):

        client = APIClient()
        response = client.patch(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.patch(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response = client.patch(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        response = client.patch(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        response = client.patch(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_adminusers_can_delete(self):

        client = APIClient()
        response = client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response = client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        response = client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        response = client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ContactFormAPITest(APITestCase):
    """
    Testing Contact Form Read only API
    Basic user => 401 Unauthenticated
    Logged use => 403 Forbidden
    Staff user => 200 OK / 405 Method is not allowed
    """

    def setUp(self):
        payload = {
            "email": "test@testing.com",
            "password": "sdhd62863%&fcd",
            "first_name": "test first name",
            "last_name": "test last name",
        }
        self.user = create_user(**payload)
        self.user.set_password(payload["password"])
        self.user.save()

        contact_form_data = {
            "first_name": "first name",
            "last_name": "last name",
            "email": "test@testing.com",
            "message": "this is test message"
        }

        self.contact = ContactForm.objects.create(**contact_form_data)

        self.new_data = {
            "first_name": "test",
            "last_name": "test",
            "email": "test@test.az",
            "message": "this is test message"
        }
        self.url_list = reverse("private_api:contact-form-list")
        self.url_detail = reverse("private_api:contact-form-detail",
                                  kwargs={'pk': self.contact.id})

    def test_api_returns_contact_form_list_to_only_admin_users(self):
        serializer = ContactFormSerializer(
            ContactForm.objects.all(),
            many=True
        )
        client = APIClient()
        response = client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response_auth = client.get(self.url_list)

        self.assertEqual(response_auth.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response_staff_reporter = client.get(self.url_list)
        self.assertEqual(
            response_staff_reporter.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.user_type = 3
        response_staff_editor = client.get(self.url_list)
        self.assertEqual(
            response_staff_editor.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.user_type = 4
        response_staff_admin = client.get(self.url_list)
        self.assertEqual(response_staff_admin.data, serializer.data)
        self.assertEqual(response_staff_admin.status_code, status.HTTP_200_OK)

    def test_api_returns_contact_form_retrieve_to_only_admin_users(self):
        serializer = ContactFormSerializer(
            ContactForm.objects.all()[0]
        )
        client = APIClient()
        response = client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response_auth = client.get(self.url_detail)

        self.assertEqual(response_auth.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response_staff_reporter = client.get(self.url_detail)
        self.assertEqual(
            response_staff_reporter.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.user_type = 3
        response_staff_editor = client.get(self.url_detail)
        self.assertEqual(
            response_staff_editor.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.user_type = 4
        response_staff_admin = client.get(self.url_detail)
        self.assertEqual(response_staff_admin.data, serializer.data)
        self.assertEqual(response_staff_admin.status_code, status.HTTP_200_OK)

    def test_delete_not_allowed(self):

        client = APIClient()
        response = client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response_auth = client.delete(self.url_detail)
        self.assertEqual(response_auth.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response_staff_reporter = client.delete(self.url_detail)
        self.assertEqual(
            response_staff_reporter.status_code, status.HTTP_403_FORBIDDEN
        )
        self.user.user_type = 3
        response_staff_editor = client.delete(self.url_detail)
        self.assertEqual(
            response_staff_editor.status_code, status.HTTP_403_FORBIDDEN
        )
        self.user.user_type = 4
        response_staff_admin = client.delete(self.url_detail)
        self.assertEqual(
            response_staff_admin.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_update_not_allowed(self):
        client = APIClient()
        put_response = client.put(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        patch_response = client.patch(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        client.force_authenticate(user=self.user)
        put_response_auth = client.put(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        patch_response_auth = client.patch(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        self.assertEqual(
            put_response_auth.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            patch_response_auth.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.is_staff = True
        self.user.user_type = 2
        put_response_staff_reporter = client.put(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        patch_response_staff_reporter = client.patch(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        self.assertEqual(
            put_response_staff_reporter.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            patch_response_staff_reporter.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.user.user_type = 3
        put_response_staff_editor = client.put(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        patch_response_staff_editor = client.patch(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        self.assertEqual(
            put_response_staff_editor.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            patch_response_staff_editor.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.user_type = 4
        put_response_staff_admin = client.put(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        patch_response_staff_admin = client.patch(
            self.url_detail,
            data=self.new_data,
            format="json"
        )
        self.assertEqual(
            put_response_staff_admin.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            patch_response_staff_admin.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )
