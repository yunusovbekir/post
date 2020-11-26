from django.db import models
from django.utils.translation import ugettext_lazy as _


class Video(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    url = models.URLField(
        _('Url'),
    )
    text = models.TextField(
        _('Content'),
        blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')
