from django.db import models
from django.conf import settings

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
    is_accepted = models.BooleanField(default=False)


class Comment(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['amount']