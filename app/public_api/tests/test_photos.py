import shutil
import tempfile
from PIL import Image
from django.test import override_settings
from django.urls import reverse
from rest_framework import status, test
from django.core.files import File
from ..serializers.photos import PublicPhotoSerializer
from photos.models import Photo

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoAPITest(test.APITestCase):

    def setUp(self):
        """
        Creating `Photo`
        """
        # create temporary image
        image = Image.new('RGB', (100, 100))
        self.tmp_img = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(self.tmp_img)

        payload = {
            "title": "Test Story",
            "photo": File(image),
        }

        self.photo = Photo.objects.create(**payload)
        self.photo_url = reverse('public_api:photo-list')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_api_returns_photos_list(self):

        serializer = PublicPhotoSerializer(
            Photo.objects.all(),
            many=True
        )
        response = self.client.get(
            path=self.photo_url
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
