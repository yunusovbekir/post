from django.urls import path, include
from ..views import news as views
from rest_framework import routers

router = routers.DefaultRouter()

router.register('content', views.ContentApiView, basename='content-api')
router.register('categories', views.CategoryApiView)
router.register('feedback', views.FeedbackApiView, basename='feedback-api')
router.register('post-identifier', views.PostIdentifierApiView,
                basename='post-identifier-api')
router.register('post-like', views.PostLikeViewSet, basename='postlike-api')
router.register('post-dislike', views.PostDislikeViewSet,
                basename='postdislike-api')
router.register('comments', views.CommentApiViewSet, basename='comment-api')
router.register('comment-like', views.CommentLikeViewSet,
                basename='comment-like-api')
router.register('comment-dislike', views.CommentDislikeViewSet,
                basename='comment-dislike-api')


POST_URLS = [
    path('list/', views.PostApiView.as_view(actions={'get': 'list'}),
         name='post-list'),
    path('<int:pk>/', views.PostApiView.as_view(actions={'get': 'retrieve'}),
         name='post-retrieve'),
    path('create/', views.PostApiView.as_view(actions={'post': 'create'}),
         name='post-create'),
    path('<int:pk>/update-non-approved/', views.PostApiView.as_view(
        actions={'patch': 'update_non_approved'}),
         name='update-non-approved-post'),
    path('<int:pk>/update-approved/', views.PostApiView.as_view(
        actions={'patch': 'update_approved'}),
         name='update-approved-post'),
    path('<int:pk>/delete/', views.PostApiView.as_view(
        actions={'delete': 'destroy'}),
         name='post-delete'),
    path('options/', views.OptionsApiView.as_view(actions={'get': 'options'}),
         name='post-options'),
]

urlpatterns = [path('', include(router.urls))] + POST_URLS
