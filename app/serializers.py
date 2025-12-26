from rest_framework import serializers
from .models import Product,User


class ProductSerializer(serializers.ModelSerializer):
    farmer=serializers.ReadOnlyField(source='farmer.username')
    class Meta:
        model = Product
        fields = '__all__'




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

