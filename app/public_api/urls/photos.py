from django.urls import path

from ..views.photos import (
    PublicPhotoViewSet,
)

urlpatterns = [
    path('', PublicPhotoViewSet.as_view({'get': 'list'}),
         name='photo-list'),
]
