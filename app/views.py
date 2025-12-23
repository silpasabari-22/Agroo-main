from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer, RegisterSerializer



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
    

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_farmer:
            raise PermissionDenied("Only farmers can add products")
        serializer.save(farmer=self.request.user)


class UpgradeToFarmerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.is_farmer = True
        request.user.save()
        return Response({"message": "Upgraded to farmer"})






# farmer..............................................................
