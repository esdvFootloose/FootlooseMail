from django.db import models
from django.contrib.auth.models import User

class ProtectedAlias(models.Model):
    Alias = models.CharField(max_length=512)
    Owners = models.ManyToManyField(User, related_name='aliases')

    def __str__(self):
        return self.Alias