from rest_framework import serializers
from .models import Product,User
from .models import CartItem,Category,OrderItem,Order



class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    farmer=serializers.ReadOnlyField(source='farmer.username')
    category_name = serializers.ReadOnlyField(source="category.name")
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'category',
            'category_name',
            'price',
            'quantity',
            'planting_time',
            'harvest_time',
            'available',
            'farmer',
            'image'
        ]
        read_only_fields = ["farmer"]



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])  # IMPORTANT
        user.save()
        return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'is_farmer',
            'is_active',
            'is_staff'
        ]



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity"
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "quantity", "price"]



class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total_amount",
            "payment_method",
            "payment_status",
            "status",
            "created_at",
            "items",
        ]



class FarmerOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    order_id = serializers.ReadOnlyField(source="order.id")
    customer_name = serializers.ReadOnlyField(source="order.user.username")
    order_date = serializers.ReadOnlyField(source="order.created_at")
    order_status = serializers.ReadOnlyField(source="order.status")
    payment_status = serializers.ReadOnlyField(source="order.payment_status")

    class Meta:
        model = OrderItem
        fields = [
            "order_id",
            "product_name",
            "quantity",
            "price",
            "customer_name",
            "order_date",
            "order_status",
            "payment_status",
        ]