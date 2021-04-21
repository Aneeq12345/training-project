from django.db import models

from django.contrib.auth.models import User
# Create your models here.


class SocialProvider(models.Model):
    provider = models.CharField(
        max_length=25)
    user =models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.auth_provider
    class Meta:
        db_table = "social_provider"  