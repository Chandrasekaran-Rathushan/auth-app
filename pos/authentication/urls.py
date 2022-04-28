from django.urls import path, include
from rest_framework import routers

from .views import UserViewSet, UserDetail, UserImageViewSet, UploadUserImage, index, sign_up, sign_in, refresh_token, \
    reset_password, Test, sign_out, verify_password_reset, confirm_password_reset, authentication_urls, isAuthenticated

router = routers.DefaultRouter()
router.register("user", UserViewSet)
router.register("user_image", UserImageViewSet)

urlpatterns = [
    path('', authentication_urls),
    path('', include(router.urls)),

    path('index/', index),

    path('user/<int:id>/', UserDetail.as_view()),
    path('user_image/<int:id>/', UploadUserImage.as_view()),

    path('sign_up/', sign_up, name="sign_up"),
    path('sign_in/', sign_in, name="sign_in"),
    path('refresh_token/', refresh_token, name="refresh_token"),
    path('reset_password/', reset_password, name="reset_password"),
    path('verify_password_reset/', verify_password_reset, name="verify_password_reset"),
    path('confirm_password_reset/', confirm_password_reset, name="confirm_password_reset"),
    path('sign_out/', sign_out, name="sign_out"),
    path('is_authenticated/', isAuthenticated, name="isAuthenticated"),

    path('test/', Test.as_view(), name="test"),
]
