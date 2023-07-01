from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.shortcuts import redirect
from rest_framework.parsers import FileUploadParser
from google.cloud import vision
from google.cloud.vision_v1 import types
from django.conf import settings
from rest_framework.decorators import parser_classes
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from dotenv import load_dotenv
import requests, secrets, os, json, re
from rest_framework import generics
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from utils.views import CategoryMixin
from rest_framework.permissions import AllowAny

load_dotenv()
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/login/callback/'
KAKAO_CALLBACK_URI = 'http://localhost:3000/oauth/callback/kakao/'
class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer

    def get_object(self):
        user = self.request.user
        try:
            if user.role == 'CO':
                obj = user.company
            else:
                obj = user.customer
        except:
            obj = None
        return obj
    
    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user
        role = user.role
        serializer = self.serializer_class(data=request.data, context={'role': role})
        serializer.is_valid(raise_exception=True)
        company = serializer.save(user=user)
        if role == 'CO':
            if request.FILES.get('image'):
                company.profile_img = request.FILES.get('image')
                company.save()
            account_data = {'company': company.id, 'username': request.data.get('username'), 'bankName': request.data.get('bankName'), 'accountNumber': request.data.get('accountNumber')}
            account_serializer = AccountInformationSerializer(data=account_data)
            account_serializer.is_valid(raise_exception=True)
            account_serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        role = request.user.role
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, context={'role': role})
        serializer.is_valid(raise_exception=True)
        company = serializer.save()
        if role == 'CO':
            if request.FILES.get('image'):
                folder_path = f'media/company/{request.user.pk}/'
                if os.path.exists(folder_path):
                    for file in os.listdir(folder_path):
                        os.remove(os.path.join(folder_path, file))
                company.profile_img = request.FILES.get('image')
                company.save()
            instance = request.user.company.bank
            account_data = {'company': company.id, 'username': request.data.get('username'), 'bankName': request.data.get('bankName'), 'accountNumber': request.data.get('accountNumber')}
            account_serializer = AccountInformationSerializer(instance, data=account_data)
            account_serializer.is_valid(raise_exception=True)
            account_serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        role = self.request.user.role
        context['role'] = role
        return context
    
    def serializer_context(self):
        context = super().serializer_context()
        context['request'] = self.request
        return context


@parser_classes([FileUploadParser])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_businesses_image(request):
    user = request.user
    if user.role == 'CU':
        return Response({'detail':'업체만 이용 가능 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
    if user.company.has_business_license:
        return Response({'detail':'이미 검증된 고객입니다.'}, status=status.HTTP_400_BAD_REQUEST)
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
    b_no, start_dt, p_nm = '', '', ''
    for text in text_list[0].split('\n'):
        text = re.sub(r'\s', '', text).split(':')
        if len(text) > 1:
            if '등록번호' in text[0] and len(text[1].split('-')) == 3 and not b_no:
                for t in text[1].split('-'):
                    b_no += t
            elif text[0] == '명' or '성 명' in text[0] or '대 표 자' in text[0] or '표 자' in text[0] or '자' in text[0]:
                if not p_nm:
                    p_nm += text[1]
            elif '개업연월일' in text[0]:
                text[1] = re.findall(r'\d+', text[1])
                start_dt += "".join(text[1])
        if b_no and start_dt and p_nm:
            break
    if businesses_check(b_no, start_dt, p_nm):
        user.company.has_business_license = True
        user.company.save()
        return Response({'등록번호': b_no, '대표자': p_nm, '개업연월일': start_dt}, status=status.HTTP_200_OK)
    return Response({'detail': '잘못된 사진이거나 올바르지 않은 사업자 등록증 입니다.'}, status=status.HTTP_400_BAD_REQUEST)

def businesses_check(b_no, start_dt, p_nm): #사업자번호, 개업연월일, 대표자 이름
    data = {
        "businesses": [
            {
            "b_no": b_no,
            "start_dt": start_dt,
            "p_nm": p_nm,
            }
        ]
        }
    url = "https://api.odcloud.kr/api/nts-businessman/v1/validate"
    service_key = os.getenv("DATA_KEY")
    response = requests.post(
    url,
    params={"serviceKey": service_key},
    data=json.dumps(data),
    headers={"Content-Type": "application/json", "Accept": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        if result['data'][0].get('status'):
            return True
    return False

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
    GOOGLE_CALLBACK_URI_FRONT = 'http://localhost:3000/oauth/callback/google/'
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
        print(accept_json)
        return JsonResponse(accept_json)
    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(
            f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        print(accept_json)
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
    if not email:
        return JsonResponse({'err_msg': '이메일 동의 없이는 사용이 불가능 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
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
        print(accept_json)
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

class ReviewViewset(CategoryMixin, viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        model, _ = self.get_category()
        queryset = model.objects.all()
        return queryset

    def perform_create(self, serializer):
        article_id = self.request.data.get('article')
        article_model, company = self.get_article()
        article = article_model.objects.get(pk=article_id)
        if article.company:
            if article.company != company.user or article.customer != self.request.user:
                raise ValidationError({'err':'회사가 다르거나 글 작성한 사람이 아닙니다.'})
            article.has_review = True
            article.save()
            author = self.request.user
            serializer.save(article_id=article_id, author=author)
        else:
            raise ValidationError({'err':'매칭이 안됐습니다.'})
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category'] = self.get_category()[1]
        return context

class CompanyList(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [AllowAny]


class AllReviewsList(generics.ListAPIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        flower_reviews = FlowerQuoteReview.objects.all()
        move_reviews = MoveQuoteReview.objects.all()
        all_reviews = flower_reviews.union(move_reviews)
        all_reviews = all_reviews.order_by('-created_at')
        return all_reviews

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ReviewSerializer(queryset, many=True, context={'category':'FLOWER'})
        return Response(serializer.data)
