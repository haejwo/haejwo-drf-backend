from rest_framework import serializers
from .models import MoveQuote, MoveQuoteComment

class MoveQuoteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoveQuoteComment
        fields = '__all__'

class MoveQuoteSerializer(serializers.ModelSerializer):
    move_comments = MoveQuoteCommentSerializer(many=True, read_only=True)

    class Meta:
        model = MoveQuote
        fields = '__all__'