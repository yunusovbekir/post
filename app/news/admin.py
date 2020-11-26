from django.contrib import admin
from .models import (
    Post,
    Content,
    PostIdentifier,
    Category,
    Comment,
    Feedback,
    PostLike,
    PostDislike,
    CommentLike,
    CommentDislike,
    HomePageSectionsSettings,
    ScreenShot
)


class ContentAdminTabularInline(admin.StackedInline):
    model = Content
    extra = 0


class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = (
        'title',
        'author',
        'is_editors_choice',
        'is_multimedia',
        'top_news',
        'is_approved',
        'show_in_home_page',
        'publish_date',
    )
    inlines = (ContentAdminTabularInline,)


class PostContentAdmin(admin.ModelAdmin):
    model = Content
    list_display = (
        'post',
        'title',
        'content_type',
        'ordering',
    )


class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = (
        'post',
        'replied_comment',
        'commented_by',
        'comment',
    )


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = (
        'title',
        'parent_category',
        'ordering',
    )


class HomePageSectionsSettingsAdmin(admin.ModelAdmin):
    model = HomePageSectionsSettings
    list_display = (
        'first_section',
        'second_section',
        'third_section',
        'fourth_section',
        'fifth_section',
        'sixth_section'
    )


class FeedbackAdmin(admin.ModelAdmin):
    model = Feedback
    list_display = (
        'post',
        'owner',
        'post_date',
        'text',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Content, PostContentAdmin)
admin.site.register(PostIdentifier)
admin.site.register(Category, CategoryAdmin)

admin.site.register(HomePageSectionsSettings, HomePageSectionsSettingsAdmin)

admin.site.register(Comment, CommentAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(PostLike)
admin.site.register(PostDislike)
admin.site.register(CommentLike)
admin.site.register(CommentDislike)
admin.site.register(ScreenShot)
