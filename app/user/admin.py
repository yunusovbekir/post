from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import AuthorSocialMediaAccounts
User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser',
    )


class SocialMediaAdmin(admin.ModelAdmin):

    model = AuthorSocialMediaAccounts
    list_display = (
        'author',
        'social_media',
        'url',
    )


admin.site.register(User, UserAdmin)
admin.site.register(AuthorSocialMediaAccounts, SocialMediaAdmin)
