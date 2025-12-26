from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import RetrieveUpdateDestroyAPIView


from .models import Product
from .serializers import ProductSerializer, RegisterSerializer






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
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer



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