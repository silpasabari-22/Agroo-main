from django.urls import path
from app import views
from app.views import ProductListCreateView

urlpatterns = [
    path('products/', ProductListCreateView.as_view()),
]
