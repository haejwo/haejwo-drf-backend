from rest_framework import serializers
from .models import MoveQuote, MoveQuoteComment
from accounts.serializers import UserSerializer

class MoveQuoteCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = MoveQuoteComment
        fields = '__all__'

class MoveQuoteSerializer(serializers.ModelSerializer):
    move_comments = MoveQuoteCommentSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    company = UserSerializer(read_only=True)
    
    class Meta:
        model = MoveQuote
        fields = '__all__'