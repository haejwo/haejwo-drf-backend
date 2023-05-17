from rest_framework import serializers
from .models import MoveQuote, MoveQuoteComment, MoveImage
from accounts.serializers import UserSerializer

class MoveImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = MoveImage
        fields = '__all__'

class MoveQuoteCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = MoveQuoteComment
        fields = '__all__'

class MoveQuoteSerializer(serializers.ModelSerializer):
    move_comments = MoveQuoteCommentSerializer(many=True, read_only=True)
    customer = UserSerializer(read_only=True)
    company = UserSerializer(read_only=True)
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        image = obj.move_images.all()
        return MoveImageSerializer(instance=image, many=True, context=self.context).data

    class Meta:
        model = MoveQuote
        fields = '__all__'

