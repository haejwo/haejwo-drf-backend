from django.urls import path, include
from rest_framework import routers
from .views import ProfileViewSet, image

router = routers.DefaultRouter()
router.register('', ProfileViewSet)

urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('profile/', include(router.urls)),
    path('signup/', include('dj_rest_auth.registration.urls')),
    path('image-upload/', image),
]