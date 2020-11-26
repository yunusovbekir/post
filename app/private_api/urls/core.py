from django.urls import path, include
from rest_framework import routers
from ..views import core as views

router = routers.DefaultRouter()

router.register('settings', views.SettingsAPIView, basename='settings-api')
router.register('socialmedia', views.SocialMediaAPIView,
                basename='socialmedia')
router.register('contact-form', views.ContactFormAPIView,
                basename='contact-form')

urlpatterns = [
    path('', include(router.urls)),
]
