from django.db import models
from django.conf import settings

REGION_CHOICES = (
    ('SGI', '서울/경기/인천'),
    ('CC', '충청'),
    ('GW', '강원'),
    ('JL', '전라'),
    ('GS', '경상'),
    ('JJ', '제주'),
)
STATUS_CHOICES = (
        ('MATCHING', '매칭전'),
        ('MATCHED', '매칭완료'),
        ('DEPOSIT', '입금완료'),
        ('PREPARING', '준비중'),
        ('COMPLETED', '완료'),
    )
# Create your models here.
class Quote(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='quotes_as_company', null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField()
    start_address = models.CharField(max_length=255)
    end_address = models.CharField(max_length=255)
    start_has_elevator = models.BooleanField(default=False)
    end_has_elevator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    moving_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='MATCHING')


class QuoteComment(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['amount']