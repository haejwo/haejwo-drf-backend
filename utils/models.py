from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Company

# Create your models here.

STATUS_CHOICES = (
        ('MATCHING', '매칭전'),
        ('MATCHED', '매칭완료'),
        ('DEPOSIT', '입금완료'),
        ('PREPARING', '준비중'),
        ('COMPLETED', '완료'),
    )

class Article(models.Model):
    title = models.CharField(max_length=30, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='MATCHING')
    has_review = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ['amount']

class Review(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.article:
            self.article.has_review = True
            self.article.save()