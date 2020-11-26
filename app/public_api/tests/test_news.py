from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..serializers.news import (
    PublicPostListModelSerializer,
    PublicPostDetailModelSerializer,
    PublicCommentCreateSerializer,
    PublicCategoryListModelSerializer,
)
from news.models import Post, Category, PostIdentifier, Comment


POST_LIST_URL = reverse('public_api:public-post-list')
LOGIN_URL = reverse('public_api:user-login')
USER = get_user_model()


def create_post(**payload):
    return Post.objects.create(**payload)


def create_user(**payload):
    return USER.objects.create_user(**payload)


def create_comment(**payload):
    return Comment.objects.create(**payload)


class PostListAndDetailApiTests(APITestCase):
    """ Public User Test Cases """

    def setUp(self):
        """
        Creating `User`, `Post`, `Category`, `Post Identifier` objects
        """

        user_data = {
            'email': 'author@user.com',
            'first_name': 'test name',
            'last_name': 'test surname',
        }
        author = create_user(**user_data)

        keyword = PostIdentifier.objects.create(title="LIVE")

        category = Category.objects.create(title="Sport")

        self.payload = {
            "title": "Test Post",
            "author": author,
            "keyword": keyword,
            "short_description": ""
        }

        self.post = create_post(**self.payload)
        self.post.category.add(category)
        self.post.is_approved = True
        self.post.save()

    def test_api_returns_only_approved_post_lists(self):
        """
        Testing Post List API endpoint returns only approved and `Open` posts
        """

        serializer = PublicPostListModelSerializer(
            Post.objects.filter(is_approved=True, status='Open'),
            many=True
        )
        response = self.client.get(POST_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_api_returns_only_approved_post(self):
        """
        Testing Post List API endpoint returns only approved and `Open` posts
        """

        serializer = PublicPostDetailModelSerializer(
            Post.objects.filter(is_approved=True, status='Open').last(),
        )
        url = reverse('public_api:public-post-detail',
                      kwargs={'pk': self.post.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), serializer.data.get('id'))


class PostAndCommentApiTests(APITestCase):
    """
    Testing Post `like request` and `dislike request`
    Testing Comment `create`, `update`, `like request`, and `dislike request`
    """

    def setUp(self):
        """
        Set new data for testing: new Post, new User
            1. Create a post
            2. Test if like_count and dislike_count is 0
            3. Create a user
            4. Add user to Post's dislike list
            5. Test if Post Dislike count is 1 and use in dislike list
        """

        # create a post
        author_data = {
            'email': 'author@user.com',
            'first_name': 'test name',
            'last_name': 'test surname',
        }
        author = create_user(**author_data)
        keyword = PostIdentifier.objects.create(title="LIVE")
        category = Category.objects.create(title="Sport")

        self.payload = {
            "title": "Test New Post",
            "author": author,
            "keyword": keyword,
            "short_description": ""
        }

        self.post = create_post(**self.payload)
        self.post.category.add(category)
        self.post.is_approved = True
        self.post.save()

        self.test_post = Post.objects.get(title='Test New Post')

        # test like and dislike count is 0
        self.assertEqual(self.test_post.like_count, 0)
        self.assertEqual(self.test_post.dislike_count, 0)

        # create a user
        payload = {
            "email": "user@test.az",
            "password": "user@12345%",
            'first_name': 'User',
            'last_name': 'Surname'
        }
        self.user = create_user(**payload)

        # add user to dislike list
        self.test_post.post_dislike.user.add(self.user)
        self.assertEqual(self.test_post.dislike_count, 1)
        self.assertIn(self.user, self.test_post.post_dislike.user.all())

        # `post-like-request` url
        self.post_like_request_url = reverse(
            'public_api:public-post-like-request',
            kwargs={'pk': self.test_post.id}
        )

        # `post-dislike-request` url
        self.post_dislike_request_url = reverse(
            'public_api:public-post-dislike-request',
            kwargs={'pk': self.test_post.id}
        )

        # `create a comment` url
        self.comment_create_url = reverse('public_api:public-create-comment')

        # payload for test comment
        self.comment_payload = {
            "post": self.test_post.id,
            "replied_comment": "",
            "comment": "testing comment request"
        }

    def test_post_like_request_authenticated_user_only(self):
        """
        Make sure like request accepts only authenticated requests,
        else it throws 403 Forbidden error
        """

        response = self.client.patch(
            path=self.post_like_request_url,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_dislike_request_authenticated_user_only(self):
        """
        Make sure dislike request accepts only authenticated requests,
        else it throws 403 Forbidden error
        """

        response = self.client.patch(
            path=self.post_dislike_request_url
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_like_request_successful(self):
        """
        Having done a like request:
            1. user is removed from Post Dislike list,
            2. Post Dislike count changed from 1 to 0
            3. user is added to Post Like list
            4. Post Like count changed from 0 to 1
        """
        # force user to login
        self.client.force_authenticate(user=self.user)

        # make sure the user is authenticated
        profile_url = reverse('public_api:user-profile')
        response = self.client.get(
            path=profile_url,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # make a like request
        like_response = self.client.patch(
            path=self.post_like_request_url
        )

        self.assertEqual(self.test_post.dislike_count, 0)
        self.assertEqual(self.test_post.like_count, 1)
        self.assertEqual(like_response.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, self.test_post.post_like.user.all())

    def test_post_dislike_request_successful(self):
        """
        Having done a dislike request:
            1. user is removed from Post Like list,
            2. Post Like count changed from 1 to 0
            3. user is added to Post Dislike list
            4. Post Dislike count changed from 0 to 1
        """

        self.client.force_authenticate(user=self.user)

        dislike_request = self.client.patch(
            path=self.post_dislike_request_url
        )

        self.assertEqual(self.test_post.like_count, 0)
        self.assertEqual(self.test_post.dislike_count, 1)
        self.assertEqual(dislike_request.status_code, status.HTTP_200_OK)
        self.assertIn(self.user, self.test_post.post_dislike.user.all())

    def test_comment_create_request_authenticated_user_only(self):
        """
        Testing Unauthorized user cannot comment on a Post. Returns 401 error
        """
        response = self.client.post(
            path=self.comment_create_url,
            data=self.comment_payload
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_create_request_successful(self):
        """
        Authorized user comments on a Post successfully.
            1. Login user
            2. Make Post request to comment create endpoint
            3. Add user to serializer's context
            4. Test serializer returns is_valid=True
            5. Request to endpoint returns 201 Created
            6. requested comment content is equal to
                comment field of Comment object, which is related to the Post.
            7. Test request user is equal to Comment's owner
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            path=self.comment_create_url,
            data=self.comment_payload,
        )
        response.user = self.user
        serializer = PublicCommentCreateSerializer(
            data=self.comment_payload,
            context={'request': response}
        )
        comment = Comment.objects.get(post_id=self.test_post)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data.get('comment'),
            self.test_post.post_commented.first().comment
        )
        self.assertEqual(self.user, comment.commented_by)

    def test_create_comment_validation_error(self):
        """
        Both `Post` and `Replied Comment` cannot be selected.

        """
        self.client.force_authenticate(user=self.user)

        invalid_data = {
            "post": 1,
            "replied_comment": 1,
            "comment": "hello world"
        }

        response = self.client.post(
            path=self.comment_create_url,
            data=invalid_data,
            format='json'
        )
        response.user = self.user
        serializer = PublicCommentCreateSerializer(
            data=invalid_data,
            context={'request': response}
        )
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_comment_owner_only(self):
        """
        Only Comment owner can update the comment:
            1. Create a new comment with a user
            2. Create a second user
            3. Test the second user is created successfully
            4. Try to update without authentication => Unsuccessful
            5. Try after login => Unsuccessful
            6. Try owner => Successful
        """

        # create user
        user_data = {
            "email": "second_user@test.az",
            "password": "password123",
        }
        second_user = create_user(**user_data)

        # test user is created
        self.assertEqual(
            second_user,
            USER.objects.get(email="second_user@test.az")
        )

        # create a Comment object, create new `comment` field data, get url
        comment = Comment.objects.create(
            commented_by=self.user,
            post_id=self.test_post.id,
            replied_comment=None,
            comment='This is new comment!'
        )
        new_comment = {
            "comment": "Testing, comment is updated!"
        }
        comment_update_url = reverse(
            'public_api:public-update-comment',
            kwargs={'pk': comment.id}
        )

        # test unauthorized user can't update
        unauthorized_request = self.client.patch(
            path=comment_update_url,
            format="json",
            data=new_comment
        )
        self.assertEqual(
            unauthorized_request.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # login with the second user and try update
        self.client.force_authenticate(user=second_user)

        second_request = self.client.patch(
            path=comment_update_url,
            format='json',
            data=new_comment,
        )
        self.assertEqual(
            second_request.status_code,
            status.HTTP_403_FORBIDDEN
        )

        # logout, then login with the comment owner
        self.client.logout()
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            path=comment_update_url,
            format='json',
            data=new_comment
        )
        updated_comment = Comment.objects.get(id=comment.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_comment.comment, new_comment.get('comment'))

    def test_comment_delete_method_without_owner(self):
        """
        Only Comment owner and Admin user can delete a comment
            1. Create a new comment with a user
            2. Create a second user
            3. Test the second user is created successfully
            4. Try to update without authentication => Unsuccessful
            5. Try after login => Unsuccessful
            6. Give `Staff (admin)` privilege to user
            7. Try delete => Successful

        """
        # create user
        user_data = {
            "email": "second_user@test.az",
            "password": "password123",
        }
        second_user = create_user(**user_data)

        # test user is created
        self.assertEqual(
            second_user,
            USER.objects.get(email="second_user@test.az")
        )

        # create a Comment object, get url
        comment = Comment.objects.create(
            commented_by=self.user,
            post_id=self.test_post.id,
            replied_comment=None,
            comment='This is new comment!'
        )
        comment_delete_url = reverse(
            'public_api:public-destroy-comment',
            kwargs={'pk': comment.id}
        )

        first_attempt = self.client.delete(comment_delete_url)
        self.assertEqual(
            first_attempt.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.client.force_authenticate(user=second_user)
        second_attempt = self.client.delete(comment_delete_url)
        self.assertEqual(
            second_attempt.status_code,
            status.HTTP_403_FORBIDDEN
        )

        second_user.is_staff = True

        second_user.user_type = 2
        second_user.save()
        successful_attempt = self.client.delete(comment_delete_url)
        self.assertEqual(
            successful_attempt.status_code,
            status.HTTP_403_FORBIDDEN
        )

        second_user.user_type = 3
        second_user.save()
        successful_attempt = self.client.delete(comment_delete_url)
        self.assertEqual(
            successful_attempt.status_code,
            status.HTTP_403_FORBIDDEN
        )

        second_user.user_type = 4
        second_user.save()
        successful_attempt = self.client.delete(comment_delete_url)
        self.assertEqual(
            successful_attempt.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_delete_comment_with_owner(self):
        """
        Delete comment with its owner is successful

        """

        # create a Comment object, get url
        comment = Comment.objects.create(
            commented_by=self.user,
            post_id=self.test_post.id,
            replied_comment=None,
            comment='This is new comment!'
        )
        comment_delete_url = reverse(
            'public_api:public-destroy-comment',
            kwargs={'pk': comment.id}
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(comment_delete_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )


class CommentLikeDislikeRequestApiTests(APITestCase):
    """
    Testing Comment Like and Dislike request endpoints
    """

    def setUp(self):

        keyword = PostIdentifier.objects.create(title="LIVE")

        user_data = {
            "email": "hello@world.com",
            "first_name": "test",
            "last_name": "user"
        }
        self.test_user = create_user(**user_data)
        post_data = {
            "title": "testing",
            "author": self.test_user,
            "keyword": keyword,
            "short_description": "short desc..."
        }
        self.test_post = create_post(**post_data)
        comment_data = {
            "commented_by": self.test_user,
            "post": self.test_post,
            "replied_comment": None,
            "comment": "testing like and dislike request"
        }
        self.test_comment = create_comment(**comment_data)

        self.comment_like_request_url = reverse(
            'public_api:public-like_request',
            kwargs={'pk': self.test_comment.id}
        )
        self.comment_dislike_request_url = reverse(
            'public_api:public-dislike_request',
            kwargs={'pk': self.test_comment.id}
        )
        self.test_comment.comment_dislike.user.add(self.test_user)
        self.assertEqual(self.test_comment.dislike_count, 1)
        self.assertIn(
            self.test_user,
            self.test_comment.comment_dislike.user.all()
        )

    def test_comment_like_request_authenticated_user_only(self):
        """
        Make sure like request accepts only authenticated requests,
        else it throws 401 Unauthenticated error
        """
        response = self.client.patch(
            path=self.comment_like_request_url
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_like_request_successful(self):
        """
        Having done a like request:
            1. user is removed from Comment Dislike list,
            2. Comment Dislike count changed from 1 to 0
            3. user is added to Comment Like list
            4. Comment Like count changed from 0 to 1
        """
        self.client.force_authenticate(user=self.test_user)

        like_response = self.client.patch(
            path=self.comment_like_request_url,
            content_type='application/json',
        )
        self.assertEqual(self.test_comment.dislike_count, 0)
        self.assertEqual(self.test_comment.like_count, 1)
        self.assertEqual(like_response.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.test_user,
            self.test_comment.comment_like.user.all()
        )

    def test_comment_dislike_request_authenticated_user_only(self):
        """
        Make sure dislike request accepts only authenticated requests,
        else it throws 401 Unauthenticated error
        """
        dislike_response = self.client.patch(
            path=self.comment_dislike_request_url
        )
        self.assertEqual(
            dislike_response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_comment_dislike_request_successful(self):
        """
        Having done a dislike request:
            1. user is removed from Comment Like list,
            2. Comment Like count changed from 1 to 0
            3. user is added to Comment Dislike list
            4. Comment Dislike count changed from 0 to 1
        """

        self.client.force_authenticate(user=self.test_user)

        dislike_request = self.client.patch(
            self.comment_dislike_request_url
        )
        self.assertEqual(self.test_comment.like_count, 0)
        self.assertEqual(self.test_comment.dislike_count, 1)
        self.assertEqual(dislike_request.status_code, status.HTTP_200_OK)
        self.assertIn(
            self.test_user,
            self.test_comment.comment_dislike.user.all()
        )


class CategoryApiTests(APITestCase):
    """
    Testing Category API endpoint
    """

    def setUp(self):
        self.category_1 = Category.objects.create(
            title='Politics',
            ordering=0
        )
        self.category_2 = Category.objects.create(
            title='Sport',
            ordering=1
        )
        self.category_3 = Category.objects.create(
            title='Tech',
            ordering=2
        )
        self.category_4 = Category.objects.create(
            title='Elections',
            parent_category=self.category_1,
            ordering=2
        )
        self.url = reverse('public_api:category-list')
        self.sample_data = {
            "title": "Lorem"
        }

    def test_category_listing(self):
        serializer = PublicCategoryListModelSerializer(
            Category.objects.filter(parent_category=None),
            many=True
        )
        response = self.client.get(
            path=self.url
        )

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_create_request_not_allowed(self):

        response = self.client.post(
            path=self.url,
            data=self.sample_data,
            format='json'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_category_update_request_not_allowed(self):

        put_response = self.client.put(
            path=self.url,
            data=self.sample_data,
            format='json'
        )
        patch_response = self.client.patch(
            path=self.url,
            data=self.sample_data,
            format='json'
        )
        self.assertEqual(
            put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
        self.assertEqual(
            patch_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_category_delete_not_allowed(self):

        response = self.client.delete(
            path=self.url,
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
