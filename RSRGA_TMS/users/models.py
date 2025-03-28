from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Planter(models.Model):
    planterid = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=100, blank=True)
    lastname = models.CharField(max_length=100, blank=True)
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    phonenumber = models.CharField(max_length=15, blank=True)
    affiliation = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
