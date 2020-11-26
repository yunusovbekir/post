from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..serializers.user import UserRegisterSerializer

"""
TESTED ENDPOINTS:
    1. PrivateUserRegisterAPIView => PrivateUserRegisterApiTests
    2. PrivateUserLoginAPIView => PrivateUserLoginApiTests
    3. PrivateUserListAPIView => PrivateUserListApiTest
    4. PrivateUserRetrieveUpdateAPIView => ??
    5. AuthorSocialMediaViewSet => ??
"""

USER = get_user_model()
CREATE_USER_URL = reverse('private_api:user-register')
LOGIN_URL = reverse('private_api:user-login')
USER_LIST_URL = reverse('private_api:private-user-api-list')


def create_user(**data):
    return USER.objects.create_user(**data)


class PrivateUserRegisterApiTests(TestCase):
    """ Private User Register API Test Cases """

    def setUp(self):
        user_data = {
            "email": "admin@test.az",
        }
        self.user = create_user(**user_data)

    def test_create_user_valid_credentials(self):
        """
        Testing create user with valid credentials
        Testing response data does not contain either plain or hashed password
        Testing response data contains `token`
        """

        payload = {
            "email": "bekir@labrin.tech",
            "password": "admin@12345%",
            "confirm_password": "admin@12345%",
            "first_name": "test first name",
            "last_name": "test last name"
        }

        client = APIClient()
        response = client.post(
            path=CREATE_USER_URL,
            format='json',
            data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(
            path=CREATE_USER_URL,
            format='json',
            data=payload
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.user_type = 2
        response = client.post(
            path=CREATE_USER_URL,
            format='json',
            data=payload
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 3
        response = client.post(
            path=CREATE_USER_URL,
            format='json',
            data=payload
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.user_type = 4
        response = client.post(
            path=CREATE_USER_URL,
            format='json',
            data=payload
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

    def test_create_user_first_name_required(self):
        """
        Testing `First Name` field is required
        Testing both serializer and API View
        """

        payload = {
            "email": "test@test.az",
            "password": "admin@12345%",
            "confirm_password": "admin@12345%",
            'first_name': "",
            "last_name": "test last name",
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.user.is_staff = True
        self.user.user_type = 4

        response = client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )

        serializer = UserRegisterSerializer(data=payload)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_last_name_required(self):
        """
        Testing `First Name` field is required
        Testing both serializer and API View
        """

        payload = {
            "email": "test@test.az",
            "password": "admin@12345%",
            "confirm_password": "admin@12345%",
            'first_name': "test fist name",
            "last_name": "",
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.user.is_staff = True
        self.user.user_type = 4

        response = client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )

        serializer = UserRegisterSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(serializer.is_valid(), False)

    def test_create_user_short_password(self):
        """
        Testing short password functionality
        Testing both serializer and API View
        """

        payload = {
            "email": "test@test.az",
            "password": "admin",
            "confirm_password": "admin",
            'first_name': "test fist name",
            "last_name": "test last name",
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.user.is_staff = True
        self.user.user_type = 4

        response = client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )

        serializer = UserRegisterSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(serializer.is_valid(), False)

    def test_password_dont_match(self):
        """
        Testing two password fields do not match
        when incorrect data is provided
        """
        payload = {
            "email": "test@test.az",
            "password": "admin@12345%",
            "confirm_password": "admin@1235",
            'first_name': "test fist name",
            "last_name": "test last name",
        }

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.user.is_staff = True
        self.user.user_type = 4

        response = client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )
        serializer = UserRegisterSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(serializer.is_valid(), False)

    def test_user_already_exists(self):
        """
        Testing user already exists
        """
        payload = {
            "email": "bekir@labrin.tech",
            "password": "admin@12345%",
            "first_name": "test first name",
            "last_name": "test last name",
        }
        create_user(**payload)

        client = APIClient()
        client.force_authenticate(user=self.user)
        self.user.is_staff = True
        self.user.user_type = 4

        response = client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserLoginApiTests(TestCase):
    """
    Private User Login API Test Cases
    """

    def setUp(self):
        payload = {
            "email": "bekir.y@labrin.tech",
            "password": "admin@12345%",
            "first_name": "test first name",
            "last_name": "test last name",
            "is_staff": "True"
        }
        create_user(**payload)

    def test_successful_login(self):
        """
        Testing successful login with valid credentials

        """
        payload = {
            "email": "bekir.y@labrin.tech",
            "password": "admin@12345%",
        }

        response = self.client.post(
            path=LOGIN_URL,
            content_type='application/json',
            data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_incorrect_credentials(self):
        payload = {
            "email": "test@test.test",
            "password": "admin@12345%"
        }

        response = self.client.post(
            path=LOGIN_URL,
            content_type='application/json',
            data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_admin_user_allowed(self):
        payload = {
            "email": "basic_user@gmail.com",
            "password": "admin@12345%",
            "first_name": "test first name",
            "last_name": "test last name",
        }
        create_user(**payload)

        response = self.client.post(
            path=LOGIN_URL,
            content_type='application/json',
            data=payload
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTest(APITestCase):
    """
    Private User API Test Cases
    """

    def setUp(self):
        """
        Setting up data to testing
        Creating 2 staff users, 1 basic user
        """
        user_1 = {
            "email": "user1@mail.com",
            "first_name": "staff first name 1",
            "last_name": "staff last name 1",
            "is_staff": True
        }

        user_2 = {
            "email": "user2@mail.com",
            "first_name": "staff first name 2",
            "last_name": "staff last name 2",
            "is_staff": True
        }

        user_3 = {
            "email": "user3@mail.com",
            "first_name": "basic first name 1",
            "last_name": "basic last name 1",
        }

        payload = {
            "email": "request@user.me",
            "first_name": "bekir",
            "last_name": "yunusov",
        }
        self.user = create_user(**payload)

        create_user(**user_1)
        create_user(**user_2)
        create_user(**user_3)

    def test_private_user_list_request(self):
        """
        Testing Private API endpoint getting list of all users
        """

        user_count = USER.objects.count()

        client = APIClient()
        response = client.get(USER_LIST_URL)

        # unauthorized user
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # login with user
        client.force_authenticate(user=self.user)
        response = client.get(USER_LIST_URL)

        # authorized user
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        response = client.get(USER_LIST_URL)

        # staff user
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data.get('results')), user_count)
