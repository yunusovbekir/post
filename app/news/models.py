from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django_elasticsearch_dsl_drf.wrappers import dict_to_obj
from core.options.tools import user_directory_path

from .options.tools import (
    NEWS_STATUS,
    TITLE_TYPES,
    TOP_NEWS,
    CONTENT_TYPES,
    truncate_sentence,
    generate_unique_slug,
)
from photos.models import Photo

USER = get_user_model()


class Category(models.Model):
    """ Post categories """

    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        verbose_name=_('Parent Category'),
        null=True,
        blank=True,
    )
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    url = models.CharField(
        _('URL'),
        max_length=255,
        null=True,
        blank=True,
        help_text="Example /about/ -page url"
    )
    ordering = models.PositiveIntegerField(
        _('Ordering'),
        default=1,
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Category')
        ordering = ('ordering', 'title',)


class Post(models.Model):
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    slug = models.SlugField(
        _('Slug'),
        max_length=255,
        blank=True,
        unique=True,
    )
    custom_slug = models.BooleanField(
        _('Custom Slug'),
        default=False,
    )
    author = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        verbose_name=_('Author'),
        related_name='post_author',
    )
    category = models.ManyToManyField(
        Category,
        verbose_name=_('Category'),
        blank=True,
    )
    keyword = models.ForeignKey(
        'PostIdentifier',
        on_delete=models.CASCADE,
        verbose_name=_('Keyword'),
        null=True,
        blank=True,
    )
    short_description = models.TextField(
        _('Short Description'),
        blank=True,
    )
    title_type = models.CharField(
        _('Title Types'),
        max_length=255,
        choices=TITLE_TYPES,
        default='Plain',
    )
    is_approved = models.BooleanField(
        _('Is approved'),
        default=False,
    )
    is_advertisement = models.BooleanField(
        _('Is advertisement'),
        default=False,
    )
    is_liked_by_auth_user = models.BooleanField(
        verbose_name=_("Liked by Auth User"),
        default=False
    )
    is_disliked_by_auth_user = models.BooleanField(
        verbose_name=_("Disliked by Auth User"),
        default=False
    )
    is_saved_by_auth_user = models.BooleanField(
        verbose_name=_("Saved by Auth User"),
        default=False
    )
    status = models.CharField(
        _('Status'),
        max_length=255,
        choices=NEWS_STATUS,
        default='Open',
    )
    social_meta_title = models.CharField(
        _('Meta tag title for Social Media Sharing'),
        max_length=255,
        blank=True,
        help_text=_('This title will be displayed '
                    'when the post shared the social media'),
    )
    social_meta_description = models.TextField(
        _('Meta tag description for Social Media Sharing'),
        blank=True,
        help_text=_('This description will be displayed '
                    'when the post shared the social media'),
    )
    seo_meta_title = models.CharField(
        _('Meta tag title for SEO'),
        max_length=255,
        blank=True,
    )
    seo_meta_description = models.TextField(
        _('Meta tag description for SEO'),
        blank=True,
    )
    seo_meta_keywords = models.TextField(
        _('Meta tag keywords for SEO'),
        blank=True,
        help_text=_('Keywords for improving SEO ')
    )
    views = models.BigIntegerField(
        _('Views'),
        default=1,
        help_text=_('The number of views by visitors')
    )
    publish_date = models.DateTimeField(
        _('Publish date'),
        default=timezone.now
    )
    end_date = models.DateTimeField(
        _('End date'),
        blank=True,
        null=True
    )
    is_editors_choice = models.BooleanField(
        verbose_name=_("Editor's choice"),
        default=False
    )

    is_multimedia = models.BooleanField(
        verbose_name=_('Multimedia Post'),
        default=False
    )

    show_in_home_page = models.BooleanField(
        verbose_name=_("Show in Home page"),
        default=False
    )
    top_news = models.PositiveIntegerField(
        verbose_name=_('Top news'),
        choices=TOP_NEWS,
        null=True,
        blank=True
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('public_api:post-detail', kwargs={'pk': self.id})

    @property
    def like_count(self):
        try:
            count = self.post_like.user.count()
        except PostLike.DoesNotExist:
            count = 0
        return count

    @property
    def dislike_count(self):
        try:
            count = self.post_dislike.user.count()
        except PostDislike.DoesNotExist:
            count = 0
        return count

    @property
    def author_indexing(self):
        """ Used in Elasticsearch indexing """

        return "{} {}".format(self.author.first_name, self.author.last_name)

    @property
    def category_indexing(self):
        """ Used in Elasticsearch indexing """

        return [category.title for category in self.category.all()]

    @property
    def content_indexing(self):
        for each in self.post_content.all():
            wrapper = dict_to_obj({
                'id': each.id,
                'title': each.title,
                'text': each.text,
                # 'photo': each.photo_indexing,
                # 'video': each.video_indexing,
            })

            return wrapper

    def save(self, *args, **kwargs):
        """
        If `Custom_slug` is True, slug can be customized, else get `Title` and
        save to `Slug` field.
        """
        if self.slug:  # edit
            if slugify(self.title) != self.slug and not self.custom_slug:
                self.slug = generate_unique_slug(Post, self.title)
        elif not self.custom_slug:  # create
            self.slug = generate_unique_slug(Post, self.title)
        # save deletion datetime
        if self.status == 'Closed':
            self.deleted_at = timezone.now()
        super(Post, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-publish_date',)


class Content(models.Model):
    """ Post contents """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Post'),
        related_name='post_content',
    )
    content_type = models.CharField(
        _('Content type'),
        max_length=255,
        choices=CONTENT_TYPES,
        default='Main Text'
    )
    ordering = models.PositiveIntegerField(
        _('Ordering'),
        default=1,
    )
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    text = models.TextField(
        _('Text'),
        blank=True,
    )
    photo = models.ForeignKey(
        Photo,
        on_delete=models.CASCADE,
        verbose_name=_('Photo'),
        null=True,
        blank=True,
    )
    video = models.CharField(
        _('Video'),
        max_length=255,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.post.short_description \
                and self.content_type == 'Main Text':
            post = Post.objects.get(id=self.post_id)
            post.short_description = truncate_sentence(self.text)
            post.save()
        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def photo_indexing(self):
        """ Used in Elasticsearch indexing """
        if self.photo is not None:
            return self.photo.title

    @property
    def video_indexing(self):
        """ Used in Elasticsearch indexing """
        if self.video is not None:
            return self.video.title

    class Meta:
        verbose_name = _('Post Content')
        verbose_name_plural = _('Post Contents')
        ordering = ('ordering', 'title',)


class Comment(models.Model):
    """ Comments written by user on a post on the website """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Post'),
        related_name='post_commented',
        null=True,
        blank=True,
    )
    replied_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        verbose_name=_('Replied Comment'),
        related_name='reply',
        null=True,
        blank=True,
    )
    commented_by = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        verbose_name=_('Commented by'),
        related_name='comment_owner',
    )
    comment = models.TextField(
        _('Comment'),
    )
    post_date = models.DateTimeField(
        default=timezone.now,
    )
    is_approved = models.BooleanField(
        verbose_name=_("Approved"), default=False
    )
    is_liked_by_auth_user = models.BooleanField(
        verbose_name=_("Liked by Auth User"),
        default=False
    )
    is_disliked_by_auth_user = models.BooleanField(
        verbose_name=_("Disliked by Auth User"),
        default=False
    )

    def __str__(self):
        return self.comment

    @property
    def like_count(self):
        try:
            count = self.comment_like.user.count()
        except CommentLike.DoesNotExist:
            count = 0
        return count

    @property
    def dislike_count(self):
        try:
            count = self.comment_dislike.user.count()
        except CommentDislike.DoesNotExist:
            count = 0
        return count

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')


