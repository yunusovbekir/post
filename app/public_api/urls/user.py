from django.urls import path
from knox.views import LogoutView
from ..views import user as views

urlpatterns = [
    path('', views.PublicUserListAPIView.as_view(), name='user-list'),
    path('me/', views.PublicUserProfileAPIView.as_view(
        actions={'get': 'retrieve', 'patch': 'update'}
    ), name='user-profile'),
    path('register/', views.PublicUserRegisterAPIView.as_view(),
         name='user-register'),
    path('login/', views.PublicUserLoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='knox_logout'),
    path('password-reset/', views.PublicUserPasswordResetAPIView.as_view(),
         name='password-reset'),
    path('author/',
         views.AuthorProfileViewSet.as_view(actions={'get': 'list'}),
         name='author-profile'),
    path('author/<int:pk>/',
         views.AuthorProfileViewSet.as_view(actions={'get': 'retrieve'}),
         name='author-profile-retrieve'),
    path('author/<int:pk>/posts/',
         views.PublicAuthorPostsAPIView.as_view(),
         name='author-posts'),
    path('saved-posts/', views.PublicUserSavedPostsAPIView.as_view(),
         name='saved-posts'),
]
