from django.http import Http404, JsonResponse
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
