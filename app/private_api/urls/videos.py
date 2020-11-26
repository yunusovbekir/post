from rest_framework import routers
from django.urls import path, include
from ..views.videos import VideoApiViewSet

router = routers.DefaultRouter()

router.register('videos', VideoApiViewSet, basename='video-api')

urlpatterns = [path('', include(router.urls))]
