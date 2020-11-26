from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from ..serializers.user import PublicUserRegisterSerializer
from news.models import Post, Category
from user.models import AuthorSocialMediaAccounts

USER = get_user_model()
CREATE_USER_URL = reverse('public_api:user-register')
LOGIN_URL = reverse('public_api:user-login')


def create_user(**data):
    return USER.objects.create_user(**data)


class PublicUserRegisterApiTests(APITestCase):
    """ Public User Test Cases """

    def test_create_user_valid_credentials(self):
        """
        Test create user with valid credentials
        Test response data does not contain neither plain nor hashed password
        Test response data contains `token`
        """

        payload = {
            "email": "bekir@labrin.tech",
            "first_name": "Test",
            "last_name": "User",
            "password": "usertest@12345%",
            "confirm_password": "usertest@12345%",
        }
        response = self.client.post(
            path=CREATE_USER_URL,
            data=payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        self.assertIn('token', response.data)

    def test_create_user_short_password(self):
        """
        Test short password functionality
        Test both serializer and API View
        """

        payload = {
            "email": "test@test.az",
            "first_name": "Test",
            "last_name": "User",
            "password": "user",
            "confirm_password": "user",
        }

        response = self.client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )

        serializer = PublicUserRegisterSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(serializer.is_valid(), False)

    def test_password_dont_match(self):
        """
        Test two password fields do not match when incorrect data is provided
        """
        payload = {
            "email": "test@test.az",
            "first_name": "Test",
            "last_name": "User",
            "password": "usertest@12345%",
            "confirm_password": "usertest@1235",
        }

        response = self.client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )
        serializer = PublicUserRegisterSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(serializer.is_valid(), False)

    def test_user_already_exists(self):
        """
        Test user already exists
        """
        create_user_data = {
            "email": "bekir@labrin.tech",
            "first_name": "Test",
            "last_name": "User",
            "password": "usertest@12345%",
        }
        post_request_data = {
            "email": "bekir@labrin.tech",
            "first_name": "Test",
            "last_name": "User",
            "password": "usertest@12345%",
            "confirm_data": "usertest@12345%"
        }
        create_user(**create_user_data)
        response = self.client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=post_request_data
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_first_name_is_required(self):

        payload = {
            "email": "test@test.az",
            "last_name": "User",
            "password": "user",
            "confirm_password": "user",
        }

        response = self.client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )

        serializer = PublicUserRegisterSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(serializer.is_valid(), False)

    def test_last_name_is_required(self):
        payload = {
            "email": "test@test.az",
            "first_name": "User",
            "password": "user",
            "confirm_password": "user",
        }

        response = self.client.post(
            path=CREATE_USER_URL,
            content_type='application/json',
            data=payload
        )

        serializer = PublicUserRegisterSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(serializer.is_valid(), False)


