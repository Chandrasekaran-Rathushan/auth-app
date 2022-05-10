import datetime

from django.utils import timezone
from rest_framework import serializers

from .models import Customer, Product, Category, CartItem, Cart, CustomIdNo


class CustomerSerializer(serializers.ModelSerializer):
    customerNumber = serializers.CharField(
        initial=CustomIdNo.generateId(module="Customer", prefix="CUS", isYear=True, suffixNo=None), allow_blank=False,
        allow_null=False)
    firstName = serializers.CharField(required=True)
    lastName = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone1 = serializers.CharField(required=True)
    phone2 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    address = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    dueAmount = serializers.FloatField(initial=0)

    class Meta:
        model = Customer
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CustomerSerializer, self).__init__(*args, **kwargs)
        self.fields['customerNumber'].initial = CustomIdNo.generateId(module="Customer", prefix="CUS", isYear=True,
                                                                      suffixNo=None)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    productCode = serializers.CharField(initial=CustomIdNo.generateId(module="Product", prefix="ITM", isYear=False,
                                                                      suffixNo=None), allow_blank=False,
                                        allow_null=False)
    pluCode = serializers.CharField(max_length=5, allow_blank=False, allow_null=False)
    productName = serializers.CharField(max_length=255, allow_blank=False, allow_null=False)
    category = serializers.PrimaryKeyRelatedField(required=True, queryset=Category.objects.all(),
                                                  allow_null=False)
    price = serializers.FloatField(allow_null=False)
    quantity = serializers.CharField(max_length=255, allow_blank=True, allow_null=True)
    available = serializers.BooleanField(initial=True)

    class Meta:
        model = Product
        fields = (
            'productId',
            'productCode',
            'pluCode',
            'productName',
            'category',
            'categoryName',
            'price',
            'quantity',
            'available',
        )

    def __init__(self, *args, **kwargs):
        super(ProductSerializer, self).__init__(*args, **kwargs)
        self.fields['productCode'].initial = CustomIdNo.generateId(module="Product", prefix="ITM", isYear=False,
                                                                   suffixNo=None)


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = (
            'cartItemId',
            'product',
            'productName',
            'pricePerUnit',
            'quantity',
            'cart',
            'price_ht',
        )


class CartSerializer(serializers.ModelSerializer):
    orderNumber = serializers.CharField(allow_blank=False,
                                        initial=CustomIdNo.generateId(module="Order", prefix="ODR", isYear=True,
                                                                      suffixNo=None))
    createdTime = serializers.DateTimeField(read_only=True)
    billingDateTime = serializers.DateTimeField(default=timezone.now())
    customer = serializers.PrimaryKeyRelatedField(required=False, queryset=Customer.objects.all(), allow_null=True,
                                                  allow_empty=True)
    isCreditBill = serializers.BooleanField(default=False)
    totalItems = serializers.IntegerField(read_only=True)
    subTotal = serializers.FloatField(read_only=True)
    isOrdered = serializers.BooleanField(initial=False)

    class Meta:
        model = Cart
        fields = ('orderId',
                  'orderNumber',
                  'createdTime',
                  'billingDateTime',
                  'customer',
                  'customerName',
                  'isCreditBill',
                  'totalItems',
                  'subTotal',
                  'isOrdered',)

    def __init__(self, *args, **kwargs):
        super(CartSerializer, self).__init__(*args, **kwargs)
        self.fields['orderNumber'].initial = CustomIdNo.generateId(module="Order", prefix="ODR", isYear=True,
                                                                   suffixNo=None)
