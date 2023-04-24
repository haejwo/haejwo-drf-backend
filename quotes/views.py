from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Quote, QuoteComment
from .serializers import QuoteSerializer, QuoteCommentSerializer
from django.http import JsonResponse
import requests, os
from dotenv import load_dotenv
load_dotenv()

service_key = os.getenv("KAKAO_REST_API_KEY")

class ArticleMixin:
    app_role = None
    model = None

    def get_queryset(self):
        user = self.request.user
        role = user.role

        if role == 'CO' and user.company.category == self.app_role:
            queryset = self.model.objects.all()
        else:
            queryset = self.model.objects.filter(customer=user)
        return queryset
    
    @action(detail=True, methods=['post'])
    def deposit(self, request, *args, **kwargs):
        article_id = self.kwargs['pk']
        article = self.model.objects.get(pk=article_id)
        if article.customer == request.user:
            article.status = 'DEPOSIT'
            article.save()
            return Response({"detail": "입금 완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def preparing(self, request, *args, **kwargs):
        article_id = self.kwargs['pk']
        article = self.model.objects.get(pk=article_id)
        if article.company == request.user:
            article.status = 'PREPARING'
            article.save()
            return Response({"detail": "확정 후, 준비중"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
    @action(detail=True, methods=['post'])
    def completed(self, request, *args, **kwargs):
        article_id = self.kwargs['pk']
        article = self.model.objects.get(pk=article_id)
        if article.company == request.user:
            article.status = 'COMPLETED'
            article.save()
            return Response({"detail": "완료"}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
    
class CommentMixin:
    app_role = None
    app_pk = None
    model = None
    parent_model = None

    def get_queryset(self):
        # 각 글에 대한 댓글만 조회
        parent_id = self.kwargs[self.app_pk]
        parent = self.parent_model.objects.get(pk=parent_id)
        queryset = parent.comments.all()
        return queryset

    def create(self, request, *args, **kwargs):
        parent_id = self.kwargs[self.app_pk]
        parent = self.parent_model.objects.get(pk=parent_id)
        queryset = parent.comments.filter(author=request.user)
        if queryset.exists():
            # 이미 댓글이 존재하는 경우, 해당 댓글을 수정
            instance = queryset.first()
            data = request.data
            serializer = self.get_serializer(instance, data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            # 새로운 댓글 작성
            role = request.user.role
            category = request.user.company.category

            if role == 'CO' and category == self.app_role:
                data = request.data
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
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
        
class QuoteViewSet(ArticleMixin, viewsets.ModelViewSet):
    serializer_class = QuoteSerializer
    app_role = 'MOVING'
    model = Quote

class QuoteCommentViewSet(CommentMixin, viewsets.ModelViewSet):
    serializer_class = QuoteCommentSerializer
    app_role = 'MOVING'
    app_pk = 'quote_pk'
    model = QuoteComment
    parent_model = Quote

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