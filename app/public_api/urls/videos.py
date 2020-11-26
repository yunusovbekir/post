from django.urls import path

from ..views.videos import (
    PublicVideosViewSet,
)

urlpatterns = [
    path('', PublicVideosViewSet.as_view({'get': 'list'}),
         name='video-list'),
]
