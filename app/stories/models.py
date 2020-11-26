from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from news.models import Post
from .options.tools import STATUS_CHOICES, PENDING
from news.options.tools import generate_unique_slug


class Story(models.Model):
    status = models.CharField(
        _('Status'),
        max_length=100,
        choices=STATUS_CHOICES,
        default=PENDING,

    )
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    description = models.CharField(
        _("Description"),
        max_length=255,
        blank=True,
    )
    start_date = models.DateField(
        _("Start date"),
        default=timezone.now
    )
    end_date = models.DateField(
        _("End date"),
        default=timezone.now,
        blank=True,
        null=True,
    )
    show_in_home_page = models.BooleanField(
        verbose_name=_("Show in Home page"),
        default=False
    )
    # bunu sonra photos modeline foreign_key ile baglamaq lazimdir, hele ki o
    # model yoxdur buraya filemanagerdan secilmis sekilin url-ni yazacaqlar,
    # front end terefi bunu js ile edecek
    cover_photo = models.URLField(
        _("Cover Photo"),
    )

    slug = models.SlugField(
        _("Slug"),
        max_length=255,
        blank=True,
        unique=True,
    )
    custom_slug = models.BooleanField(
        default=False
    )
    ordering = models.IntegerField(
        _('Ordering'),
        default=0,
    )
    views = models.BigIntegerField(
        _('Views'),
        default=0,
        help_text=_('The number of views by visitors'),
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        If `description` is not provided,
        get the related Post's `short description`, and save it

        If `Custom_slug` is True, slug can be customized, else get `Title` and
        save to `Slug` field.
        """
        if not self.description and self.storycontent_set.all():
            obj = self.storycontent_set.get(story=self.pk)
            self.description = obj.post.short_description

        if self.slug:  # edit
            if slugify(self.title) != self.slug and not self.custom_slug:
                self.slug = generate_unique_slug(Story, self.title)
        elif not self.custom_slug:  # create
            self.slug = generate_unique_slug(Story, self.title)
        super(Story, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')
        ordering = ('ordering', 'title',)


class StoryContent(models.Model):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        verbose_name=_('Story'),
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Post'),
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.story.title

    class Meta:
        verbose_name = _('Story Content')
        verbose_name_plural = _('Story Contents')
