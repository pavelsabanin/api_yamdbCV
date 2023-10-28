from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (UserViewSet, get_jwt_token, send_confirmation_code)
from django.urls import include, path
from rest_framework.routers import DefaultRouter


from api import views
from .views import CategoryViewSet, GenreViewSet, TitleViewSet

reviews_url = r'titles/(?P<title_id>\d+)/reviews' 
comments_url = rf'{reviews_url}/(?P<review_id>\d+)/comments'

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet)
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(reviews_url, views.ReviewViewSet, basename='reviews') 
v1_router.register(comments_url, views.CommentViewSet, basename='comments')


v1_auth_patterns = [
    path('signup/', send_confirmation_code, name='send_confirmation_code'),
    path('token/', get_jwt_token, name='get_token'),
]
urlpatterns = [
    path('v1/auth/', include(v1_auth_patterns)),
    path('v1/', include(v1_router.urls))
]
