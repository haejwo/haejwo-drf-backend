from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.shortcuts import redirect
from rest_framework.parsers import FileUploadParser
from google.cloud import vision
from google.cloud.vision_v1 import types
from django.conf import settings
import os
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import parser_classes
from rest_framework.parsers import FileUploadParser
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import requests, secrets

BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/login/callback/'
KAKAO_CALLBACK_URI = BASE_URL + 'accounts/kakao/login/callback/'

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        user = request.user
        role = user.role

        # CU role인 경우 Customer 객체 생성
        if role == 'CU':
            customer_data = {'user': user.id, 'username': request.data.get('username')}
            customer_serializer = CustomerSerializer(data=customer_data)
            if customer_serializer.is_valid():
                customer_serializer.save()
                serializer = self.get_serializer(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(customer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # CO role인 경우 Company 객체 생성
        elif role == 'CO':
            company_data = {'user': user.id, 'username': request.data.get('username'), 'category': request.data.get('category')}
            company_serializer = CompanySerializer(data=company_data)
            if company_serializer.is_valid():
                company = company_serializer.save()

                # Company 객체와 연결된 AccountInformation 객체 생성
                account_data = {'company': company.id, 'username': request.data.get('username'), 'bankName': request.data.get('bankName'), 'accountNumber': request.data.get('accountNumber')}
                account_serializer = AccountInformationSerializer(data=account_data)
                if account_serializer.is_valid():
                    account_serializer.save()
                    serializer = self.get_serializer(user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # AccountInformation 생성 실패시 Company 객체 삭제
                    company.delete()
                    return Response(account_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(company_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

@parser_classes([FileUploadParser])
@csrf_exempt
def image(request):
    BASE_DIR = settings.BASE_DIR
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(BASE_DIR,"secret.json")
    file_obj = request.FILES.get('image')
    image = types.Image(content=file_obj.read())
    client = vision.ImageAnnotatorClient()

    response = client.text_detection(image=image)
    texts = response.text_annotations
    text_list = list(map(lambda x: x.description, texts))
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    print(text_list)
    return JsonResponse({'text': text_list})

def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    state = secrets.token_urlsafe(16) # 16자리 무작위 문자열 생성
    request.session['state'] = state # state 값을 세션에 저장
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}&state={state}")

def google_callback(request):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOCLE_CLIENT_SECRET")
    code = request.GET.get('code')
    GOOGLE_CALLBACK_URI_FRONT = GOOGLE_CALLBACK_URI
    state = request.GET.get('state')
    session_state = request.session.get('state') # 세션에서 state 값을 가져옴
    if state != session_state:
        return JsonResponse({'err_msg': 'invalid state'}, status=status.HTTP_400_BAD_REQUEST)
    del request.session['state']
    token_req = requests.post(
        f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI_FRONT}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')

    # Access Token으로 Email 값을 Google에게 요청
    """
    Email Request
    """
    email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code
    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    email_req_json = email_req.json()
    email = email_req_json.get('email')
    # 전달받은 Email, Access Token, Code를 바탕으로 회원가입/로그인 진행
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Google로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        print(accept)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        return JsonResponse(accept_json)

class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client

#백에서 테스트용으로 사용 / 프론트는 callback 주소만 사용
def kakao_login(request):
    rest_api_key = os.getenv("KAKAO_REST_API_KEY")
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


def kakao_callback(request):
    rest_api_key = os.getenv("KAKAO_REST_API_KEY")
    code = request.GET.get("code")
    redirect_uri = KAKAO_CALLBACK_URI
    """ 
    Access Token Request
    """
    token_req = requests.get(
        f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={rest_api_key}&redirect_uri={redirect_uri}&code={code}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get("access_token")
    """
    Email Request
    """
    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
    profile_json = profile_request.json()
    kakao_account = profile_json.get('kakao_account')
    """
    kakao_account에서 이메일 외에
    카카오톡 프로필 이미지, 배경 이미지 url 가져올 수 있음
    print(kakao_account) 참고
    """
    # print(kakao_account)
    email = kakao_account.get('email')
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        social_user = SocialAccount.objects.get(user=user)
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'kakao':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Google로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
        accept_json = accept.json()
        return JsonResponse(accept_json)
        
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        # user의 pk, email, first name, last name과 Access Token, Refresh token 가져옴
        accept_json = accept.json()
        print(accept_json)  
        return JsonResponse(accept_json)
    
class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client