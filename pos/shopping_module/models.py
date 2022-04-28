from django.db import models
from django.utils import timezone

from .exceptions import CartItemExists, OrderDelivered, CustomerRequired


class CustomIdNo(models.Model):
    module = models.CharField(max_length=50)
    prefix = models.CharField(max_length=8)
    isYear = models.BooleanField(default=False)
    suffix = models.CharField(max_length=255)
    idString = models.TextField(default="")

    class Meta:
        verbose_name_plural = "IdNumbers"

    def __str__(self):
        return self.idString

    @staticmethod
    def generateId(module, prefix, isYear, suffixNo):
        year = {True: timezone.now().year, False: "", None: ""}[isYear]

        suffix = 0

        try:
            moduleRecordCount = CustomIdNo.objects.filter(module=module).count()
            suffix = moduleRecordCount + 1
        except:
            suffix = suffix + 1

        idString = ""

        if isYear is None or isYear is False:
            idString = f"{prefix}-{str(suffix)}"
        else:
            idString = f"{prefix}-{year}{str(suffix)}"

        return idString

    def save(self, *args, **kwargs):
        if self.idString is not None or self.idString != "":
            isIdNotExist = CustomIdNo.objects.filter(idString=self.idString).count() == 0
            if isIdNotExist:
                super().save(*args, **kwargs)

        else:
            year = {True: timezone.now().year, False: ""}[self.isYear]
            suffix = 0

            try:
                moduleRecordCount = CustomIdNo.objects.filter(module=self.module).count()
                suffix = moduleRecordCount + 1
            except CustomIdNo.DoesNotExist:
                suffix = suffix + 1
            self.suffix = suffix
            self.idString = f"{self.prefix}-{str(year)}{str(suffix)}"
            isIdNotExist = CustomIdNo.objects.filter(idString=self.idString).count() == 0
            if isIdNotExist:
                super().save(*args, **kwargs)


class Customer(models.Model):
    customerId = models.AutoField(primary_key=True)
    customerNumber = models.CharField(max_length=100, blank=False, unique=True,
                                      default=CustomIdNo.generateId(module="Customer", prefix="CUS", isYear=True,
                                                                    suffixNo=None))
    firstName = models.CharField(max_length=255, null=False, blank=False)
    lastName = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone1 = models.CharField(max_length=255, null=False, blank=False)
    phone2 = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    dueAmount = models.FloatField(default=0, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.firstName = str(self.firstName).capitalize()
        self.lastName = str(self.lastName).capitalize()
        super(Customer, self).save(*args, **kwargs)
        CustomIdNo.objects.create(module="Customer", prefix="CUS", isYear=True, idString=self.customerNumber)

    def __str__(self):
        lastName = self.lastName is not None and f" {self.lastName}" or ""
        return self.firstName + lastName


class Category(models.Model):
    categoryId = models.AutoField(primary_key=True)
    categoryName = models.CharField(max_length=255, unique=False, blank=False)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.categoryName

    def save(self, *args, **kwargs):
        self.categoryName = str(self.categoryName).capitalize()
        super().save(*args, **kwargs)


class Product(models.Model):
    productId = models.AutoField(primary_key=True)
    productCode = models.CharField(max_length=100, blank=False, unique=True,
                                   default=CustomIdNo.generateId(module="Product", prefix="ITM", isYear=False,
                                                                 suffixNo=None))
    pluCode = models.CharField(max_length=5, blank=False, null=False)
    productName = models.CharField(max_length=255, null=False, blank=False)
    category = models.ForeignKey(Category,related_name="category", on_delete=models.CASCADE, null=False, blank=False)
    price = models.FloatField(null=False, blank=False)
    quantity = models.CharField(max_length=255, null=True, blank=True)
    available = models.BooleanField(default=True, verbose_name="available")

    def __str__(self):
        return self.productName

    def categoryName(self):
        if self.category is not None:
            return self.category.categoryName

    def save(self, *args, **kwargs):
        self.productName = str(self.productName).capitalize()
        super(Product, self).save(*args, **kwargs)
        CustomIdNo.objects.create(module="Product", prefix="ITM", isYear=False, idString=self.productCode)


class Cart(models.Model):
    orderId = models.AutoField(primary_key=True)
    orderNumber = models.TextField(blank=False, unique=True,
                                   default=CustomIdNo.generateId(module="Order", prefix="ODR", isYear=True,
                                                                 suffixNo=None))
    createdTime = models.DateTimeField(default=timezone.now())
    billingDateTime = models.DateTimeField(default=timezone.now())
    customer = models.ForeignKey(Customer, related_name="customer", on_delete=models.CASCADE, null=True, blank=True)
    isCreditBill = models.BooleanField(default=False, verbose_name="credit")
    totalItems = models.IntegerField(default=0)
    subTotal = models.FloatField(default=0)
    isOrdered = models.BooleanField(default=False, verbose_name="order status")

    # purchasedProducts = models.ManyToManyField(CartItem)

    def __str__(self):
        return self.orderNumber

    def customerName(self):
        if self.customer is not None:
            return self.customer.firstName + " " + self.customer.lastName

    def save(self, a=None, *args, **kwargs):
        if self.customer is None and self.isCreditBill:
            raise CustomerRequired
        elif self.customer is not None and self.isCreditBill:
            customer = Customer.objects.get(customerId=self.customer.customerId)
            customer.dueAmount = self.subTotal
            customer.save()

        super(Cart, self).save(*args, **kwargs)

        if not a:
            CustomIdNo.objects.create(module="Order", prefix="ODR", isYear=True, idString=self.orderNumber)


class CartItem(models.Model):
    cartItemId = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name="product", on_delete=models.CASCADE)
    pricePerUnit = models.FloatField(blank=True, null=True)
    quantity = models.FloatField(default=1, blank=False, null=False)
    cart = models.ForeignKey(Cart, related_name="cart", on_delete=models.CASCADE, null=False, blank=False)
    price_ht = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} of {self.product} - {self.cart}"

    def productName(self):
        if self.product is not None:
            return self.product.productName

    def delete(self, using=None, keep_parents=False):
        super(CartItem, self).delete()

        cart = Cart.objects.get(orderId=vars(self.cart)["orderId"])

        cart.totalItems = cart.totalItems - 1
        cart.subTotal = cart.subTotal - self.price_ht
        cart.billingDateTime = timezone.now()
        cart.save(a=True)

    def save(self, *args, **kwargs):
        existing_price_ht = self.price_ht or 0

        if self.cart.isOrdered:
            raise OrderDelivered

        try:
            cartItem = CartItem.objects.get(product=self.product.productId,
                                            cart=self.cart.orderId)

            # to check is a new record or not
            is_new = self.pk is None

            if is_new and cartItem is not None:
                raise CartItemExists
            elif not is_new:
                pass

        except CartItem.DoesNotExist:
            pass

        try:
            if self.pricePerUnit > 0:
                self.price_ht = self.quantity * self.pricePerUnit
        except:
            self.pricePerUnit = vars(Product.objects.get(productId=vars(self.product)["productId"]))['price']
            self.price_ht = self.quantity * self.pricePerUnit

        super(CartItem, self).save(*args, **kwargs)

        cart = Cart.objects.get(orderId=vars(self.cart)["orderId"])
        if existing_price_ht > 0:
            cart.subTotal = cart.subTotal - existing_price_ht

        if existing_price_ht == 0 or existing_price_ht is None:
            cart.totalItems = cart.totalItems + 1

        cart.subTotal = cart.subTotal + self.price_ht
        cart.billingDateTime = timezone.now()
        cart.save(a=True)
