from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from ..serializers.stories import PublicStorySerializer
from stories.models import Story


def create_story(**payload):
    return Story.objects.create(**payload)


class StoryAPITest(APITestCase):
    """ Endpoint should return only active stories """

    def setUp(self):
        """
        Creating `Story`
        """
        story_data = {
            "title": "Test Story",
            "description": "Test Description",
            "cover_photo": "testurl.url",
        }
        self.pending_story = create_story(**story_data)

        story_data.update({'status': 'ACTIVE'})

        self.active_story = create_story(**story_data)

    def test_api_story_list_endpoint(self):
        """ Public Story list endpoint should return only active stories """

        story_list_url = reverse('public_api:public-story-api-list')
        all_stories = PublicStorySerializer(Story.objects.all(), many=True)
        active_stories = PublicStorySerializer(
            Story.objects.filter(status='ACTIVE'), many=True
        )
        response = self.client.get(story_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data, all_stories.data)
        self.assertEqual(response.data, active_stories.data)

    def test_api_story_retrieve_endpoint(self):
        """ Public Story Retrieve endpoint should return only active story """

        pending_story_detail_url = reverse(
            'public_api:public-story-api-detail',
            kwargs={'pk': self.pending_story.id}
        )
        active_story_detail_url = reverse(
            'public_api:public-story-api-detail',
            kwargs={'pk': self.active_story.id}
        )
        active_story = PublicStorySerializer(
            Story.objects.filter(status='ACTIVE').last()
        )
        response_pending = self.client.get(pending_story_detail_url)
        response_active = self.client.get(active_story_detail_url)

        self.assertEqual(
            response_pending.status_code, status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(
            response_active.status_code, status.HTTP_200_OK
        )

        self.assertEqual(response_active.data, active_story.data)
