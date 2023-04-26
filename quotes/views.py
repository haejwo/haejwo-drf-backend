from rest_framework import viewsets
from .models import Quote, QuoteComment
from .serializers import QuoteSerializer, QuoteCommentSerializer
from utils.views import ArticleMixin, CommentMixin
from django.http import JsonResponse
        
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
