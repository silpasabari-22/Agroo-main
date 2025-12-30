
from django.urls import path
from .views import ProductListView,ProductCreateView,UpgradeToFarmerView,RegisterView
from .views import FarmerProductListView
from .views import DowngradeToCustomerView
from .views import FarmerProductDetailView
from .views import AdminUserListView, AdminToggleUserStatusView, AdminApproveFarmerView
from .views import AddToCartView, CartListView, RemoveFromCartView
from .views import CategoryListView,AdminCategoryCreateView, AdminCategoryDeleteView
from .views import PaymentOptionsView,OrderSummaryView,PlaceOrderView


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('upgrade-farmer/', UpgradeToFarmerView.as_view()),
    path('products/', ProductListView.as_view()),    #GET all available products
    path('products/add/', ProductCreateView.as_view()),  #POST (only farmers)
    path('farmer/products/', FarmerProductListView.as_view()),
    path('downgrade-customer/', DowngradeToCustomerView.as_view()),
    path('farmer/products/<int:pk>/', FarmerProductDetailView.as_view()),
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/toggle/<int:user_id>/', AdminToggleUserStatusView.as_view()),
    path('admin/approve-farmer/<int:user_id>/', AdminApproveFarmerView.as_view()),
    path("cart/add/", AddToCartView.as_view()),
    path("cart/", CartListView.as_view()),
    path("cart/remove/<int:cart_id>/", RemoveFromCartView.as_view()),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/', CategoryListView.as_view()),     # Public
    path('admin/categories/add/', AdminCategoryCreateView.as_view()),   # Admin only
    path('admin/categories/delete/<int:pk>/', AdminCategoryDeleteView.as_view()),   # Admin only
    path("payment/options/", PaymentOptionsView.as_view(), name="payment-options"),
    path("order/summary/", OrderSummaryView.as_view(), name="order-summary"),
    path("order/place/", PlaceOrderView.as_view(), name="place-order"),
    

]