class PostIdentifier(models.Model):
    """ Keywords written with the post titles. Ex: "Sample title - VIDEO" """

    title = models.CharField(
        _('Title'),
        max_length=255,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('Post Identifier')
        verbose_name_plural = _('Post Identifiers')


class Feedback(models.Model):
    """ Feedback given by Website staff """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name=_('Post'),
    )
    owner = models.ForeignKey(
        USER,
        on_delete=models.CASCADE,
        verbose_name=_('Owner'),
    )
    text = models.TextField(
        _('Text'),
    )
    post_date = models.DateTimeField(
        _('Post Date'),
        default=timezone.now,
    )

    def __str__(self):
        return self.post.title

    class Meta:
        verbose_name = _('Feedback')
        verbose_name_plural = _('Feedback')


class PostLike(models.Model):
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name='post_like',
        verbose_name=_('Post'),
    )
    user = models.ManyToManyField(
        USER,
        verbose_name=_('User'),
        blank=True,
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.post.title)

    class Meta:
        verbose_name = _('Post Like')
        verbose_name_plural = _('Post Likes')


class PostDislike(models.Model):
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name='post_dislike',
        verbose_name=_('Post'),
    )
    user = models.ManyToManyField(
        USER,
        verbose_name=_('User'),
        blank=True,
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.post.title)

    class Meta:
        verbose_name = _('Post Dislike')
        verbose_name_plural = _('Post Dislikes')


