from rest_framework import status
from rest_framework.exceptions import APIException


class CartItemExists(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "product added to cart already."
    default_code = "cart_item_exists"


class OrderDelivered(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Order is delivered."
    default_code = "order_delivered"


class CustomerRequired(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Need a customer to add credit bill."
    default_code = "customer_required_for_credit_bill"
