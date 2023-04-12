from rest_framework import serializers
from .models import Quote, Comment

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class QuoteSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Quote
        fields = ['id', 'customer', 'company', 'content', 'created_at', 'is_accepted', 'comments']