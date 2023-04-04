from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .managers import CustomUserManager

# Create your models here.
ROLE_CHOICES = (
        ('CU', '고객'),
        ('CO', '업체'),
        ('AD', '관리자'),
    )

CATEGORY_CHOICES = [
    ('moving', '이사'),
    ('flower', '꽃'),
    ('other', '기타'),
]

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default='CU')
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=20, blank=True)
    
class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='other')

class AccountInformation(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='bank')
    username = models.CharField(max_length=20, blank=True)
    bankName = models.CharField(max_length=20, blank=True)
    accountNumber = models.CharField(max_length=30, blank=True)

class Review(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)