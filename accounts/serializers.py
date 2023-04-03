from models import *
from rest_framework import serializers

class CompanySerializer(serializers.ModelSerializer):
    review_avg = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'user', 'category', 'review_avg']

    def get_review_avg(self, obj):
        reviews = obj.reviews.all()
        if reviews.count() == 0:
            return 0
        else:
            return sum([review.rating for review in reviews])/reviews.count()