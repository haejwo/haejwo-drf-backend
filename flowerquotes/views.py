from rest_framework import viewsets
from .models import FlowerQuote, FlowerQuoteComment
from .serializers import FlowerQuoteSerializer, FlowerQuoteCommentSerializer
from utils.views import ArticleMixin, CommentMixin
        
class FlowerQuoteViewSet(ArticleMixin, viewsets.ModelViewSet):
    serializer_class = FlowerQuoteSerializer
    app_role = 'FLOWER'
    model = FlowerQuote

class FlowerQuoteCommentViewSet(CommentMixin, viewsets.ModelViewSet):
    serializer_class = FlowerQuoteCommentSerializer
    app_role = 'FLOWER'
    app_pk = 'article_pk'
    model = FlowerQuoteComment
    parent_model = FlowerQuote

