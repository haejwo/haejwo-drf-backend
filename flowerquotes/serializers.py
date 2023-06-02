from rest_framework import serializers
from .models import FlowerQuote, FlowerQuoteComment, FlowerImage
from accounts.serializers import UserSerializer

class FlowerImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = FlowerImage
        fields = '__all__'

class FlowerQuoteCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = FlowerQuoteComment
        fields = '__all__'

class FlowerQuoteSerializer(serializers.ModelSerializer):
    flower_comments = FlowerQuoteCommentSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    company = UserSerializer(read_only=True)
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        image = obj.flower_images.all()
        return FlowerImageSerializer(instance=image, many=True, context=self.context).data

    class Meta:
        model = FlowerQuote
        fields = '__all__'