class PublicUserLoginApiTests(APITestCase):

    def setUp(self):
        payload = {
            "email": "bekir.y@labrin.tech",
            "password": "user@12345%",
        }
        create_user(**payload)

    def test_successful_login(self):
        payload = {
            "email": "bekir.y@labrin.tech",
            "password": "user@12345%"
        }

        response = self.client.post(
            path=LOGIN_URL,
            data=payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_incorrect_credentials(self):

        payload = {
            "email": "bekir.y@labrin.tech",
            "password": "usertest@123%"
        }

        response = self.client.post(
            path=LOGIN_URL,
            data=payload,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PublicUserListApiTests(APITestCase):

    def setUp(self):
        payload_1 = {
            "email": "test@user.az",
            "first_name": "Test",
            "last_name": "User"
        }
        payload_2 = {
            "email": "testing@user.com",
            "first_name": "Test",
            "last_name": "User"
        }

        self.user_1 = create_user(**payload_1)
        self.user_2 = create_user(**payload_2)

        self.url = reverse('public_api:user-list')

    def test_user_list_request(self):

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PasswordResetApiTests(APITestCase):

    def setUp(self):
        payload = {
            "email": "test@user.az",
            "password": "usertest@12345%",
            "first_name": "User",
            "last_name": "Test"
        }
        self.user = create_user(**payload)

        self.url = reverse('public_api:password-reset')
        self.client.force_authenticate(user=self.user)

    def test_password_reset_request_successful(self):
        """
        Testing password reset API endpoint accepts put request successfully
        """

        password_reset_data = {
            "old_password": "usertest@12345%",
            "new_password": "newpassword1234",
            "confirm_new_password": "newpassword1234"
        }

        response = self.client.put(
            path=self.url,
            data=password_reset_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_reset_request_invalid_current_password(self):
        """
        Testing password reset API endpoint rejects the request if
        current password is not entered correctly
        """

        password_reset_data = {
            "old_password": "wrongpassword1234",
            "new_password": "newpassword1234",
            "confirm_new_password": "newpassword1234"
        }

        response = self.client.put(
            path=self.url,
            data=password_reset_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request_two_password_doesnt_match(self):
        """
        Testing password reset API endpoint rejects request if
        two new entered password does not match
        """

        password_reset_data = {
            "old_password": "usertest@12345%",
            "new_password": "newpassword1234",
            "confirm_new_password": "newpassword123"
        }

        response = self.client.put(
            path=self.url,
            data=password_reset_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_request_new_password_validation(self):
        """
        Testing password reset API endpoint validates password,
         user can login with new password
        """

        password_reset_data = {
            "old_password": "usertest@12345%",
            "new_password": "newpassword1234",
            "confirm_new_password": "newpassword1234"
        }

        self.client.put(
            path=self.url,
            data=password_reset_data,
            format='json'
        )
        self.client.logout()

        new_password_data = {
            "email": "test@user.az",
            "password": "newpassword1234"
        }
        old_password_data = {
            "email": "test@user.az",
            "password": "usertest@12345%"
        }

        response_with_new_password = self.client.post(
            path=LOGIN_URL,
            data=new_password_data,
            format='json'
        )
        response_with_old_password = self.client.post(
            path=LOGIN_URL,
            data=old_password_data,
            format='json'
        )

        self.assertEqual(
            response_with_new_password.status_code, status.HTTP_200_OK
        )
        self.assertIn('token', response_with_new_password.data)
        self.assertEqual(
            response_with_old_password.status_code, status.HTTP_400_BAD_REQUEST
        )


class PublicUserProfileUpdateApiTests(APITestCase):

    def setUp(self):

        # create a user
        user_data = {
            "email": "the_user@email.com",
            "first_name": "Bekir",
            "last_name": "Yunusov",
        }
        self.user = create_user(**user_data)

        # create the second user
        secondary_user = {
            "email": "another@user.az",
            "first_name": "Another",
            "last_name": "User"
        }
        self.secondary_user = create_user(**secondary_user)

        # endpoint url
        self.url = reverse('public_api:user-profile')

        # create a category
        category_data = {
            "title": "sport"
        }
        self.category = Category.objects.create(**category_data)

        # create a post
        post_data = {
            "title": "test post",
            "author": self.secondary_user,
        }
        self.post = Post.objects.create(**post_data)

    def test_public_user_retrieve_request_successful(self):
        """
        Testing public user profile API endpoint returns only requested user's
        profile.

        """
        response = self.client.get(self.url)

        # login required
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('email'), self.user.email)

    def test_public_user_update_request_successful(self):
        """
        Testing public user profile API endpoint update request
        """
        new_data = {
            "first_name": "new first name",
            "last_name": "new last name"
        }

        response = self.client.patch(
            path=self.url,
            data=new_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            path=self.url,
            data=new_data,
            format='json'
        )
        data = response.data.get('data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data.get('first_name'),
            self.user.first_name
        )

    def test_public_user_profile_update_saved_news_and_category(self):
        """
        Testing public user profile API endpoint update `saved_new` and
        `preferred_categories`

        """
        update_data = {
            "saved_news": [self.post.id],
            "preferred_categories": [self.category.id]
        }

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            path=self.url,
            data=update_data,
            format='json'
        )

        data = response.data.get('data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.post, self.user.saved_news.all())
        self.assertIn(self.category, self.user.preferred_categories.all())
        self.assertIn(self.post.id, data.get('saved_news'))
        self.assertIn(self.category.id, data.get('preferred_categories'))


class AuthorProfileApiTests(APITestCase):

    def setUp(self):
        user_data = {
            "email": "author@user.az",
            "first_name": "Author",
            "last_name": "Test"
        }
        self.user = create_user(**user_data)

        social_data = {
            'author': self.user,
            'social_media': 'Facebook',
            'url': 'https://facebook.com'
        }
        self.author = AuthorSocialMediaAccounts.objects.create(**social_data)
        self.url = reverse(
            'public_api:author-profile-retrieve', kwargs={'pk': self.user.id}
        )

    def test_author_profile_retrieve_request(self):
        """
        Testing author profile API endpoint retrieve request returns `Author`
        user, which means `is_staff=True` and `is_active=True`
        """
        # default => self.user.is_staff = False
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.user.is_staff = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
