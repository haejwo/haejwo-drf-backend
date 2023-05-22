from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('profile', views.ProfileViewSet, basename='profile')
router.register(r'(?P<company_pk>\d+)/reviews', views.ReviewViewset, basename='review')

urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('', include(router.urls)),
    path('signup/', include('dj_rest_auth.registration.urls')),
    path('image-upload/', views.upload_businesses_image),
    path('kakao/login/', views.kakao_login),
    path('kakao/login/callback/', views.kakao_callback),
    path('kakao/login/finish/', views.KakaoLogin.as_view()),
    path('google/login/', views.google_login),
    path('google/login/callback/', views.google_callback),  
    path('google/login/finish/', views.GoogleLogin.as_view()),
    path('companies/', views.CompanyList.as_view()),
]