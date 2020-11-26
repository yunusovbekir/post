from django.db import models
from django.utils.translation import ugettext_lazy as _
from core.options.tools import user_directory_path


class Photo(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    photo = models.ImageField(
        _('Photo'),
        upload_to=user_directory_path,
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'


class Gallery(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        verbose_name=_('Photo')
    )
    description = models.TextField(
        _('Description'),
        blank=True,
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Gallery'
