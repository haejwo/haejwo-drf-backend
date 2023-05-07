from rest_framework import viewsets
from .models import MoveQuote, MoveQuoteComment
from .serializers import MoveQuoteSerializer, MoveQuoteCommentSerializer
from utils.views import ArticleMixin, CommentMixin
        
class MoveQuoteViewSet(ArticleMixin, viewsets.ModelViewSet):
    serializer_class = MoveQuoteSerializer
    app_role = 'MOVING'
    model = MoveQuote

class MoveQuoteCommentViewSet(CommentMixin, viewsets.ModelViewSet):
    serializer_class = MoveQuoteCommentSerializer
    app_role = 'MOVING'
    app_pk = 'article_pk'
    model = MoveQuoteComment
    parent_model = MoveQuote
