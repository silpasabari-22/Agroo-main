
from django.urls import path
from app.views import ProductListView,ProductCreateView,UpgradeToFarmerView,RegisterView
from .views import FarmerProductListView
from .views import DowngradeToCustomerView
from .views import FarmerProductDetailView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('upgrade-farmer/', UpgradeToFarmerView.as_view()),
    path('products/', ProductListView.as_view()),    #GET all available products
    path('products/add/', ProductCreateView.as_view()),  #POST (only farmers)
    path('farmer/products/', FarmerProductListView.as_view()),
    path('downgrade-customer/', DowngradeToCustomerView.as_view()),
    path('farmer/products/<int:pk>/', FarmerProductDetailView.as_view()),
]



