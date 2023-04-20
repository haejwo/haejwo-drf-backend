from django.db import models
from django.conf import settings

# Create your models here.

DISCOUNT_TYPE_PERCENTAGE = 'PERCENTAGE'
DISCOUNT_TYPE_FIXED_AMOUNT = 'FIXED_AMOUNT'
DISCOUNT_TYPES = [
    (DISCOUNT_TYPE_PERCENTAGE, 'Percentage'),
    (DISCOUNT_TYPE_FIXED_AMOUNT, 'Fixed Amount'),
]
class CompanyName(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Coupon(models.Model):
    company = models.ForeignKey(CompanyName, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

class UserCoupon(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    used_date = models.DateTimeField(null=True, blank=True)