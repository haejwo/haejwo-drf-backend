from django.db import models
from utils.models import Article, Comment, Review

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
    start_address = models.CharField(max_length=255)
    end_address = models.CharField(max_length=255)
    start_has_elevator = models.BooleanField(default=False)
    end_has_elevator = models.BooleanField(default=False)

class QuoteComment(Comment):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='comments')

class QuoteReview(Review):
    quote = models.ForeignKey(Quote, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('author', 'quote')
