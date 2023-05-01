from rest_framework import serializers
from .models import FlowerQuote, FlowerQuoteComment

class FlowerQuoteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowerQuoteComment
        fields = '__all__'

class FlowerQuoteSerializer(serializers.ModelSerializer):
    flower_comments = FlowerQuoteCommentSerializer(many=True, read_only=True)

    class Meta:
        model = FlowerQuote
        fields = '__all__'