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
    planting_time = models.CharField(max_length=200)
    harvest_time = models.CharField(max_length=200)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")
