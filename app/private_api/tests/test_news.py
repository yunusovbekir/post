from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from news.models import (
    Category,
    Feedback,
    PostIdentifier,
    Post,
    PostLike,
    PostDislike,
    Content,
    Comment,
    CommentLike,
    CommentDislike,
)
from ..serializers.news import (
    CategorySerializer,
    FeedbackSerializer,
    PostLikeSerializer,
    PostDislikeSerializer,
    CommentLikeSerializer,
    CommentDislikeSerializer,
)

"""
TESTED ENDPOINTS:
    1. PostIdentifierApiView => PostIdentifierApiTests
    2. CategoryApiView => PrivateCategoryApiTest
    3. FeedbackApiView => FeedbackApiTests
    4. PostLikeViewSet => PostLikeAndDislikeApiTest
    5. PostDislikeViewSet => PostLikeAndDislikeApiTest
    6. ContentApiView => ContentApiTestCases
    7. CommentLikeViewSet => ??
    8. CommentDislikeViewSet => ??
    7. PostApiView => ??
    8. CommentApiViewSet => ??
"""

USER = get_user_model()
CATEGORY_LIST_URL = reverse('private_api:category-list')


def create_user(**data):
    return USER.objects.create_user(**data)


def create_category(**data):
    return Category.objects.create(**data)


def create_feedback(**data):
    return Feedback.objects.create(**data)


def create_post(**payload):
    return Post.objects.create(**payload)


def create_postlike(**payload):
    return PostLike.objects.create(**payload)


def create_comment(**payload):
    return Comment.objects.create(**payload)


