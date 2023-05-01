from django.db import models
from utils.models import Article, Comment, Review
from accounts.models import Company
from django.conf import settings

# Create your models here.

class MoveQuote(Article):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_move')
    company = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='company_move')
    start_address = models.CharField(max_length=255)
    end_address = models.CharField(max_length=255)
    start_has_elevator = models.BooleanField(default=False)
    end_has_elevator = models.BooleanField(default=False)

class MoveQuoteComment(Comment):
    article = models.ForeignKey(MoveQuote, on_delete=models.CASCADE, related_name='move_comments')

class MoveQuoteReview(Review):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='move_reviews')
    article = models.ForeignKey(MoveQuote, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('author', 'article')