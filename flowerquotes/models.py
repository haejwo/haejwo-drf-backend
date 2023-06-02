from django.db import models
from utils.models import Article, Comment, Review
from accounts.models import Company
from django.conf import settings

# Create your models here.

class FlowerQuote(Article):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_flower')
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_flower')
    end_address = models.CharField(max_length=255)

class FlowerQuoteComment(Comment):
    article = models.ForeignKey(FlowerQuote, on_delete=models.CASCADE, related_name='flower_comments')

class FlowerQuoteReview(Review):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='flower_reviews')
    article = models.ForeignKey(FlowerQuote, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('author', 'article')

def get_upload_path(instance, filename):
    return f'flowerquote/{instance.article.id}/{filename}'

class FlowerImage(models.Model):
    article = models.ForeignKey(FlowerQuote, on_delete=models.CASCADE, related_name='flower_images')
    image = models.ImageField(upload_to=get_upload_path)