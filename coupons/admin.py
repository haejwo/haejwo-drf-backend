from django.contrib import admin
from .models import Coupon, CompanyName
# Register your models here.

@admin.register(CompanyName)
class CompanyNameAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active']