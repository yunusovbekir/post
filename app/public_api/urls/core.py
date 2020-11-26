from django.urls import path
from ..views import core as views

urlpatterns = [
    path('settings/', views.SettingsAPIView.as_view(), name='settings'),
    path('settings/social-media/',
         views.SocialMediaListAPIView.as_view(), name='social'),
    path('contact-form/', views.ContactFormCreateAPIView.as_view(),
         name='contact-form'),
    path('opinion/', views.OpinionCreateAPIView.as_view(),
         name='opinion')
]
