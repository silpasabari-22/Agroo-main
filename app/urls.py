
from django.urls import path
from app.views import ProductListCreateView, UpgradeToFarmerView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('upgrade-farmer/', UpgradeToFarmerView.as_view()),
    path('products/', ProductListCreateView.as_view()),
]



