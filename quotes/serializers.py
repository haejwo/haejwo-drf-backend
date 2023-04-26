from rest_framework import serializers
from .models import Quote, QuoteComment

class QuoteCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteComment
        fields = '__all__'

class QuoteSerializer(serializers.ModelSerializer):
    quote_comments = QuoteCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Quote
        fields = ('id', 'customer', 'company', 'content', 'created_at','start_address','end_address','start_has_elevator','end_has_elevator','date','status', 'quote_comments')