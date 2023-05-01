from django.urls import path, include
from rest_framework import routers
from .views import MoveQuoteViewSet, MoveQuoteCommentViewSet

router = routers.DefaultRouter()
router.register('', MoveQuoteViewSet, basename='move')
router.register(r'(?P<article_pk>\d+)/comments', MoveQuoteCommentViewSet, basename='move-comments')

urlpatterns = [
    path('', include(router.urls)),
]