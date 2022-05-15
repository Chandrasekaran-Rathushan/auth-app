import calendar
import datetime
import json
import math

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Sum, Count
from django.db.models.expressions import Value, F
from django.db.models.functions import Extract
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, CustomIdNo, Product, Cart, Category, CartItem
from .serializers import CustomerSerializer, ProductSerializer, CartSerializer, CategorySerializer, CartItemSerializer


def checkForRequiredParams(request, params):
    errors = {
        "errors": [
        ]
    }

    for param in params:
        o = request.GET.get(param, None)
        if o is None:
            errors["errors"].append({"error": f"{param} is a required url parameter."})

        if param == "isYear" and not str(o).capitalize() in ['True', 'False'] and o is not None:
            isYear = bool(o)
            errors["errors"].append({"error": "isYear is a boolean field."})

    return errors


@csrf_exempt
@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def generateId(request):
    params = ['module', 'prefix', 'isYear']

    errors = checkForRequiredParams(request, params)

    if errors["errors"].__len__() > 0:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    module = request.GET.get("module", None)
    prefix = request.GET.get("prefix", None)
    isYear = request.GET.get("isYear", False)

    isYear = (False, True)[isYear == "true"]

    id = CustomIdNo.generateId(module=module, prefix=prefix, isYear=isYear, suffixNo=None)
    return Response({"id": id}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def customer_list_view(request):
    if request.method == "GET":
        try:
            customers = Customer.objects.all()
            serializer_class = CustomerSerializer(customers, many=True)
            return JsonResponse(serializer_class.data, safe=False)
        except:
            return JsonResponse({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "POST":
        customer = JSONParser().parse(request)
        serializer_class = CustomerSerializer(data=customer)
        if serializer_class.is_valid():
            serializer_class.save()
            return JsonResponse(serializer_class.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerApiView(APIView):

    def get_object(self, id):
        try:
            return Customer.objects.get(customerId=id)
        except Customer.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        try:
            customer = self.get_object(id=id)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "not found."})

    def put(self, request, id, format=None):
        customer = self.get_object(id=id)
        serializer = CustomerSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        customer = self.get_object(id=id)
        customer.delete()
        return Response({"customerNumber": customer.customerNumber, "firstName": customer.firstName},
                        status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def product_list_view(request):
    if request.method == "GET":
        try:
            products = Product.objects.all()
            serializer_class = ProductSerializer(products, many=True)
            return JsonResponse(serializer_class.data, safe=False)
        except:
            return JsonResponse({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "POST":
        product = JSONParser().parse(request)
        serializer_class = ProductSerializer(data=product)
        if serializer_class.is_valid():
            serializer_class.save()
            return JsonResponse(serializer_class.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductApiView(APIView):

    def get_object(self, id):
        try:
            return Product.objects.get(productId=id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        try:
            product = self.get_object(id=id)
            serializer = ProductSerializer(product)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "not found."})

    def put(self, request, id, format=None):
        product = self.get_object(id=id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        product = self.get_object(id=id)
        product.delete()
        return Response({"productCode": product.productCode, "productName": product.productName},
                        status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def cart_list_view(request):
    def get_object(orderNumber):
        try:
            return Cart.objects.get(orderNumber=orderNumber)
        except Cart.DoesNotExist:
            raise Http404

    if request.method == "GET":
        try:
            carts = Cart.objects.all()
            serializer_class = CartSerializer(carts, many=True)
            return JsonResponse(serializer_class.data, safe=False)
        except:
            return JsonResponse({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "POST":
        cart = JSONParser().parse(request)
        serializer_class = CartSerializer(data=cart)
        if serializer_class.is_valid():
            serializer_class.save()

            return JsonResponse(serializer_class.data,
                                status=status.HTTP_200_OK)

        return JsonResponse(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class CartApiView(APIView):

    @staticmethod
    def get_object(id):
        try:
            return Cart.objects.get(orderId=id)
        except Cart.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        try:
            cart = self.get_object(id=id)
            serializer = CartSerializer(cart)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "not found."})

    def put(self, request, id, format=None):
        cart = self.get_object(id=id)
        serializer = CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        try:
            cart = self.get_object(id=id)
            cart.delete()
            return Response({"message": "success"},
                            status=status.HTTP_200_OK)
        except:
            return Response({"message": "error"},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def cartItem_list_view(request):
    if request.method == "GET":
        params = ['cartId']
        error = checkForRequiredParams(request, params)

        cartItems = None

        try:

            if error["errors"].__len__() > 0:
                cartItems = CartItem.objects.all()
            else:
                cartItems = CartItem.objects.filter(cart=request.GET.get('cartId', None))

            serializer_class = CartItemSerializer(cartItems, many=True)

            return JsonResponse(serializer_class.data, safe=False)
        except:
            return JsonResponse({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "POST":
        serializer_class = CartItemSerializer(data=request.data, many=True)
        if serializer_class.is_valid():
            serializer_class.save()
            return JsonResponse(serializer_class.data, status=status.HTTP_200_OK, safe=False)
        return JsonResponse(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemApiView(APIView):

    @staticmethod
    def get_object(id):
        try:
            return CartItem.objects.get(cartItemId=id)
        except CartItem.DoesNotExist:
            raise Http404

    @staticmethod
    def get_objects(id):
        try:
            return CartItem.objects.filter(cart=id)
        except CartItem.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        try:
            cartItem = self.get_object(id=id)
            serializer = CartItemSerializer(cartItem)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "not found."})

    def put(self, request, id, format=None):
        cartItems = self.get_objects(id=id)

        # method used to convert Query set to JSON
        # referenceCartItems = list(cartItems.values())

        requestCartItems = request.data
        returnData = []
        errors = []

        for obj in requestCartItems:
            cartItem = self.get_object(id=obj['cartItemId'])
            serializer = CartItemSerializer(cartItem, data=obj)
            if serializer.is_valid():
                serializer.save()
                returnData.append(serializer.data)
            else:
                errors.append(serializer.errors)

        if errors.__len__() > 0:
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST, safe=False)
        else:
            return JsonResponse(returnData,
                                status=status.HTTP_200_OK, safe=False)

    def delete(self, request, id, format=None):
        try:
            cartItem = self.get_object(id=id)
            cartItem.delete()
            return Response({"message": "success"},
                            status=status.HTTP_200_OK)
        except:
            return Response({"message": "error"},
                            status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def category_list_view(request):
    if request.method == "GET":
        try:
            categories = Category.objects.all()
            serializer_class = CategorySerializer(categories, many=True)
            return JsonResponse(serializer_class.data, safe=False)
        except:
            return JsonResponse({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "POST":
        category = JSONParser().parse(request)
        serializer_class = CategorySerializer(data=category)
        if serializer_class.is_valid():
            serializer_class.save()
            return JsonResponse(serializer_class.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryApiView(APIView):

    @staticmethod
    def get_object(id):
        try:
            return Category.objects.get(categoryId=id)
        except Category.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        try:
            category = self.get_object(id=id)
            serializer = CategorySerializer(category)
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        except Http404:
            return Response({"error": "not found."})

    def put(self, request, id, format=None):
        category = self.get_object(id=id)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        try:
            category = self.get_object(id=id)
            category.delete()
            return Response({"message": "success"},
                            status=status.HTTP_200_OK)
        except:
            return Response({"message": "error"},
                            status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['GET'])
def get_stats(request):
    data = None

    currentDate = timezone.now()

    currentDateStart = currentDate.replace(hour=0, minute=0, second=0, microsecond=0)
    currentDateEnd = currentDate.replace(hour=23, minute=59, second=59, microsecond=999999)

    monthStartDate = currentDate.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthEndDate = monthStartDate.replace(day=calendar.monthrange(monthStartDate.year, monthStartDate.month)[1],
                                          hour=23, minute=59, second=59, microsecond=999999)

    yearStartDate = currentDate.replace(day=1, month=1, hour=0, minute=0, second=0, microsecond=0)
    yearEndDate = yearStartDate.replace(day=31, month=12, hour=23, minute=59, second=59, microsecond=999999)

    chartStartDate = (currentDate - timezone.timedelta(days=365)).replace(day=1, hour=0, minute=0, second=0,
                                                                          microsecond=0)
    chartEndDate = currentDate.replace(day=calendar.monthrange(chartStartDate.year, chartStartDate.month)[1], hour=23,
                                       minute=59, second=59, microsecond=999999)

    def convertToString(value):
        try:
            floatVal = float(value)
            strVal = str(floatVal)
            return strVal
        except:
            return "0.0"

    sys_start_date = vars(Cart.objects.all().order_by("billingDateTime").first())['billingDateTime']
    sys_end_date = currentDateEnd.isoformat().split("+")[0]

    try:
        completedOrders = {
            'key': 'completedOrders',
            'value': Cart.objects.filter(isOrdered=True).count(),
            'label': "Completed",
            "type": "text",
            'start': sys_start_date,
            'end': sys_end_date,
            "dateFormat": "DD MMM yyyy"
        }
        pendingOrders = {
            'key': 'pendingOrders',
            'value': Cart.objects.filter(isOrdered=False).count(),
            'label': "Pending",
            "type": "text",
            'start': sys_start_date,
            'end': sys_end_date,
            "dateFormat": "DD MMM yyyy"
        }
        creditOrders = {
            'key': 'creditOrders',
            'value': Cart.objects.filter(isCreditBill=True).count(),
            'label': "Credit",
            "type": "text",
            'start': sys_start_date,
            'end': sys_end_date,
            "dateFormat": "DD MMM yyyy"
        }

        salesForDayQS = Cart.objects.filter(
            billingDateTime__range=[currentDateStart.isoformat(), currentDateEnd.isoformat()])

        salesForTheDay = {
            'key': 'salesForTheDay',
            'value': convertToString(salesForDayQS.aggregate(Sum('subTotal'))['subTotal__sum']),
            'salesCount': salesForDayQS.count(),
            'label': "Today",
            'start': currentDateStart.isoformat().split("+")[0],
            'end': currentDateEnd.isoformat().split("+")[0],
            "type": "date",
            "dateFormat": "hh:mm A"
        }

        salesForTheMonthQS = Cart.objects.filter(
            billingDateTime__range=[monthStartDate.isoformat(), monthEndDate.isoformat()])

        salesForTheMonth = {
            'key': 'salesForTheMonth',
            'value': str(salesForTheMonthQS.aggregate(Sum('subTotal'))['subTotal__sum']),
            'salesCount': salesForTheMonthQS.count(),
            'label': "Monthly Sales",
            'start': monthStartDate.isoformat().split("+")[0],
            'end': monthEndDate.isoformat().split("+")[0],
            "type": "date",
            "dateFormat": "MMM"
        }

        salesForTheYearQS = Cart.objects.filter(
            billingDateTime__range=[yearStartDate.isoformat(), yearEndDate.isoformat()])

        salesForTheYear = {
            'key': 'salesForTheYear',
            'value': str(salesForTheYearQS.aggregate(Sum('subTotal'))['subTotal__sum']),
            'salesCount': salesForTheYearQS.count(),
            'label': "Yearly Sales",
            'start': yearStartDate.isoformat().split("+")[0],
            'end': yearEndDate.isoformat().split("+")[0],
            "type": "date",
            "dateFormat": "YYYY"
        }

        salesByMonthQS = Cart.objects.annotate(billingMonth=Extract('billingDateTime', 'month')) \
            .annotate(billingYear=Extract('billingDateTime', 'year')) \
            .annotate(total=Sum('subTotal')) \
            .filter(billingDateTime__range=[chartStartDate.isoformat(), chartEndDate.isoformat()]) \
            .values('billingMonth', 'billingYear', "total") \
            .annotate(noOfSalesForTheMonth=Count('billingMonth')) \
            .order_by('billingYear', 'billingMonth')

        salesByMonth = {
            'key': 'salesByMonth',
            'value': list(salesByMonthQS),
            'monthCount': salesByMonthQS.count(),
            'label': "Sales By Month",
            'start': chartStartDate.isoformat().split("+")[0],
            'end': chartEndDate.isoformat().split("+")[0],
            "type": "chart"
        }

        # orders sales by month
        # print(list(Cart.objects.annotate(billingMonth=Extract('billingDateTime', 'month'))
        #            .order_by('billingMonth', 'orderId').values('orderId', 'billingMonth')))

        # a = Cart.objects.all().values_list('billingDateTime__year', 'billingDateTime__month')
        #                       .order_by('billingDateTime__year', 'billingDateTime__month')
        # print(a)

        data = [
            salesForTheDay,
            salesForTheMonth,
            salesForTheYear,
            completedOrders,
            creditOrders,
            pendingOrders,
            salesByMonth
        ]

        return Response(data, status=status.HTTP_200_OK)

    except:
        Response({"message": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
def get_sales_report(request):
    startDate = request.GET.get("startDate", "")
    endDate = request.GET.get("endDate", "")
    type = request.GET.get("type", None)

    try:

        if startDate != "" and endDate != "":
            startDate = timezone.datetime \
                .strptime(startDate, "%Y-%m-%d") \
                .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

            endDate = timezone.datetime \
                .strptime(endDate, "%Y-%m-%d") \
                .replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

        elif startDate == "" and endDate != "":
            endDate = timezone.datetime \
                .strptime(endDate, "%Y-%m-%d") \
                .replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)
            startDate = endDate.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        elif startDate != "" and endDate == "":
            startDate = timezone.datetime \
                .strptime(startDate, "%Y-%m-%d") \
                .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
            endDate = startDate.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc)

        elif startDate == "" and endDate == "":
            return Response({"error": "Provide valid start date and end date."}, status=status.HTTP_400_BAD_REQUEST)

    except ValueError:
        return Response({"error": "Provide valid start date and end date."}, status=status.HTTP_400_BAD_REQUEST)

    e = 0.00001
    noOfDays = round(math.floor(endDate.timestamp() - startDate.timestamp() + e) / (60 * 60) / 24)

    salesForThePeriod = Cart.objects.filter(
        billingDateTime__range=[startDate.isoformat(), endDate.isoformat()])

    noOfMonths = ((endDate.year - startDate.year) * 12) \
                 + (endDate.month - startDate.month) \
                 + 1

    daterange_unit = {True: "days", False: {True: "years", False: "months", None: ""}[noOfMonths > 12], None: ""}[
        noOfDays < 27 and noOfMonths == 1]

    if type is not None and type != "":
        daterange_unit = type

    salesByPeriodQS = []

    def byDays():
        return list(Cart.objects.filter(billingDateTime__range=[startDate.isoformat(), endDate.isoformat()]).values())

    def byMonths():
        qs = Cart.objects.annotate(billingMonth=Extract('billingDateTime', 'month')) \
            .annotate(billingYear=Extract('billingDateTime', 'year')) \
            .annotate(total=Sum('subTotal')) \
            .filter(billingDateTime__range=[startDate.isoformat(), endDate.isoformat()]) \
            .values('billingMonth', 'billingYear', "total") \
            .annotate(noOfSalesForTheMonth=Count('billingMonth')) \
            .order_by('billingYear', 'billingMonth')

        data = []

        allSalesInRange = Cart.objects.annotate(billingMonth=Extract('billingDateTime', 'month')) \
            .annotate(billingYear=Extract('billingDateTime', 'year')) \
            .filter(billingDateTime__range=[startDate.isoformat(), endDate.isoformat()])

        for q in qs:
            data.append({
                **q,
                "sales": list(
                    allSalesInRange.filter(billingMonth=q["billingMonth"], billingYear=q["billingYear"]).values())
            })

        return data

    def byYears():
        qs = Cart.objects.annotate(billingYear=Extract('billingDateTime', 'year')) \
            .annotate(total=Sum('subTotal')) \
            .filter(billingDateTime__range=[startDate.isoformat(), endDate.isoformat()]) \
            .values('billingYear', "total") \
            .annotate(noOfSalesForTheYear=Count('billingYear')) \
            .order_by('billingYear')

        data = []

        allSalesInRange = Cart.objects.annotate(billingYear=Extract('billingDateTime', 'year')) \
            .filter(billingDateTime__range=[startDate.isoformat(), endDate.isoformat()])

        for q in qs:
            data.append({
                **q,
                "sales": list(
                    allSalesInRange.filter(billingYear=q["billingYear"]).values())
            })

        return data

    if type is None:
        if noOfMonths == 1 and noOfDays < 32:
            salesByPeriodQS = byDays()
        elif 0 < noOfMonths < 13:
            salesByPeriodQS = byMonths()
        elif noOfMonths > 12:
            salesByPeriodQS = byYears()
    elif type == "days":
        salesByPeriodQS = byDays()
    elif type == "months":
        salesByPeriodQS = byMonths()
    elif type == "years":
        salesByPeriodQS = byYears()

    data1 = {
        "startDate": startDate,
        "endDate": endDate,
        "salesPeriodType": daterange_unit,
        'salesByPeriod': salesByPeriodQS,
        'salesByPeriodCount': salesForThePeriod.count(),
        "total": salesForThePeriod.aggregate(Sum('subTotal'))['subTotal__sum']
    }

    # currentDate = timezone.now();
    # chartStartDate = (currentDate - timezone.timedelta(days=365)).replace(day=1, hour=0, minute=0, second=0,
    #                                                                       microsecond=0)
    # chartEndDate = currentDate.replace(day=calendar.monthrange(chartStartDate.year, chartStartDate.month)[1], hour=23,
    #                                    minute=59, second=59, microsecond=999999)

    return Response(data1, status=status.HTTP_200_OK)
