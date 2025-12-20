from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_farmer = models.BooleanField(default=False)


class Product(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.IntegerField()
    planting_time = models.CharField(max_length=50)
    harvest_time = models.CharField(max_length=50)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
