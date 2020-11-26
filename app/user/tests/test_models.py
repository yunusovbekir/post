import datetime
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth import get_user_model
from PIL import Image

MyUser = get_user_model()


class TestUserModel(TestCase):

    def create_sample_user(self):

        # create image
        image = Image.new('RGB', (100, 100))
        self.tmp_img = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(self.tmp_img)

        # save to Simple Uploaded File
        upload_image = SimpleUploadedFile('tmp_img.png', self.tmp_img.read())

        user = get_user_model().objects.create_user(
            email='test@gmail.com',
            first_name='example first name',
            last_name='example last name',
            avatar=upload_image,
            is_staff=False,
            is_active=True,
            is_superuser=False,
            date_joined=datetime.datetime(2020, 2, 29, 12, 00),
            last_login=datetime.datetime(2020, 3, 10, 13, 00),
        )
        return user

    def test_create_user(self):

        sample_user = self.create_sample_user()
        self.assertTrue(isinstance(sample_user, MyUser))