class CommentLike(models.Model):
    comment = models.OneToOneField(
        Comment,
        on_delete=models.CASCADE,
        related_name='comment_like',
        verbose_name=_('Comment'),
    )
    user = models.ManyToManyField(
        USER,
        verbose_name=_('User'),
        blank=True,
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.comment)

    class Meta:
        verbose_name = _('Comment Like')
        verbose_name_plural = _('Comment Likes')


class CommentDislike(models.Model):
    comment = models.OneToOneField(
        Comment,
        on_delete=models.CASCADE,
        related_name='comment_dislike',
        verbose_name=_('Comment'),
    )
    user = models.ManyToManyField(
        USER,
        verbose_name=_('User'),
        blank=True,
    )

    # logs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.comment.comment)

    class Meta:
        verbose_name = _('Comment Dislike')
        verbose_name_plural = _('Comment Dislikes')


class ScreenShot(models.Model):
    screenshot = models.ImageField(
        _('Photo'),
        upload_to=user_directory_path,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('ScreenShot')
        verbose_name_plural = _('ScreenShots')


class HomePageSectionsSettings(models.Model):
    right_corner_section = models.ForeignKey(
        Category,
        verbose_name=_('Right Corner section category'),
        on_delete=models.CASCADE,
        related_name='right_corner_category',
        null=True

    )
    first_section = models.ForeignKey(
        Category,
        verbose_name=_('First section category'),
        on_delete=models.CASCADE,
        related_name='first_section_category',

    )
    second_section = models.ForeignKey(
        Category,
        verbose_name=_('Second section category'),
        on_delete=models.CASCADE,
        related_name='second_section_category',

    )
    third_section = models.ForeignKey(
        Category,
        verbose_name=_('Third section category'),
        on_delete=models.CASCADE,
        related_name='third_section_category',

    )
    fourth_section = models.ForeignKey(
        Category,
        verbose_name=_('Fourth section category'),
        on_delete=models.CASCADE,
        related_name='fourth_section_category',

    )
    fifth_section = models.ForeignKey(
        Category,
        verbose_name=_('Fifth section category'),
        on_delete=models.CASCADE,
        related_name='fifth_section_category',

    )
    sixth_section = models.ForeignKey(
        Category,
        verbose_name=_('Sixth section category'),
        on_delete=models.CASCADE,
        related_name='sixth_section_category',

    )
    seventh_section = models.ForeignKey(
        Category,
        verbose_name=_('Seventh section category'),
        on_delete=models.CASCADE,
        related_name='seventh_section_category',
        null=True
    )
