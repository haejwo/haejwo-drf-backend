from rest_framework import viewsets
from .models import MoveQuote, MoveQuoteComment, MoveImage
from .serializers import MoveQuoteSerializer, MoveQuoteCommentSerializer
from utils.views import ArticleMixin, CommentMixin
        
class MoveQuoteViewSet(ArticleMixin, viewsets.ModelViewSet):
    serializer_class = MoveQuoteSerializer
    app_role = 'MOVE'
    model = MoveQuote
    image_model = MoveImage

class MoveQuoteCommentViewSet(CommentMixin, viewsets.ModelViewSet):
    serializer_class = MoveQuoteCommentSerializer
    app_role = 'MOVE'
    app_pk = 'article_pk'
    model = MoveQuoteComment
    parent_model = MoveQuote

