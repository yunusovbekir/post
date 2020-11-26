from django.urls import reverse
from rest_framework import status, test
from ..serializers.videos import PublicVideoSerializer
from videos.models import Video


class VideoAPITest(test.APITestCase):

    def setUp(self):

        payload = {
            "title": "Test Story",
            "url": 'https://www.youtube.com/',
            "text": 'Testing text field in video api',
        }

        self.video = Video.objects.create(**payload)
        self.video_url = reverse('public_api:video-list')

    def test_api_returns_video_list(self):

        serializer = PublicVideoSerializer(
            Video.objects.all(),
            many=True
        )
        response = self.client.get(
            path=self.video_url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
