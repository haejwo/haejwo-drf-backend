from django.urls import path, include
from rest_framework import routers
from .views import QuoteViewSet, QuoteCommentViewSet, search_address

router = routers.DefaultRouter()
router.register('', QuoteViewSet, basename='quote')
router.register(r'(?P<quote_pk>\d+)/comments', QuoteCommentViewSet, basename='quote-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('search/address/', search_address, name='search_address'),
]