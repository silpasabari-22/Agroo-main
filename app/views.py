from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser
from .serializers import UserSerializer
from .models import User
from .models import Product,Cart
from .serializers import ProductSerializer, RegisterSerializer,CartSerializer






#customer.........................................................

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Farmer → only their products
        if user.is_farmer:
            return Product.objects.filter(farmer=user)

        # Customer → all available products
        return Product.objects.filter(available=True)
    def perform_create(self, serializer):
        if not self.request.user.is_farmer:
            raise PermissionDenied(
                "You must upgrade to farmer to add products"
            )

        serializer.save(farmer=self.request.user)



class DowngradeToCustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.is_farmer = False
        request.user.save()
        return Response({"message": "You are now a customer"})



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )



class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Farmers cannot add to cart
        if request.user.is_farmer:
            raise PermissionDenied("Farmers cannot add products to cart")

        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        try:
            product = Product.objects.get(id=product_id, available=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = quantity

        cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)




class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_id):
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            cart_item.delete()
            return Response({"message": "Item removed from cart"})
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)




# farmer..............................................................



class ProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            raise PermissionDenied("Admin cannot add products")

        if not user.is_farmer:
            raise PermissionDenied("Only farmers can add products")

        serializer.save(farmer=user)


class FarmerProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not user.is_farmer:
            raise PermissionDenied("Only farmers can view their products")

        return Product.objects.filter(farmer=user)




class UpgradeToFarmerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.is_farmer = True
        request.user.save()
        return Response({"message": "Upgraded to farmer"})


class FarmerProductDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Farmer can access ONLY their own products
        if not self.request.user.is_farmer:
            raise PermissionDenied("Only farmers can manage products")
        return Product.objects.filter(farmer=self.request.user)




# admin.................................................................

class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AdminToggleUserStatusView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            return Response({
                "message": f"User {'activated' if user.is_active else 'blocked'} successfully"
            })
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class AdminApproveFarmerView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        user.is_farmer = True
        user.save()
        return Response({"message": "Farmer approved"})
