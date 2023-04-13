from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Quote, Comment
from .serializers import QuoteSerializer, CommentSerializer
from django.http import JsonResponse
import requests, os
from dotenv import load_dotenv
load_dotenv()

service_key = os.getenv("KAKAO_REST_API_KEY")

class QuoteViewSet(viewsets.ModelViewSet):
    serializer_class = QuoteSerializer

    def get_queryset(self):
        user = self.request.user
        role = user.role

        # role이 'CO'이고, category가 'moving'인 경우 모든 글 조회
        if role == 'CO' and user.company.category == 'moving':
            queryset = Quote.objects.all()
        else:
            # 본인의 글만 조회
            queryset = Quote.objects.filter(customer=user)
        return queryset

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        # 각 글에 대한 댓글만 조회
        quote_id = self.kwargs['quote_pk']
        queryset = Comment.objects.filter(quote_id=quote_id)
        return queryset

    def create(self, request, *args, **kwargs):
        user = self.request.user
        role = user.role
        category = user.company.category

        # role이 'CO'이고, category가 'moving'인 경우에만 댓글 작성이 가능하도록 처리
        if role == 'CO' and category == 'moving':
            quote_id = kwargs['quote_pk']
            data = request.data.copy()
            data['quote'] = quote_id

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "You do not have permission to create a comment."}, status=status.HTTP_403_FORBIDDEN)
        
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