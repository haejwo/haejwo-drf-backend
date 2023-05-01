from django.urls import path, include
from rest_framework import routers
from .views import FlowerQuoteViewSet, FlowerQuoteCommentViewSet

router = routers.DefaultRouter()
router.register('', FlowerQuoteViewSet, basename='flower')
router.register(r'(?P<article_pk>\d+)/comments', FlowerQuoteCommentViewSet, basename='flower-comments')

urlpatterns = [
    path('', include(router.urls)),
]