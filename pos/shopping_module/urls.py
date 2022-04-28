from django.urls import path, include
from rest_framework import routers

from .views import CustomerApiView, generateId, ProductApiView, cart_list_view, CartApiView, product_list_view, \
    customer_list_view, CategoryApiView, category_list_view, cartItem_list_view, CartItemApiView

router = routers.DefaultRouter()
# router.register("customer", CustomerViewSet)
# router.register("product", ProductViewSet)
# router.register("cart", CartViewSet)
# router.register("category", CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),

    path('customer/', customer_list_view, name="Customer"),
    path('customer/<int:id>/', CustomerApiView.as_view(), name="Customer"),

    path('product/', product_list_view, name="Product"),
    path('product/<int:id>/', ProductApiView.as_view(), name="Product"),

    path('cart/', cart_list_view, name="Cart"),
    path('cart/<int:id>/', CartApiView.as_view()),

    path('cart-item/', cartItem_list_view, name="Cart-Item"),
    path('cart-item/<int:id>/', CartItemApiView.as_view(), name="Cart-Item"),

    path('category/', category_list_view, name="Category"),
    path('category/<int:id>/', CategoryApiView.as_view()),

    path('generateId/', generateId),
]