class PrivateCategoryApiTest(TestCase):

    def setUp(self):
        payload = {
            "email": "bekir@labrin.tech",
            "password": "sdhd62863%&fcd",
            "first_name": "test first name",
            "last_name": "test last name",
        }
        self.user = create_user(**payload)
        self.user.set_password(payload["password"])
        self.user.save()

        category_data = {
            "title": "test_category"
        }

        self.category = create_category(**category_data)
        self.category.save()

        self.category_detail_url = reverse(
            'private_api:category-detail',
            kwargs={'pk': self.category.id}
        )

    def test_category_api_list_request(self):
        client = APIClient()

        # basic user
        response = client.get(CATEGORY_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(CATEGORY_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(CATEGORY_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_api_retrieve_request(self):
        client = APIClient()

        # basic user
        response = client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_api_update_request(self):
        new_category = {
            "title": "test_updated_category"
        }
        client = APIClient()
        response = client.patch(
            path=self.category_detail_url,
            format="json",
            data=new_category
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_category_api_delete_request(self):
        client = APIClient()

        # basic user
        response = client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_api_returns_category_list(self):
        serializer = CategorySerializer(
            Category.objects.all(),
            many=True
        )
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get(CATEGORY_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True

        response = client.get(CATEGORY_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_category_detail(self):
        serializer = CategorySerializer(
            Category.objects.all()[0],
        )

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        response = client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_category_update(self):
        new_category = {
            "title": "test_updated_category"
        }
        client = APIClient()

        # basic user
        patch_response = client.patch(
            path=self.category_detail_url,
            format="json",
            data=new_category
        )
        put_response = client.patch(
            path=self.category_detail_url,
            format="json",
            data=new_category
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        patch_response = client.patch(
            path=self.category_detail_url,
            format="json",
            data=new_category
        )
        put_response = client.patch(
            path=self.category_detail_url,
            format="json",
            data=new_category
        )
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        patch_response = client.patch(
            path=self.category_detail_url,
            format="json",
            data=new_category
        )
        put_response = client.patch(
            path=self.category_detail_url,
            format="json",
            data=new_category
        )
        updated_category = Category.objects.get(id=self.category.id)

        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_category.title, new_category.get('title'))

    def test_delete_category(self):
        client = APIClient()

        # basic user
        response = client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class FeedbackApiTests(APITestCase):
    """
    Tests for Private Feedback API endpoints
    """

    def setUp(self):
        """
        Set up test objects
        1. User
        2. Keyword (Post Identifier)
        3. Post
        4. Feedback
        5. URL for list, create requests
        6. URL for retrieve, update, partial_update, delete requests
        """

        user_data = {
            "email": "test@test.az",
            "first_name": "Test",
            "last_name": "User",
        }
        self.user = create_user(**user_data)
        self.user.save()

        keyword = PostIdentifier.objects.create(title="LIVE")

        post_data = {
            "title": "Testing Post",
            "author": self.user,
            "keyword": keyword
        }
        self.post = Post.objects.create(**post_data)

        feedback_data = {
            "post": self.post,
            "owner": self.user,
            "text": "Testing feedback",
        }

        self.feedback = Feedback.objects.create(**feedback_data)

        self.url_list = reverse('private_api:feedback-api-list')
        self.url_detail = reverse(
            'private_api:feedback-api-detail',
            kwargs={'pk': self.feedback.id},
        )

    def test_feedback_list_request(self):
        """
        Testing list request with 3 different users:

            Unauthenticated user => 401 Unauthenticated
            Logged basic user => 403 Forbidden
            Staff user => 200 OK
        """

        client = APIClient()
        response_basic_user = client.get(path=self.url_list)
        self.assertEqual(
            response_basic_user.status_code, status.HTTP_401_UNAUTHORIZED
        )

        client.force_authenticate(user=self.user)
        response_logged_user = client.get(path=self.url_list)
        self.assertEqual(
            response_logged_user.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.is_staff = True
        response_admin_user = client.get(path=self.url_list)
        self.assertEqual(
            response_admin_user.status_code, status.HTTP_200_OK
        )

    def test_feedback_retrieve_request(self):
        """
        Testing retrieve requests with 3 different users:

        Unauthenticated user => 401 Unauthenticated
        Logged basic user => 403 Forbidden
        Staff user => 200 OK
        """

        client = APIClient()
        response_basic_user = client.get(path=self.url_detail)
        self.assertEqual(
            response_basic_user.status_code, status.HTTP_401_UNAUTHORIZED
        )

        client.force_authenticate(user=self.user)
        response_logged_user = client.get(path=self.url_detail)
        self.assertEqual(
            response_logged_user.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.is_staff = True
        self.user.save()
        response_admin_user = client.get(path=self.url_detail)
        self.assertEqual(
            response_admin_user.status_code, status.HTTP_200_OK
        )

    def test_feedback_create_request(self):
        """
        Testing create request with 5 different users:

        Unauthenticated user => 401 Unauthenticated
        Logged basic user => 403 Forbidden
        Reporter user => 403 Forbidden
        Editor => 201 Created
        Admin => 201 Created
        """

        # unauthenticated user
        feedback_data = {
            "post": self.post.id,
            "text": "Testing create request"
        }
        client = APIClient()
        response_user = client.post(
            path=self.url_list,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            response_user.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        response_logged_user = client.post(
            path=self.url_list,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            response_logged_user.status_code, status.HTTP_403_FORBIDDEN
        )

        # Reporter staff user
        self.user.is_staff = True
        self.user.user_type = 2
        response_reporter = client.post(
            path=self.url_list,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            response_reporter.status_code, status.HTTP_201_CREATED
        )

        # Editor staff user
        self.user.user_type = 3
        response_editor = client.post(
            path=self.url_list,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            response_editor.status_code, status.HTTP_201_CREATED
        )

        # Superuser
        self.user.user_type = 4
        response_superuser = client.post(
            path=self.url_list,
            data=feedback_data,
            format='json'
        )
        # add user to request
        response_superuser.user = self.user
        serializer = FeedbackSerializer(
            data=feedback_data,
            context={"request": response_superuser}
        )
        test_serializer = FeedbackSerializer(
            Feedback.objects.last()
        )
        # test create request is successful
        self.assertEqual(
            response_superuser.status_code, status.HTTP_201_CREATED
        )
        # test adding user to request works as expected
        self.assertTrue(serializer.is_valid())
        # test serializer
        self.assertEqual(response_superuser.data, test_serializer.data)

    def test_feedback_update_requests(self):
        """
        Testing update request with 6 different users:

        Unauthenticated user => 401 Unauthenticated
        Logged basic user => 403 Forbidden
        Reporter user => 403 Forbidden
        Editor => 403 Forbidden
        Admin => 403 Forbidden
        Owner => 200 OK
        """

        secondary_user_data = {
            "email": "owner@test.az",
            "first_name": "The",
            "last_name": ""
        }
        secondary_user = create_user(**secondary_user_data)
        feedback_owner = self.user
        feedback_owner.is_staff = True
        feedback_owner.user_type = 4

        # unauthenticated user
        feedback_data = {
            "post": self.post.id,
            "text": "Testing put request",
        }

        client = APIClient()
        put_response_user = client.put(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        patch_response_user = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            put_response_user.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            patch_response_user.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=secondary_user)
        put_response_logged_user = client.put(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        patch_response_logged_user = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            put_response_logged_user.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            patch_response_logged_user.status_code, status.HTTP_403_FORBIDDEN
        )

        # Reporter staff user
        secondary_user.is_staff = True
        secondary_user.user_type = 2
        put_response_reporter = client.put(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        patch_response_reporter = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            put_response_reporter.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            patch_response_reporter.status_code, status.HTTP_403_FORBIDDEN
        )

        # Editor staff user
        secondary_user.user_type = 3
        put_response_editor = client.put(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        patch_response_editor = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            put_response_editor.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            patch_response_editor.status_code, status.HTTP_403_FORBIDDEN
        )

        # Admin
        secondary_user.user_type = 4
        put_response_superuser = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        patch_response_superuser = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )

        self.assertEqual(
            put_response_superuser.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            patch_response_superuser.status_code, status.HTTP_403_FORBIDDEN
        )

        client.logout()
        client.force_authenticate(user=feedback_owner)

        put_response_feedback_owner = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        patch_response_feedback_owner = client.patch(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )

        self.assertEqual(
            put_response_feedback_owner.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            patch_response_feedback_owner.status_code, status.HTTP_200_OK
        )

    def test_feedback_delete_request(self):
        """
        Testing delete request with 6 different users:

        Unauthenticated user => 401 Unauthenticated
        Logged basic user => 403 Forbidden
        Reporter user => 403 Forbidden
        Editor => 403 Forbidden
        Admin => 403 Forbidden
        Owner => 204 No Content
        """
        secondary_user_data = {
            "email": "owner@test.az",
            "first_name": "The",
            "last_name": ""
        }
        secondary_user = create_user(**secondary_user_data)
        feedback_owner = self.user
        feedback_owner.is_staff = True
        feedback_owner.user_type = 4

        # unauthenticated user
        feedback_data = {
            "post": self.post.id,
            "text": "Testing put request",
        }

        client = APIClient()
        delete_response_user = client.delete(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            delete_response_user.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=secondary_user)
        delete_response_logged_user = client.delete(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            delete_response_logged_user.status_code, status.HTTP_403_FORBIDDEN
        )

        # Reporter staff user
        secondary_user.is_staff = True
        secondary_user.user_type = 2
        delete_response_reporter = client.delete(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            delete_response_reporter.status_code, status.HTTP_403_FORBIDDEN
        )

        # Editor staff user
        secondary_user.user_type = 3
        delete_response_editor = client.delete(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            delete_response_editor.status_code, status.HTTP_403_FORBIDDEN
        )

        # Admin
        secondary_user.user_type = 4
        delete_response_superuser = client.delete(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            delete_response_superuser.status_code, status.HTTP_403_FORBIDDEN
        )

        client.logout()
        client.force_authenticate(user=feedback_owner)

        delete_response_feedback_owner = client.delete(
            path=self.url_detail,
            data=feedback_data,
            format='json'
        )
        self.assertEqual(
            delete_response_feedback_owner.status_code,
            status.HTTP_204_NO_CONTENT
        )


class PostIdentifierApiTests(APITestCase):
    """
    Testing Post Identifier requests with 3 different users

    basic user => 401 Unauthenticated
    logged user => 403 Forbidden
    logged staff user => 200 OK
    """

    def setUp(self):
        self.keyword_data = {
            "title": "LIVE"
        }
        self.keyword = PostIdentifier.objects.create(**self.keyword_data)

        staff_user_data = {
            "email": "test@test.az",
            "first_name": "Test",
            "last_name": "User"
        }
        self.url_list = reverse('private_api:post-identifier-api-list')
        self.url_detail = reverse(
            'private_api:post-identifier-api-detail',
            kwargs={'pk': self.keyword.id}
        )
        self.user = create_user(**staff_user_data)

    def test_post_identifier_list_request(self):
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
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_identifier_retrieve_request(self):
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
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_identifier_create_request(self):
        """
        Testing create request with 3 different users
        """

        client = APIClient()
        data = {"title": "TEST"}
        response = client.post(
            self.url_list,
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.post(
            self.url_list,
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        response = client.post(
            self.url_list,
            data=data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_identifier_update_request(self):
        """
         Testing update, partial_update request with 3 different users
        """
        client = APIClient()
        data = {"title": "TEST"}
        put_response = client.put(
            self.url_detail,
            data=data
        )
        patch_response = client.patch(
            self.url_detail,
            data=data
        )
        self.assertEqual(
            put_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            patch_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        client.force_authenticate(user=self.user)
        put_response = client.put(
            self.url_detail,
            data=data
        )
        patch_response = client.patch(
            self.url_detail,
            data=data
        )
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        put_response = client.put(
            self.url_detail,
            data=data
        )
        patch_response = client.patch(
            self.url_detail,
            data=data
        )
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

    def test_post_identifier_delete_request(self):
        """
        Testing delete request with 3 different users
        """

        client = APIClient()
        response = client.delete(
            self.url_detail,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        client.force_authenticate(user=self.user)
        response = client.delete(
            self.url_detail,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        response = client.delete(
            self.url_detail,
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PostLikeAndDislikeApiTest(TestCase):
    """
    Post like and dislike API endpoint tests.
    `RETRIEVE` => Staff user
    `LIST` => Staff user
    `CREATE` => No one
    `UPDATE` => No one
    `PARTIAL_UPDATE` => No one
    `DESTROY` => No one

    """

    def setUp(self):
        user_data = {
            "email": "user@user.us",
            "password": "sdhd62863%&fsdvsqeswegfs",
            "first_name": "test_ first name",
            "last_name": "test_ last name",
        }
        self.user = create_user(**user_data)
        self.user.set_password(user_data["password"])
        self.user.save()

        keyword = PostIdentifier.objects.create(title="OPEN")

        category = Category.objects.create(title="Category1")

        post_data = {
            "title": "Testpost",
            "author": self.user,
            "keyword": keyword,
            "short_description": "sfhswiaa"
        }
        self.post = create_post(**post_data)
        self.post.category.add(category)
        self.postlike = PostLike.objects.filter(post=self.post)[0]
        self.postdislike = PostDislike.objects.filter(post=self.post)[0]

        self.url_like_detail = reverse('private_api:postlike-api-detail',
                                       kwargs={'pk': self.postlike.id})
        self.url_dislike_detail = reverse('private_api:postdislike-api-detail',
                                          kwargs={'pk': self.postdislike.id})
        self.url_like_list = reverse('private_api:postlike-api-list')
        self.url_dislike_list = reverse('private_api:postdislike-api-list')

    def test_api_returns_post_like_list_to_only_staff_user(self):
        """
        Testing Post like list request test, only Staff user is allowed
        """
        serializer = PostLikeSerializer(
            PostLike.objects.all(),
            many=True
        )
        client = APIClient()
        # basic user
        response = client.get(self.url_like_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_like_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_like_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_api_returns_post_like_retrieve_to_only_staff_user(self):
        """
        Testing Post like retrieve request test, only Staff user is allowed
        """

        serializer = PostLikeSerializer(
            PostLike.objects.all()[0]
        )
        client = APIClient()

        # basic user
        response = client.get(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_post_like_is_not_allowed(self):
        """
        Testing Post like update request method is NOT allowed to ANYONE
        """

        client = APIClient()

        # basic user
        patch_response = client.patch(
            path=self.url_like_detail
        )
        put_response = client.put(
            path=self.url_like_detail
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        patch_response = client.patch(
            path=self.url_like_detail
        )
        put_response = client.put(
            path=self.url_like_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.user_type = 2
        patch_response = client.patch(
            path=self.url_like_detail
        )
        put_response = client.put(
            path=self.url_like_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

        # editor user
        self.user.user_type = 3
        patch_response = client.patch(
            path=self.url_like_detail
        )
        put_response = client.put(
            path=self.url_like_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

        # admin user
        self.user.user_type = 4
        patch_response = client.patch(
            path=self.url_like_detail
        )
        put_response = client.put(
            path=self.url_like_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_like_is_not_allowed(self):
        """
        Testing Post like delete request method is NOT allowed to ANYONE
        """

        client = APIClient()

        # basic user
        response = client.delete(
            path=self.url_like_detail
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        response = client.delete(
            path=self.url_like_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.user_type = 2
        response = client.delete(
            path=self.url_like_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # editor user
        self.user.user_type = 3
        response = client.delete(
            path=self.url_like_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # admin user
        self.user.user_type = 4
        response = client.delete(
            path=self.url_like_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_returns_post_dislike_list_to_only_staff_user(self):
        """
        Testing Post dislike list request, only Staff user is allowed
        """

        serializer = PostDislikeSerializer(
            PostDislike.objects.all(),
            many=True
        )
        client = APIClient()

        # basic user
        response = client.get(self.url_dislike_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_dislike_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_dislike_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_api_returns_post_dislike_retrieve_to_only_staff_user(self):
        """
        Testing Post dislike retrieve request, only Staff user is allowed
        """

        serializer = PostDislikeSerializer(
            PostDislike.objects.all()[0]
        )
        client = APIClient()

        # basic user
        response = client.get(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_post_dislike_is_not_allowed(self):
        """
        Testing Post dislike update request method is NOT allowed to ANYONE
        """

        client = APIClient()

        # basic user
        put_response = client.patch(
            path=self.url_dislike_detail
        )
        patch_response = client.put(
            path=self.url_dislike_detail
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        put_response = client.put(
            path=self.url_dislike_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.user_type = 2
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        put_response = client.put(
            path=self.url_dislike_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

        # editor user
        self.user.user_type = 3
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        put_response = client.put(
            path=self.url_dislike_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

        # admin user
        self.user.user_type = 4
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        put_response = client.put(
            path=self.url_dislike_detail
        )
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_dislike_is_not_allowed(self):
        """
        Testing Post like delete request method is NOT allowed to ANYONE
        """

        client = APIClient()

        # basic user
        response = client.delete(
            path=self.url_dislike_detail
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        response = client.delete(
            path=self.url_dislike_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.user_type = 2
        response = client.delete(
            path=self.url_dislike_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # editor user
        self.user.user_type = 3
        response = client.delete(
            path=self.url_dislike_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # admin user
        self.user.user_type = 4
        response = client.delete(
            path=self.url_dislike_detail
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ContentApiTestCases(APITestCase):
    """
    API endpoints for Post Contents.
    All admin users can perform all requests.
    Exception:
        If post is approved, reporter user is allowed only for SAFE_METHODS.

    Allowed requests:
        `GET` => Admin user
        `POST` => Admin user
        `PUT` and `PATCH`=> Admin user if Post is not approved
        `PUT` and `PATCH` => Editor and Admin user if Post is approved
        `DELETE` => Admin user
    """

    def setUp(self):
        user_data = {
            "email": "test@test.az",
            "first_name": "Test",
            "last_name": "User",
        }
        self.user = create_user(**user_data)
        self.user.save()

        keyword = PostIdentifier.objects.create(title="LIVE")

        post_data = {
            "title": "Testing Post",
            "author": self.user,
            "keyword": keyword
        }
        self.post = Post.objects.create(**post_data)

        content_data = {
            "content_type": "Main Text",
            "ordering": 0,
            "title": "Testing",
            "text": "testing",
            "post": self.post
        }

        self.content_request_data = {
            "content_type": "Main Text",
            "ordering": 0,
            "title": "request",
            "text": "testing api request",
            "post": self.post.id
        }

        self.content = Content.objects.create(**content_data)
        self.url_list = reverse('private_api:content-api-list')
        self.url_detail = reverse('private_api:content-api-detail',
                                  kwargs={"pk": self.content.id})

    def test_retrieve_post_content_staff_user_only(self):
        """
        Only staff user is allowed to make list action
        """

        client = APIClient()

        # basic user
        response = client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response_auth_user = client.get(self.url_list)
        self.assertEqual(
            response_auth_user.status_code, status.HTTP_403_FORBIDDEN
        )

        # staff user
        self.user.is_staff = True
        response_staff_user = client.get(self.url_list)
        self.assertEqual(
            response_staff_user.status_code, status.HTTP_200_OK
        )

    def test_list_post_content_staff_user_only(self):
        """
        Only staff user is allowed to make retrieve action
        """

        client = APIClient()

        # basic user
        response = client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response_auth_user = client.get(self.url_detail)
        self.assertEqual(
            response_auth_user.status_code, status.HTTP_403_FORBIDDEN
        )

    def test_post_post_content_staff_user_only(self):
        """
        Only staff user is allowed to make POST request
        """

        client = APIClient()

        # basic user
        response = client.post(
            path=self.url_list,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response_auth_user = client.post(
            path=self.url_list,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            response_auth_user.status_code, status.HTTP_403_FORBIDDEN
        )

        # staff user
        self.user.is_staff = True
        response_staff_user = client.post(
            path=self.url_list,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            response_staff_user.status_code, status.HTTP_201_CREATED
        )

    def test_patch_non_approved_post_content(self):
        """
        If the post is not approved, reporter can update the post content
        """

        client = APIClient()

        # basic user
        patch_response = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        patch_response_auth_user = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response_auth_user = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response_auth_user.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            put_response_auth_user.status_code, status.HTTP_403_FORBIDDEN
        )

        # staff user
        self.user.is_staff = True
        patch_response_staff_user = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response_staff_user = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response_staff_user.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            put_response_staff_user.status_code, status.HTTP_200_OK
        )

    def test_patch_approved_post_content(self):
        """
        If the post is approved, reporter CANNOT update the post content
        """

        client = APIClient()
        self.post.is_approved = True

        # basic user
        patch_response = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        patch_response_auth_user = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response_auth_user = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response_auth_user.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            put_response_auth_user.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.is_staff = True
        post = Post.objects.last()
        post.is_approved = True
        post.save()

        # reporter user
        self.user.user_type = 2
        patch_response_reporter_user = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response_reporter_user = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response_reporter_user.status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            put_response_reporter_user.status_code, status.HTTP_403_FORBIDDEN
        )

        # editor user
        self.user.user_type = 3
        patch_response_editor_user = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response_editor_user = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response_editor_user.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            put_response_editor_user.status_code, status.HTTP_200_OK
        )

        # admin user
        self.user.user_type = 4
        patch_response_admin_user = client.patch(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        put_response_admin_user = client.put(
            path=self.url_detail,
            data=self.content_request_data,
            format="json"
        )
        self.assertEqual(
            patch_response_admin_user.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            put_response_admin_user.status_code, status.HTTP_200_OK
        )

    def test_delete_non_approved_post_content(self):
        """
        If the post is not approved, reporter can delete the post content
        """

        client = APIClient()

        # basic user
        response = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        response = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )

        # staff user
        self.user.is_staff = True
        response = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT
        )

    def test_delete_approved_post_content(self):
        """
        If the post is not approved, reporter can update the post content
        """

        client = APIClient()
        self.post.is_approved = True

        # basic user
        response = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        response_logged = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response_logged.status_code, status.HTTP_403_FORBIDDEN
        )

        self.user.is_staff = True
        post = Post.objects.last()
        post.is_approved = True
        post.save()

        # reporter user
        self.user.user_type = 2
        response_reporter = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response_reporter.status_code, status.HTTP_403_FORBIDDEN
        )

        # editor user
        self.user.user_type = 3
        response_editor = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response_editor.status_code, status.HTTP_403_FORBIDDEN
        )

        # admin user
        self.user.user_type = 4
        response_admin = client.delete(
            path=self.url_detail,
        )
        self.assertEqual(
            response_admin.status_code, status.HTTP_204_NO_CONTENT
        )


class CommentLikeAndDislikeApiTest(TestCase):
    """
    Comment like and dislike API endpoint tests.
    `RETRIEVE` => Staff user
    `LIST` => Staff user
    `CREATE` => Nobody
    `UPDATE` => Nobody
    `PARTIAL_UPDATE` => Nobody
    `DESTROY` => Nobody

    """

    def setUp(self):
        user_data = {
            "email": "user@user.az",
            "password": "sdhd62863%&fcdafsswegfs",
            "first_name": "test_ first name",
            "last_name": "test_ last name",
        }
        self.user = create_user(**user_data)
        self.user.set_password(user_data["password"])
        self.user.save()

        keyword = PostIdentifier.objects.create(title="OPEN")
        category = Category.objects.create(title="Category")

        post_data = {
            "title": "TEstpost",
            "author": self.user,
            "keyword": keyword,
            "short_description": "sfhswiaa"
        }
        self.post = create_post(**post_data)
        self.post.category.add(category)

        self.post.save()
        comment_data = {
            "commented_by": self.user,
            "post": self.post,
            "replied_comment": None,
            "comment": "testing like and dislike request"
        }
        self.comment = create_comment(**comment_data)
        self.comment.save()

        self.commentlike = CommentLike.objects.filter(
            comment=self.comment)[0]
        self.commentdislike = CommentDislike.objects.filter(
            comment=self.comment)[0]

        self.url_like_list = reverse(
            'private_api:comment-like-api-list',
        )
        self.url_like_detail = reverse(
            'private_api:comment-like-api-detail',
            kwargs={'pk': self.commentlike.id})
        self.url_dislike_list = reverse(
            'private_api:comment-dislike-api-list',
        )
        self.url_dislike_detail = reverse(
            'private_api:comment-dislike-api-detail',
            kwargs={'pk': self.commentdislike.id})

    def test_api_returns_comment_like_list_to_only_staff_user(self):
        """
        Testing Comment like list request test, only Staff user is allowed
        """
        serializer = CommentLikeSerializer(
            CommentLike.objects.all(),
            many=True
        )
        client = APIClient()

        # basic user
        response = client.get(self.url_like_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_like_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_like_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_api_returns_comment_like_retrieve_to_only_staff_user(self):
        """
        Testing Comment like retrieve request test, only Staff user is allowed
        """

        serializer = CommentLikeSerializer(
            CommentLike.objects.all()[0]
        )
        client = APIClient()

        # basic user
        response = client.get(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_nobody_can_update_comment_like(self):
        """
        Testing Comment like update request test, no one is allowed.
        """

        client = APIClient()

        # basic user
        patch_response = client.patch(
            path=self.url_like_detail
        )
        put_response = client.put(
            path=self.url_like_detail
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        put_response = client.put(
            path=self.url_like_detail
        )
        patch_response = client.patch(
            path=self.url_like_detail
        )
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.is_staff = True
        self.user.user_type = 2
        patch_response = client.patch(
            path=self.url_like_detail
        )
        put_response = client.put(
            path=self.url_like_detail
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 2)

        # editor user
        self.user.user_type = 3
        put_response = client.put(
            path=self.url_like_detail
        )
        patch_response = client.patch(
            path=self.url_like_detail
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 3)

        # admin user
        self.user.user_type = 4
        put_response = client.put(
            path=self.url_like_detail
        )
        patch_response = client.patch(
            path=self.url_like_detail
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 4)

    def test_nobody_can_delete_comment_like(self):
        """
        Testing Comment like delete request test, no one is allowed
        """

        client = APIClient()

        # basic user
        response = client.delete(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.delete(self.url_like_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.is_staff = True
        self.user.user_type = 2
        response = client.delete(self.url_like_detail)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 2)

        # editor user
        self.user.user_type = 3
        response = client.delete(self.url_like_detail)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 3)

        # admin user
        self.user.user_type = 4
        response = client.delete(self.url_like_detail)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 4)

    def test_api_returns_comment_dislike_list_to_only_staff_user(self):
        """
        Testing Comment dislike list request, only Staff user is allowed
        """

        serializer = CommentDislikeSerializer(
            CommentDislike.objects.all(),
            many=True
        )
        client = APIClient()

        # basic user
        response = client.get(self.url_dislike_list)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_dislike_list)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_dislike_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_api_returns_comment_dislike_retrieve_to_only_staff_user(self):
        """
        Testing Comment dislike retrieve request, only Staff user is allowed
        """

        serializer = CommentDislikeSerializer(
            CommentDislike.objects.all()[0]
        )
        client = APIClient()

        # basic user
        response = client.get(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.get(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = client.get(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_nobody_can_update_comment_dislike(self):
        """
        Testing Comment dislike update request test, no one is allowed.
        """

        client = APIClient()

        # basic user
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        put_response = client.put(
            path=self.url_dislike_detail
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_401_UNAUTHORIZED
        )

        # logged user
        client.force_authenticate(user=self.user)
        put_response = client.put(
            path=self.url_dislike_detail
        )
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        self.assertEqual(put_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(patch_response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.is_staff = True
        self.user.user_type = 2
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        put_response = client.put(
            path=self.url_dislike_detail
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 2)

        # editor user
        self.user.user_type = 3
        put_response = client.put(
            path=self.url_dislike_detail
        )
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 3)

        # admin user
        self.user.user_type = 4
        put_response = client.put(
            path=self.url_dislike_detail
        )
        patch_response = client.patch(
            path=self.url_dislike_detail
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 4)

    def test_nobody_can_delete_comment_dislike(self):
        """
        Testing Comment dislike delete request test, no one is allowed
        """

        client = APIClient()

        # basic user
        response = client.delete(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        client.force_authenticate(user=self.user)
        response = client.delete(self.url_dislike_detail)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.is_staff = True
        self.user.user_type = 2
        response = client.delete(self.url_dislike_detail)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 2)

        # editor user
        self.user.user_type = 3
        response = client.delete(self.url_dislike_detail)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 3)

        # admin user
        self.user.user_type = 4
        response = client.delete(self.url_dislike_detail)
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(self.user.user_type, 4)


class PrivatePostApiTests(APITestCase):
    """
    `GET` => Staff user
    `POST` => Staff user
    `PATCH` => Reporter user (if Post has not been approved)
    `PATCH` => Editor or Superuser user (if Post has been approved)
    `DELETE` => Admin user
    """
    def setUp(self):
        user_data = {
            "email": "admin@admin.az",
            "first_name": "first name",
            "last_name": "last name",
        }
        self.user = create_user(**user_data)
        self.user.save()

        self.keyword = PostIdentifier.objects.create(title="OPEN")
        self.category = create_category(title='Sport')

        post_data = {
            "title": "Test",
            "author": self.user,
            "keyword": self.keyword,
            "short_description": "testing post api",
            "is_approved": False,
        }

        self.post = create_post(**post_data)
        self.post_list_url = reverse('private_api:post-list')
        self.post_retrieve_url = reverse(
            'private_api:post-retrieve',
            kwargs={'pk': self.post.id}
        )
        self.post_create_url = reverse('private_api:post-create')
        self.non_approved_post_update = reverse(
            'private_api:update-non-approved-post',
            kwargs={'pk': self.post.id}
        )
        self.approved_post_update = reverse(
            'private_api:update-approved-post',
            kwargs={'pk': self.post.id}
        )

    def test_post_list_request_only_staff_user_is_allowed(self):

        # basic user
        response = self.client.get(
            path=self.post_list_url,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            path=self.post_list_url,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = self.client.get(
            path=self.post_list_url,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_retrieve_request_only_staff_user_is_allowed(self):

        # basic user
        response = self.client.get(
            path=self.post_retrieve_url,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            path=self.post_retrieve_url,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = self.client.get(
            path=self.post_retrieve_url,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_create_request_only_staff_user_is_allowed(self):
        post_payload = {
            "title": "Test",
            "keyword": self.keyword.id,
            "category": [self.category.id],
            "short_description": "testing post api"
        }

        # basic user
        response = self.client.post(
            path=self.post_create_url,
            data=post_payload,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            path=self.post_create_url,
            data=post_payload,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # staff user
        self.user.is_staff = True
        response = self.client.post(
            path=self.post_create_url,
            data=post_payload,
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_non_approved_post_update_request(self):
        """
        Non-approved posts can be updated by staff user
        Update `title`, `short_description`.
        `Remove` previous category, `add` new category.
        """
        new_category_object = create_category(title='lorem')

        # get new category as an object
        new_category = new_category_object.id

        # get old category as an object
        old_category = self.category.id

        post_update_payload = {
            "title": "Updated test post",
            "category": (new_category,),
            "short_description": "testing update post by staff user"
        }

        # basic user
        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.is_staff = True
        self.user.user_type = 2
        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )

        response_data = response.data.get('data')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
             new_category, response_data.get('category')
        )
        self.assertNotIn(
            old_category, response_data.get('category')
        )

        # editor user
        self.user.is_staff = True
        self.user.user_type = 3

        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
             new_category, response_data.get('category')
        )
        self.assertNotIn(
            old_category, response_data.get('category')
        )

        # admin user
        self.user.is_staff = True
        self.user.user_type = 4

        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
             new_category, response_data.get('category')
        )
        self.assertNotIn(
            old_category, response_data.get('category')
        )

    def test_approved_post_update_request(self):
        """
        Approved posts can be updated only by editor and admin users
        Update `title`, `short_description`.
        `Remove` previous category, `add` new category.
        """
        self.post.is_approved = True
        self.post.save()
        new_category_object = create_category(title='lorem')

        # get new category as an object
        new_category = new_category_object.id

        # get old category as an object
        old_category = self.category.id

        post_update_payload = {
            "title": "Updated test post",
            "category": (new_category,),
            "short_description": "testing update post by staff user"
        }

        # basic user
        response = self.client.patch(
            path=self.approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            path=self.approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.is_staff = True
        self.user.user_type = 2

        response = self.client.patch(
            path=self.approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # editor user
        self.user.user_type = 3

        response = self.client.patch(
            path=self.approved_post_update,
            data=post_update_payload,
            format='json'
        )
        response_data = response.data.get('data')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(
            new_category, response_data.get('category')
        )
        self.assertNotIn(
            old_category, response_data.get('category')
        )

        # admin user
        self.user.user_type = 4

        response = self.client.patch(
            path=self.approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data.get('data')
        self.assertIn(
            new_category, response_data.get('category')
        )
        self.assertNotIn(
            old_category, response_data.get('category')
        )

    def test_update_approved_post_with_api_for_non_approved_posts(self):
        """
        Testing `update-non-approved-post` endpoint with approved post
        If Post is approved, `update-non-approved-post` cannot accept a request
        """
        self.post.is_approved = True
        self.post.save()
        new_category = create_category(title='lorem')

        post_update_payload = {
            "title": "Updated test post",
            "category": (new_category.id,),
            "short_description": "testing update post by staff user"
        }

        # basic user
        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # logged user
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # reporter user
        self.user.is_staff = True
        self.user.user_type = 2

        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # editor user
        self.user.user_type = 3

        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # admin user
        self.user.user_type = 4

        response = self.client.patch(
            path=self.non_approved_post_update,
            data=post_update_payload,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_approve_by_only_editor_or_admin_user(self):
        pass
