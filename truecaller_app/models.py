from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    phone_number = models.CharField(max_length=15, null=False, unique=True)
    email = models.EmailField(max_length=50, null=True)
    spam = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class Contact(models.Model):
    name = models.CharField(max_length=50, null=False)
    phone_number = models.CharField(max_length=15, null=False, unique=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    spam = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UserContactRelation(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return f"{self.user}, {self.contact}"


class GlobalSpam(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return self.phone_number
