from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import (
    PermissionsMixin,
    AbstractBaseUser,
)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from .model_managers import MyUserManager
from .options.tools import SOCIAL_MEDIA_CHOICES
from core.options.tools import user_directory_path


class MyUser(AbstractBaseUser, PermissionsMixin):
    """ Custom User model """

    class User_Type(models.IntegerChoices):
        USER = 1
        REPORTER = 2
        EDITOR = 3
        ADMIN = 4

    profession = models.CharField(
        _('Profession'),
        max_length=255,
        null=True,
        blank=True
        )

    user_type = models.IntegerField(
        _('User type'),
        choices=User_Type.choices,
        default=1,
    )
    favorite_category = models.ManyToManyField(
        'news.Category',
        verbose_name=_('Favorite category'),
        blank=True,
    )
    email = models.EmailField(
        _('email address'),
        max_length=255,
        unique=True,
        db_index=True
    )
    first_name = models.CharField(
        _('First Name'),
        max_length=255,
        blank=True
    )
    last_name = models.CharField(
        _('Last Name'),
        max_length=255,
        blank=True
    )
    avatar = models.ImageField(
        verbose_name=_('Avatar'),
        null=True,
        blank=True,
        upload_to=user_directory_path,
    )
    phone_number = models.CharField(
        _('Phone Number'),
        max_length=255,
        blank=True,
    )
    saved_news = models.ManyToManyField(
        'news.Post',
        verbose_name=_('Saved news'),
        related_name='saved_news',
        blank=True,
    )
    preferred_categories = models.ManyToManyField(
        'news.Category',
        verbose_name=_('Preferred Categories'),
        related_name='categories',
        blank=True
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether '
                    'the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.'
                    'Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )
    last_login = models.DateTimeField(
        _('last login'),
        default=timezone.now,
    )

    USERNAME_FIELD = 'email'

    objects = MyUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def user_type_name(self):
        get_type = self.user_type
        if get_type == 1:
            r = 'User'
        elif get_type == 2:
            r = 'Reporter'
        elif get_type == 3:
            r = 'Editor'
        elif get_type == 4:
            r = 'Admin'
        else:
            r = 'type not found'

        return r


class AuthorSocialMediaAccounts(models.Model):

    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name=_('Author'),
        related_name='social_account',
    )
    social_media = models.CharField(
        _('Social Media'),
        max_length=255,
        choices=SOCIAL_MEDIA_CHOICES
    )
    url = models.URLField(
        _('Url')
    )

    def __str__(self):
        return self.author.email

    class Meta:
        verbose_name = _("Author's Social Media Account")
        verbose_name_plural = _("Author's Social Media Accounts")
