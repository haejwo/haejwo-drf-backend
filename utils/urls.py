from django.urls import path, include

from .views import search_address

urlpatterns = [
    path('search/address/', search_address, name='search_address'),
]