from .models import *
from rest_framework import serializers

class AccountInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountInformation
        fields = ('id', 'company', 'username', 'bankName', 'accountNumber')

class CompanySerializer(serializers.ModelSerializer):
    review_avg = serializers.SerializerMethodField()
    bank = AccountInformationSerializer(read_only=True)
    
    class Meta:
        model = Company
        fields = ('id', 'user','username', 'category', 'review_avg', 'bank')

    def get_review_avg(self, obj):
        reviews = obj.reviews.all()
        if reviews.count() == 0:
            return 0
        else:
            return sum([review.rating for review in reviews])/reviews.count()
        

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'user', 'username')

class UserSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'customer', 'company')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        role = ret['role']
        if role == 'CU':
            ret.pop('company')
        elif role == 'CO':
            ret.pop('customer')
        return ret
    