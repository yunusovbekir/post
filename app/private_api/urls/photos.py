from rest_framework import routers
from django.urls import path, include
from ..views.photos import PhotoApiViewSet, GalleryApiViewSet


router = routers.DefaultRouter()

router.register('photos', PhotoApiViewSet, basename='photo-api')
router.register('gallery', GalleryApiViewSet, basename='gallery-api')

urlpatterns = [path('', include(router.urls))]
