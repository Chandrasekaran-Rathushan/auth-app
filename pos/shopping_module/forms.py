import datetime

from django import forms
from django.utils import timezone

from .models import Customer, CustomIdNo, Category, Product


class CustomerForm(forms.ModelForm):
    customerNumber = forms.CharField(
        initial=CustomIdNo.generateId(module="Customer", prefix="CUS", isYear=False, suffixNo=None))
    firstName = forms.CharField(required=True)
    lastName = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone1 = forms.CharField(required=True)
    phone2 = forms.CharField(required=False)
    address = forms.CharField(required=False)
    dueAmount = forms.FloatField(initial=0, required=False)

    class Meta:
        model = Customer
        fields = [
            'customerNumber',
            'firstName',
            'lastName',
            'email',
            'phone1',
            'phone2',
            'address',
            'dueAmount'
        ]

    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['customerNumber'].initial = CustomIdNo.generateId(module="Customer", prefix="CUS", isYear=True,
                                                                      suffixNo=None)


class ProductForm(forms.ModelForm):
    productCode = forms.CharField(
        initial=CustomIdNo.generateId(module="Product", prefix="ITM", isYear=False, suffixNo=None))
    pluCode = forms.CharField(max_length=5, required=True)
    productName = forms.CharField(max_length=255, required=True)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)
    price = forms.FloatField(required=True)
    quantity = forms.CharField(required=False)
    available = forms.BooleanField(initial=True)

    class Meta:
        model = Product
        fields = [
            'productCode',
            'pluCode',
            'productName',
            'category',
            'price',
            'quantity',
            'available'
        ]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['productCode'].initial = CustomIdNo.generateId(module="Product", prefix="ITM", isYear=False,
                                                                   suffixNo=None)


class OrderForm(forms.ModelForm):
    orderNumber = forms.CharField(initial=CustomIdNo.generateId(module="Order", prefix="ODR", isYear=True,
                                                                suffixNo=None), required=True)
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), required=False)
    createdTime = forms.DateTimeField(disabled=True, initial=timezone.now(), required=False)
    billingDateTime = forms.DateTimeField(initial=timezone.now(), required=False)
    isCreditBill = forms.BooleanField(initial=False, required=False)
    totalItems = forms.IntegerField(disabled=True, initial=0, required=False)
    subTotal = forms.FloatField(disabled=True, initial=0, required=False)
    isOrdered = forms.BooleanField(initial=False, required=False)

    class Meta:
        model = Product
        fields = [
            'orderNumber',
            'createdTime',
            'billingDateTime',
            'customer',
            'isCreditBill',
            'totalItems',
            'subTotal',
            'isOrdered'
        ]

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['orderNumber'].initial = CustomIdNo.generateId(module="Order", prefix="ODR", isYear=True,
                                                                   suffixNo=None)
