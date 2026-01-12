from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import DestroyAPIView
from .serializers import UserSerializer
from .models import User
from .models import Product,Cart,CartItem
from .serializers import ProductSerializer, RegisterSerializer,CartItemSerializer
from .models import Category,OrderItem,Order
from .serializers import CategorySerializer,OrderItemSerializer,OrderHistorySerializer
from .serializers import FarmerOrderItemSerializer
from .models import DeliveryAddress
from .serializers import AddressSerializer





#Admin............................................................

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class AdminCategoryCreateView(CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


class AdminCategoryDeleteView(DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]


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
        queryset = Product.objects.all()

        # Farmer → see only their products
        if user.is_farmer:
            queryset = queryset.filter(farmer=user)

        # Customer → see all available products
        else:
            queryset = queryset.filter(available=True)

        # 🔹 CATEGORY FILTER (IMPORTANT PART)
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset





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
        if request.user.is_farmer:
            raise PermissionDenied("Farmers cannot add products to cart")

        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        try:
            product = Product.objects.get(id=product_id, available=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class CartListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        cart_items = CartItem.objects.filter(cart__user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
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
        





class OrderSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"message": "Cart is empty"})

        total = 0
        summary = []

        for item in cart_items:
            subtotal = item.product.price * item.quantity
            total += subtotal

            summary.append({
                "product": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": subtotal
            })

        return Response({
            "items": summary,
            "total_amount": total,
            "payment_options": ["COD", "ONLINE"]
        })



class CustomerOrderHistoryView(ListAPIView):
    serializer_class = OrderHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Farmers should not see customer order history
        if user.is_farmer:
            return Order.objects.none()

        return Order.objects.filter(user=user).order_by("-created_at")




class FarmerUpdateOrderItemStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_item_id):
        user = request.user

        if not user.is_farmer:
            return Response(
                {"error": "Only farmers can update order status"},
                status=403
            )

        try:
            order_item = OrderItem.objects.get(
                id=order_item_id,
                product__farmer=user
            )
        except OrderItem.DoesNotExist:
            return Response(
                {"error": "Order item not found or access denied"},
                status=404
            )

        new_status = request.data.get("status")

        if new_status not in ["Pending", "Confirmed", "Delivered"]:
            return Response(
                {"error": "Invalid status"},
                status=400
            )

        order_item.status = new_status
        order_item.save()

        return Response({
            "message": "Order item status updated",
            "product": order_item.product.name,
            "new_status": order_item.status
        })





class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_farmer:
            return Response({"error": "Farmers cannot place orders"}, status=403)

        payment_method = request.data.get("payment_method")

        if payment_method not in ["COD", "ONLINE"]:
            return Response({"error": "Invalid payment method"}, status=400)

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = sum(
            item.product.price * item.quantity
            for item in cart.items.all()
        )

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_method=payment_method,
            payment_status="Pending",
            status="Confirmed"
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()

        return Response({
            "message": "Order placed successfully",
            "order_id": order.id
        }, status=201)



class AddAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id, user=request.user)

        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.save(user=request.user)
            order.address = address
            order.save()
            return Response({"message": "Address added"})
        return Response(serializer.errors, status=400)



class SelectPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id, user=request.user)
        payment_method = request.data.get("payment_method")

        if payment_method not in ["COD", "ONLINE"]:
            return Response({"error": "Invalid payment method"}, status=400)

        order.payment_method = payment_method
        order.status = "Confirmed"
        order.save()

        return Response({
            "message": "Order confirmed",
            "order_id": order.id
        })







class OrderSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = Order.objects.get(
            id=order_id,
            user=request.user,
            status="Confirmed"
        )
        serializer = OrderSerializer(order)
        return Response(serializer.data)



class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)








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







class FarmerOrderDashboardView(ListAPIView):
    serializer_class = FarmerOrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Only farmers allowed
        if not user.is_farmer:
            return OrderItem.objects.none()

        return OrderItem.objects.filter(
            product__farmer=user
        ).order_by("-order__created_at")



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
