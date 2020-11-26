from rest_framework import routers
from django.urls import path, include
from ..views.stories import StoryViewSet, StoryContentViewSet

router = routers.DefaultRouter()

router.register('stories', StoryViewSet, basename='story-api')
router.register('story-contents', StoryContentViewSet,
                basename='story-content-api')

urlpatterns = [path('', include(router.urls))]
