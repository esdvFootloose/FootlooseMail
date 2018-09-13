from django.db import models
from django.contrib.auth.models import User

class AliasChange(models.Model):
    types = (
        ('a', 'added'),
        ('d', 'removed')
    )

    Alias = models.CharField(max_length=512)
    Email = models.EmailField()
    Type = models.CharField(max_length=1, choices=types)
    User = models.ForeignKey(User, related_name='aliaschanges', on_delete=models.CASCADE)
    Timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{} did {} to {} from {}'.format(self.User, self.Type, self.Email, self.Alias)
