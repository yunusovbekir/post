from django.contrib import admin
from .models import Story
from .models import StoryContent


class StoryAdmin(admin.ModelAdmin):
    model = Story
    list_display = ('title', 'status', 'slug', 'description',)
    readonly_fields = ('id',)


class StoryContentAdmin(admin.ModelAdmin):
    model = StoryContent
    list_display = ('story', 'post',)


admin.site.register(Story, StoryAdmin)
admin.site.register(StoryContent, StoryContentAdmin)
