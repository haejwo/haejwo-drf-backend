from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('', views.ProfileViewSet)

urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('profile/', include(router.urls)),
    path('signup/', include('dj_rest_auth.registration.urls')),
    path('image-upload/', views.image),
    path('kakao/login/', views.kakao_login),
    path('kakao/login/callback/', views.kakao_callback),
    path('kakao/login/finish/', views.KakaoLogin.as_view()),
    path('google/login/', views.google_login),
    path('google/login/callback/', views.google_callback),  
    path('google/login/finish/', views.GoogleLogin.as_view()),
]