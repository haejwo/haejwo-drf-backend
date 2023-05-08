from rest_framework.fields import empty
from .models import *
from rest_framework import serializers
from movequotes.models import MoveQuoteReview
from flowerquotes.models import FlowerQuoteReview

class AccountInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountInformation
        fields = ('id', 'company', 'username', 'bankName', 'accountNumber')

class CompanySerializer(serializers.ModelSerializer):
    bank = AccountInformationSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Company
        fields = ('id', 'user','username', 'category', 'bank')


class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
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
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        category = kwargs['context']['category']
        super().__init__(*args, **kwargs)
        if category == 'MOVING':
            self.Meta.model = MoveQuoteReview
        elif category == 'FLOWER':
            self.Meta.model = FlowerQuoteReview
    
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = None
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        role = kwargs['context']['role']
        super().__init__(*args, **kwargs)
        if role == 'CO':
            self.Meta.model = Company
        elif role == 'CU':
            self.Meta.model = Customer