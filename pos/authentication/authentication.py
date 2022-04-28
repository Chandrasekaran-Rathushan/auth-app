import firebase_admin
import pyrebase
from django.conf import settings

from django.utils import timezone
from firebase_admin import auth, credentials
from rest_framework import authentication

from .exceptions import InvalidAuthToken, FirebaseError
from .exceptions import NoAuthToken
from .models import User, UserToken

firebase = pyrebase.initialize_app(settings.FIREBASE_CONFIG)
firebase_auth = firebase.auth()

cred = credentials.Certificate(
    settings.FIREBASE_CONFIG_CERTIFICATE
)
firebase_admin_app = firebase_admin.initialize_app(cred)


class FireBaseTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            raise NoAuthToken("No auth token provided")

        id_token = auth_header.split(" ").pop()
        decoded_token = None

        try:
            decoded_token = auth.verify_id_token(id_token)

        except Exception:
            raise InvalidAuthToken("Invalid auth token")
            pass

        if not id_token or not decoded_token:
            return None

        try:
            uid = decoded_token.get("uid")
        except Exception:
            raise FirebaseError()

        user = User.objects.get(email=decoded_token.get("email"))
        user.last_login = timezone.localtime()

        user_token = None
        try:
            user_token = UserToken.objects.get(id=vars(user)['id'])
        except UserToken.DoesNotExist:
            raise InvalidAuthToken("Invalid auth token/ you have been logged out.")

        if user_token and id_token:
            return (user, None)
        else:
            return None


# class FireBaseTokenAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         auth_header = request.META.get("HTTP_AUTHORIZATION")
#
#         if not auth_header:
#             raise NoAuthToken("No auth token provided")
#
#         id_token = auth_header.replace("Bearer ", "")
#         verified_token = None
#
#         try:
#             verified_token = firebase_auth.get_account_info(id_token)
#
#             if id_token == request.session['uid'] and verified_token['users'][0]:
#                 user = User.objects.get(email=verified_token['users'][0]['email'])
#                 user.last_login = timezone.localtime()
#
#             else:
#                 raise InvalidAuthToken("Invalid auth token")
#
#         except:
#             raise InvalidAuthToken("Invalid auth token")
#
#         if not id_token or not verified_token:
#             return None
#
#         return (user, None)


def get_pyrebase_firebase_auth():
    return firebase_auth


def get_firebase_admin_auth():
    return auth
