from rest_framework import routers

from ..views.stories import PublicStoryViewSet

router = routers.DefaultRouter()

router.register('stories', PublicStoryViewSet, basename='public-story-api')

urlpatterns = router.urls
