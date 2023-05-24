from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import CustomUserManager

# Create your models here.
ROLE_CHOICES = (
        ('CU', '고객'),
        ('CO', '업체'),
        ('AD', '관리자'),
    )

CATEGORY_CHOICES = [
    ('MOVE', '이사'),
    ('FLOWER', '꽃'),
    ('OTHER', '기타'),
]

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default='CU')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=20, blank=True)

def get_upload_path(instance, filename):
    return f'company/{instance.pk}/{filename}'

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='other')
    profile_img = models.ImageField(upload_to=get_upload_path, blank=True)
    has_business_license = models.BooleanField(default=False)
    has_cdl = models.BooleanField(default=False)

class AccountInformation(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='bank')
    username = models.CharField(max_length=20, blank=True)
    bankName = models.CharField(max_length=20, blank=True)
    accountNumber = models.CharField(max_length=30, blank=True)
