from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class MailMember(models.Model):
    language_options = ((0, "Dutch"),
                        (1, "English"))

    gender_options = ((0, "Male"),
                      (1, "Female"))

    FirstName = models.CharField(max_length=256)
    LastName = models.CharField(max_length=256)
    Email = models.EmailField()
    Registration = models.DateTimeField()
    BirthDay = models.DateField()
    Language = models.IntegerField(choices=language_options, validators=[MinValueValidator(0), MaxValueValidator(1)])
    Study = models.CharField(max_length=256, blank=True, default='')
    BunkerAccess = models.BooleanField()
    Institute = models.CharField(max_length=256, blank=True, default='')
    Student = models.BooleanField()
    City = models.CharField(max_length=256)
    PostalCode = models.CharField(max_length=6)
    Address = models.CharField(max_length=256)
    Gender = models.IntegerField(choices=gender_options, validators=[MinValueValidator(0), MaxValueValidator(1)])

    def __str__(self):
        return "{} {}".format(self.FirstName, self.LastName)