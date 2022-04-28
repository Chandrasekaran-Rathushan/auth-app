from django.contrib import admin
from .forms import CustomerForm, ProductForm, OrderForm
from .models import Customer, Category, Product, CartItem, Cart, CustomIdNo

admin.site.register(CustomIdNo)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ["customerNumber", "firstName", "lastName", "dueAmount"]
    list_filter = ["customerNumber", "firstName"]
    search_fields = ["customerNumber", "firstName"]
    form = CustomerForm

    # def __init__(self, model, admin_site):
    #     super().__init__(model, admin_site)
    #
    # def save_model(self, request, obj, form, change):
    #     super(CustomerAdmin, self).save_model(request, obj, form, change)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Category)


class ProductAdmin(admin.ModelAdmin):
    list_display = ["productCode", "productName", "category", "price", "available"]
    list_filter = ["productCode", "category", "productName"]
    search_fields = ["productCode", "category", "productName", "pluCode"]
    form = ProductForm


admin.site.register(Product, ProductAdmin)


class CartItemAdmin(admin.ModelAdmin):
    list_display = ["product", "pricePerUnit", "quantity", "price_ht", "cart"]
    list_filter = ["cart"]
    search_fields = ["cart"]


admin.site.register(CartItem, CartItemAdmin)


class CartAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ["orderNumber", "createdTime", "billingDateTime", "customer", "totalItems",
                    "subTotal", "isCreditBill"]
    list_filter = ["orderNumber", "customer", "billingDateTime"]
    search_fields = ["orderNumber", "customer", "billingDateTime"]


admin.site.register(Cart, CartAdmin)
