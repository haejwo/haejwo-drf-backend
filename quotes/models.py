from django.db import models
from utils.models import Article, Comment, Review
from accounts.models import Company
from django.conf import settings

REGION_CHOICES = (
    ('SGI', '서울/경기/인천'),
    ('CC', '충청'),
    ('GW', '강원'),
    ('JL', '전라'),
    ('GS', '경상'),
    ('JJ', '제주'),
)

# Create your models here.
class Quote(Article):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_quote')
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_quote')
    start_address = models.CharField(max_length=255)
    end_address = models.CharField(max_length=255)
    start_has_elevator = models.BooleanField(default=False)
    end_has_elevator = models.BooleanField(default=False)

class QuoteComment(Comment):
    article = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='quote_comments')

class QuoteReview(Review):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='quote_reviews')
    article = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('author', 'article')

class Flower(Article):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_flower')
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_flower')
    start_address = models.CharField(max_length=255)
    end_address = models.CharField(max_length=255)
    start_has_elevator = models.BooleanField(default=False)
    end_has_elevator = models.BooleanField(default=False)

class FlowerComment(Comment):
    article = models.ForeignKey(Flower, on_delete=models.CASCADE, related_name='flower_comments')

class FlowerReview(Review):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='flower_reviews')
    article = models.ForeignKey(Flower, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('author', 'article')