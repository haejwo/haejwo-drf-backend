from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Quote, Comment
from .serializers import QuoteSerializer, CommentSerializer

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
            # quote_id를 request.data의 복사본에 추가하여 댓글 작성
            quote_id = kwargs['quote_pk']
            data = request.data.copy()
            data['quote'] = quote_id

            # 시리얼라이저를 사용하여 데이터를 직렬화하고 저장
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({"detail": "You do not have permission to create a comment."}, status=status.HTTP_403_FORBIDDEN)