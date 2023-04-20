from rest_framework import serializers
from .models import CompanyName, Coupon, UserCoupon

class CompanyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyName
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    company = CompanyNameSerializer(read_only=True)

    class Meta:
        model = Coupon
        fields = '__all__'

class UserCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)

    class Meta:
        model = UserCoupon
        fields = '__all__'