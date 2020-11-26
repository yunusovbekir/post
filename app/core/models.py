from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from .options.tools import POSITION, user_directory_path

USER = get_user_model()


class Settings(models.Model):
    """ Static website settings """

    copyright = models.TextField(
        _('Copyright'),
        blank=True,
    )
    logo = models.FileField(
        _('Website Logo'),
        upload_to=user_directory_path,
    )
    footer_text = models.TextField(
        _('Text on footer section'),
        blank=True,
    )
    footer_social_media_text = models.TextField(
        _('Social media text on footer section'),
        blank=True,
    )
    search_placeholder = models.CharField(
        _('Search placeholder'),
        max_length=255,
        blank=True,
    )
    author_widget_title = models.CharField(
        _('Widget title on authors section'),
        max_length=255,
        blank=True,
    )
    slider_video_title = models.CharField(
        _('Slider video title'),
        max_length=255,
        blank=True,
    )
    slider_button_title = models.CharField(
        _('Slider button title'),
        max_length=255,
        blank=True,
    )
    item_now_playing_text = models.CharField(
        _('Item now playing text'),
        max_length=255,
        blank=True,
    )
    terms_and_conditions = models.TextField(
        _('Terms and Conditions'),
        blank=True,
    )

    def __str__(self):
        return "{}".format('Settings')

    class Meta:
        verbose_name = _('Setting')
        verbose_name_plural = _('Settings')


class SocialMedia(models.Model):
    """ Social Media Accounts Settings """

    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    icon = models.FileField(
        _('Icon'),
        upload_to=user_directory_path,
    )
    link = models.URLField(
        _('Link')
    )
    position = models.CharField(
        _('Position'),
        max_length=255,
        choices=POSITION,
        help_text='Choose the position of the Social Media Logo on the website'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Social Media Setting')
        verbose_name_plural = _('Social Media Settings')


class ContactForm(models.Model):
    """ Messages sent by website users """

    first_name = models.CharField(
        _('First name'),
        max_length=255,
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=255,
    )
    email = models.EmailField(
        _('Email'),
    )
    phone_number = models.CharField(
        _('Phone Number'),
        max_length=255,
        null=True,
    )
    message = models.TextField(
        _('Message'),
    )
    send_date = models.DateTimeField(
        _('Send date'),
        default=timezone.now,
    )

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        verbose_name = _('Contact Form')
        verbose_name_plural = _('Contact Forms')


class Opinion(models.Model):
    """ Opinions sent by website users """

    first_name = models.CharField(
        _('First name'),
        max_length=255,
    )
    last_name = models.CharField(
        _('Last name'),
        max_length=255,
    )
    email = models.EmailField(
        _('Email'),
    )
    message = models.TextField(
        _('Message'),
    )
    send_date = models.DateTimeField(
        _('Send date'),
        default=timezone.now,
    )

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        verbose_name = _('Opinion')
        verbose_name_plural = _('Opinions')


class OneSignal(models.Model):
    user_code = models.CharField(
        _('User Code'),
        max_length=255,
    )
    device_type = models.CharField(
        _('Device type'),
        max_length=255,
    )

    def __str__(self):
        return self.user_code

    class Meta:
        verbose_name = _('One Signal')
        verbose_name_plural = _('One Signal')
