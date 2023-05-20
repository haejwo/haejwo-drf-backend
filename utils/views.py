from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import requests, os
from django.apps import apps
from accounts.models import Company
from dotenv import load_dotenv
load_dotenv()
# Create your views here.

service_key = os.getenv("KAKAO_REST_API_KEY")

class ArticleMixin:
    app_role = None
    model = None
    image_model = None

    def get_queryset(self):
        user = self.request.user
        role = user.role

        if role == 'CO' and user.company.category == self.app_role:
            queryset = self.model.objects.all()
        else:
            queryset = self.model.objects.filter(customer=user)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article = serializer.save(customer=request.user)
        image_set = request.FILES
        for image_data in image_set.getlist('image'):
            self.image_model.objects.create(article=article, image=image_data)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update_article_status(self, article_id, status):
        article = self.model.objects.get(pk=article_id)
        if article.company == self.request.user:
            article.status = status
            article.save()
            return Response({"detail": "상태가 변경되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def deposit(self, request, *args, **kwargs):
        return self.update_article_status(self.kwargs['pk'], 'DEPOSIT')

    @action(detail=True, methods=['post'])
    def preparing(self, request, *args, **kwargs):
        return self.update_article_status(self.kwargs['pk'], 'PREPARING')

    @action(detail=True, methods=['post'])
    def completed(self, request, *args, **kwargs):
        return self.update_article_status(self.kwargs['pk'], 'COMPLETED')

class CommentMixin:
    app_role = None
    app_pk = None
    model = None
    parent_model = None

    def get_queryset(self):
        # 각 글에 대한 댓글만 조회
        parent_id = self.kwargs[self.app_pk]
        queryset = self.model.objects.filter(article_id=parent_id)
        return queryset

    def create(self, request, *args, **kwargs):
        queryset = self.model.objects.filter(article_id=kwargs['article_pk'],author=request.user)
        data = request.data.copy()
        data['article'] = kwargs['article_pk']
        if queryset.exists():
            # 이미 댓글이 존재하는 경우, 해당 댓글을 수정
            instance = queryset.first()
        
            serializer = self.get_serializer(instance, data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            # 새로운 댓글 작성
            role = request.user.role
            category = request.user.company.category
            if role == 'CO' and category == self.app_role:
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save(author=request.user)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def matching(self, request, *args, **kwargs):
        parent_id = self.kwargs[self.app_pk]
        parent = self.parent_model.objects.get(pk=parent_id)
        if parent.customer == request.user:
            comment_id = self.kwargs['pk']
            comment = self.model.objects.get(pk=comment_id)
            parent.company = comment.author
            parent.status = 'MATCHED'
            parent.save()
            return Response({"detail": "매칭 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

def search_address(request):
    query = request.GET.get('address')
    if not query:
        return Response({"detail": "주소를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {service_key}"
    }
    params = {
        "query": query
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json().get('documents')
    if data:
        if len(data) == 1:
            address_data = data[0]
            road_data = address_data.get('road_address')
            road_address = road_data.get('address_name') if road_data else ''
            zip_code = road_data.get('zone_no') if road_data else ''
            old_address = address_data.get('address').get('address_name', '')
            return Response({
                "road_address": road_address,
                "zip_code": zip_code,
                "old_address": old_address
            }, status=status.HTTP_200_OK)
        else:
            result = [i.get('address_name') for i in data]
            return Response({"result": result}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "검색 결과가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)


app_labels = {
            'MOVE':'movequotes',
            'FLOWER':'flowerquotes',
        }

class CategoryMixin:
    def get_company(self):
        company = Company.objects.get(pk=self.kwargs['company_pk'])
        category = company.category
        app_label = app_labels.get(category, '')
        return app_label, category, company

    def get_category(self):
        app_label, category, _ = self.get_company()
        model = apps.get_model(app_label=app_label, model_name=category.capitalize() + 'QuoteReview')
        return model, category
    
    def get_article(self):
        app_label, category, company = self.get_company()
        model = apps.get_model(app_label=app_label, model_name=category.capitalize() + 'Quote')
        return model, company