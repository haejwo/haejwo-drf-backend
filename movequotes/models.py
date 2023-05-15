from django.db import models
from utils.models import Article, Comment, Review
from accounts.models import Company
from django.conf import settings

# Create your models here.
SIZE_CHOICES = (
    ('SMALL', '소형(20평미만)'),
    ('BIG', '대형(20평이상)'),
)
PACKING_CHOICES = (
    ('PACKING', '포장'),
    ('NORMAL', '일반'),
    ('SEMIPACKING', '반포장'),
)
class MoveQuote(Article):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_move')
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_move')
    size_type = models.CharField(max_length=20, choices=SIZE_CHOICES, default='SMALL')
    packing_type = models.CharField(max_length=20, choices=PACKING_CHOICES, default='PACKING')
    customer_support = models.BooleanField(default=False)
    start_info = models.JSONField(default=dict)
    end_info = models.JSONField(default=dict)
    luggage_info = models.JSONField(default=dict)

class MoveQuoteComment(Comment):
    article = models.ForeignKey(MoveQuote, on_delete=models.CASCADE, related_name='move_comments')

class MoveQuoteReview(Review):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='move_reviews')
    article = models.ForeignKey(MoveQuote, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('author', 'article')

def get_upload_path(instance, filename):
    return f'/movequote/{instance.article.id}/{filename}'

class MoveImage(models.Model):
    article = models.ForeignKey(MoveQuote, on_delete=models.CASCADE, related_name='move_images')
    image = models.ImageField(upload_to=get_upload_path)

    def __int__(self):
        return self.id