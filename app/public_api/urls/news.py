from django.urls import path

from ..views.news import (
    PublicPostViewSet,
    CommentViewSet,
    CategoryListApiView,
)

POST_URL_PATTERNS = [
    path('posts/',
         PublicPostViewSet.as_view(actions={"get": "list"}),
         name='public-post-list'),
    path('posts/<int:pk>/',
         PublicPostViewSet.as_view(actions={'get': 'retrieve'}),
         name='public-post-detail'),
    path('posts/<int:pk>/like/',
         PublicPostViewSet.as_view(actions={'patch': 'like_request'}),
         name='public-post-like-request'),
    path('posts/<int:pk>/dislike/',
         PublicPostViewSet.as_view(actions={'patch': 'dislike_request'}),
         name='public-post-dislike-request'),
]

COMMENT_URL_PATTERNS = [
    path('posts/comments/',
         CommentViewSet.as_view(actions={'post': 'create'}),
         name='public-create-comment'),
    path('posts/comments/<int:pk>/',
         CommentViewSet.as_view(actions={'patch': 'update_comment'}),
         name='public-update-comment'),
    path('posts/comments/<int:pk>/delete/',
         CommentViewSet.as_view(actions={'delete': 'destroy'}),
         name='public-destroy-comment'),
    path('posts/comments/<int:pk>/like/',
         CommentViewSet.as_view(actions={'patch': 'like_request'}),
         name='public-like_request'),
    path('posts/comments/<int:pk>/dislike/',
         CommentViewSet.as_view(actions={'patch': 'dislike_request'}),
         name='public-dislike_request')
]

CATEGORY_URL_PATTERNS = [
    path('categories/', CategoryListApiView.as_view(), name='category-list'),
]

urlpatterns = [] + POST_URL_PATTERNS + COMMENT_URL_PATTERNS +\
              CATEGORY_URL_PATTERNS
