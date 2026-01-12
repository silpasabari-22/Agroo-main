from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    is_farmer = models.BooleanField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name



class Product(models.Model):
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    quantity = models.IntegerField()
    planting_time = models.CharField(max_length=500,null=True)
    harvest_time = models.CharField(max_length=200,null=True)
    expiry_date = models.DateField(null=True, blank=True)

    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True
    )

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



class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    district = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.full_name} - {self.city}"





class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL,null=True,blank=True)
    total_amount = models.FloatField()
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        default="Initiated"
    )
    created_at = models.DateTimeField(auto_now_add=True)




class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    status = models.CharField(  
        max_length=20,
        default="Pending"
    )   # Pending → Confirmed → Delivered

    def __str__(self):
        return f"{self.product.name} - {self.status}"




