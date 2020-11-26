from django.urls import path, include
from rest_framework import routers
from knox.views import LogoutView
from ..views import user as views

router = routers.DefaultRouter()

router.register('social-account', views.AuthorSocialMediaViewSet,
                basename='social-account')
router.register('', views.PrivateUserApiView,
                basename='private-user-api')

urlpatterns = [
    path('register/', views.PrivateUserAddAPIView.as_view(),
         name='user-register'),
    path('types/', views.ChoiceApiView.as_view(),
         name='user-types'),
    path('login/', views.PrivateUserLoginAPIView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='knox_logout'),
    path('accounts/', include(router.urls))
]
