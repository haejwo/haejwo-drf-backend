from rest_framework.fields import empty
from .models import *
from rest_framework import serializers
from movequotes.models import MoveQuoteReview
from flowerquotes.models import FlowerQuoteReview
from django.apps import apps

class AccountInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountInformation
        fields = ('id', 'company', 'username', 'bankName', 'accountNumber')

class CompanySerializer(serializers.ModelSerializer):
    # bank = serializers.SerializerMethodField() # 계좌 정보 숨겨야 할시 사용
    bank = AccountInformationSerializer(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Company
        fields = '__all__'

    # def get_bank(self, obj): # 계좌 정보 숨겨야 할 시 사용
    #     request = self.context.get('request')
    #     if request:
    #         url = request.get_full_path()
    #         url_int = ''
    #         cnt = 2
    #         while url[-cnt].isdigit():
    #             url_int += url[-cnt]
    #             cnt += 1
    #         if url != '/accounts/companies/' and url[-7:] != 'quotes/':
    #             user = request.user
    #             category = obj.category
    #             answer = False
    #             if url_int:
    #                 url_int = int(url_int[::-1])
    #                 model = apps.get_model(app_label=app_labels.get(category, ''), model_name=category.capitalize() + 'Quote')
    #                 article = model.objects.get(pk=url_int)
    #                 if article.customer == user and article.company == obj.user:
    #                     answer = True
    #             if obj.user == user or answer:
    #                 return AccountInformationSerializer(obj.bank).data
    #     return None


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
    
app_labels = {
            'MOVE':'movequotes',
            'FLOWER':'flowerquotes',
        }
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = None
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        category = kwargs['context']['category']
        super().__init__(*args, **kwargs)
        self.Meta.model = apps.get_model(app_label=app_labels.get(category, ''), model_name=category.capitalize() + 'QuoteReview')
    
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