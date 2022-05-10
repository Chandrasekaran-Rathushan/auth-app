from datetime import datetime
from time import sleep

import requests
import simplejson

from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from google.auth import jwt

from rest_framework import viewsets, status, routers
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import get_pyrebase_firebase_auth, FireBaseTokenAuthentication, get_firebase_admin_auth
from .models import User, UserImage, UserToken
from .serializers import UserDetailsSerializer, RegisterSerializer, ImageSerializer, UserTokenSerializer
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt

firebase_auth = get_pyrebase_firebase_auth()
firebase_admin_auth = get_firebase_admin_auth()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer


class UserDetail(APIView):
    authentication_classes = [SessionAuthentication, FireBaseTokenAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get_object(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "[]"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id, format=None):
        snippet = self.get_object(id=id)
        serializer = RegisterSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        user = self.get_object(id=id)
        serializer = RegisterSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        user = self.get_object(id=id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserImageViewSet(viewsets.ModelViewSet):
    queryset = UserImage.objects.all()
    serializer_class = ImageSerializer


class UploadUserImage(APIView):
    queryset = User.objects.all()
    serializer_class = UserDetailsSerializer

    def get_object(self, id):
        try:
            return UserImage.objects.get(id=id)
        except UserImage.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        snippet = self.get_object(id=id)
        serializer = ImageSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        image = self.get_object(id=id)
        serializer = ImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        image = self.get_object(id=id)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def index(request):
    return render(request, 'index.html')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def sign_up(request):
    keys = [
        'email',
        'password1',
        'password2',
        'username'
    ]

    errors = []

    for key in keys:
        try:
            request.data[key]
        except KeyError:
            errors.append(key)

    if errors.__len__() > 0:
        return Response({"error": "Required fields are missing.", "fields": "{errors}".format(errors=errors)},
                        status.HTTP_400_BAD_REQUEST)

    email = request.data['email']
    password = request.data['password1']

    try:
        system_user = User.objects.get(email=email)

        if (system_user):
            return Response({"error": "User Already Exists"},
                            status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        serializer = UserDetailsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(request)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # creating a user with the given email and password
        user = firebase_auth.create_user_with_email_and_password(email, password)
        idToken = user['idToken']

        # session_id = user['idToken']
        # request.session['uid'] = str(session_id)

        email_verification = firebase_auth.send_email_verification(idToken)
    except:
        return Response(
            {"error": "Please Check Provided Details. Ex: {email: test@email.com, password: <minimum 6 characters>}"},
            status=status.HTTP_400_BAD_REQUEST)

    return Response({"user": user, "email_verification_status": email_verification}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def sign_in(request):
    keys = [
        'email',
        'password',
    ]

    errors = []

    for key in keys:
        try:
            request.data[key]
        except KeyError:
            errors.append(key)

    if errors.__len__() > 0:
        return Response({"error": "Required fields are missing.", "fields": "{errors}".format(errors=errors)},
                        status.HTTP_400_BAD_REQUEST)

    email = request.data['email']
    password = request.data['password']

    try:
        system_user = User.objects.get(email=email)
        if not system_user.check_password(password):
            return Response({"error": "incorrect password."}, status=status.HTTP_400_BAD_REQUEST, )

    except User.DoesNotExist:
        return Response({"error": "Email is not registered on the system."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if request.session['uid']:
            return Response({"error": "already authenticated."})
    except:
        pass

    user_token = None
    try:
        user_token = UserToken.objects.get(id=vars(system_user)['id'])
    except UserToken.DoesNotExist:
        pass

    try:
        # if there is no error then signin the user with given email and password
        user = firebase_auth.sign_in_with_email_and_password(email, password)

        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        request.session['email'] = str(user['email'])

        is_email_verified = firebase_auth.get_account_info(user['idToken'])['users'][0]['emailVerified']

        if is_email_verified:
            serializer = None

            if user_token is not None:
                serializer = UserTokenSerializer(user_token, data={
                    "user_token_id": user_token.user_token_id,
                    "id": system_user.id,
                    "idToken": user['idToken'],
                    "refreshToken": user['refreshToken'],
                    "kind": user_token.kind,
                    "localId": user_token.localId,
                    "email": user_token.email,
                    "displayName": system_user.first_name or system_user.email,
                    "registered": user['registered'],
                    "expiresIn": user['expiresIn'],
                })
            else:
                serializer = UserTokenSerializer(data={
                    "id": vars(system_user)['id'],
                    "kind": user['kind'],
                    "localId": user['localId'],
                    "email": user['email'],
                    "displayName": vars(system_user)['first_name'] or vars(system_user)['email'],
                    "idToken": user['idToken'],
                    "registered": user['registered'],
                    "refreshToken": user['refreshToken'],
                    "expiresIn": user['expiresIn'],
                })

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            signed_in_success = serializer.data

            decodedToken = jwt.decode(user['idToken'], verify=False)

            return Response(
                {
                    **signed_in_success,
                    "authTime": decodedToken["auth_time"],
                    "iat": decodedToken["iat"],
                    "exp": decodedToken["exp"],
                    "isExpired": timezone.now().timestamp() > decodedToken["exp"],
                }, status=status.HTTP_200_OK)

            # try:
            #     sleep(1)
            #     auth = firebase_admin_auth.verify_id_token(user["idToken"])
            #     print("\naurth \n" + auth)
            #     print("\naurth \n" + auth["auth_time"])
            #
            #     auth_success = {"authTime": auth["auth_time"], "iat": auth["iat"], "expireAt": auth["exp"],
            #                     "isExpired": timezone.now().timestamp() > auth["exp"]}
            #
            #     return Response(
            #         {**signed_in_success, **auth_success}, status=status.HTTP_200_OK
            #     )
            # except:
            #     return Response({**signed_in_success, "authTime": "", "iat": "", "expireAt": "", "isExpired": True})

            # return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "A verification link has been sent to your email. Please Verify"})

    except firebase_admin_auth.InvalidIdTokenError as e:
        print(e)
        return Response({"error": "InvalidIdTokenError"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except firebase_admin_auth.ExpiredIdTokenError as e:
        print(e)
        return Response({"error": "ExpiredIdTokenError"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except firebase_admin_auth.RevokedIdTokenError as e:
        print(e)
        return Response({"error": "RevokedIdTokenError"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except firebase_admin_auth.CertificateFetchError as e:
        print(e)
        return Response({"error": "CertificateFetchError"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except firebase_admin_auth.UserDisabledError as e:
        print(e)
        return Response({"error": "UserDisabledError"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except:
        message = "Invalid Credentials! Please Check Your Data."
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
def refresh_token(request):
    errors = []

    if request.GET.get('uid', None) is None:
        errors.append("uid")
    if request.GET.get('refresh_token', None) is None:
        errors.append("refresh_token")

    if errors.__len__() > 0:
        return Response({"error": "Required search queries are missing.", "fields": "{errors}".format(errors=errors)},
                        status.HTTP_400_BAD_REQUEST)

    firebase_user = None

    try:
        firebase_user = firebase_admin_auth.get_user(request.GET.get('uid', None))
    except:
        return Response({"error": "invalid uid / refresh token "})

    try:
        system_user = User.objects.get(email=firebase_user.email)
    except User.DoesNotExist:
        return Response({"error": "User is not registered on the system."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        expired_user_token = UserToken.objects.get(id=vars(system_user)['id'])
    except UserToken.DoesNotExist:
        return Response({"error": "User is not registered on the system. / you are not logged in."},
                        status=status.HTTP_400_BAD_REQUEST)

    new_token = None

    try:
        new_token = firebase_auth.refresh(request.GET.get('refresh_token', None))
        request.session['uid'] = new_token['idToken']

        decodedToken = jwt.decode(new_token['idToken'], verify=False)

        serializer = UserTokenSerializer(expired_user_token, data={
            "user_token_id": vars(expired_user_token)['user_token_id'],
            "id": vars(system_user)['id'],
            "idToken": new_token['idToken'],
            "refreshToken": new_token['refreshToken'],
            "kind": vars(expired_user_token)['kind'],
            "localId": new_token['userId'],
            "email": vars(expired_user_token)['email'],
            "displayName": vars(system_user)['first_name'] or vars(system_user)['email'],
            "registered": vars(expired_user_token)['registered'],
            "expiresIn": vars(expired_user_token)['expiresIn'],
            "created_date": datetime.utcfromtimestamp(int(decodedToken["iat"])).strftime('%Y-%m-%dT%H:%M:%SZ')
        })

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                **serializer.data,
                "authTime": decodedToken["auth_time"],
                "iat": decodedToken["iat"],
                "exp": decodedToken["exp"],
                "isExpired": timezone.now().timestamp() > decodedToken["exp"],
                "email": decodedToken['email'],
            },
            status=status.HTTP_200_OK)
    except:
        return Response({"error": "something went wrong."})


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def reset_password(request):
    try:
        email = request.data['email']
    except KeyError:
        return Response({"error": "email field is required"})

    try:
        a = firebase_auth.send_password_reset_email(email)

        return Response({"message": "A email to reset password is successfully sent"}, status=status.HTTP_200_OK)
    except:
        message = "Something went wrong, Please check the email you provided is registered or not"
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def verify_password_reset(request):
    oobCode = request.GET.get('oobCode', None)

    url = 'https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={0}'.format(
        settings.FIREBASE_CONFIG['apiKey'])
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = simplejson.dumps({"oobCode": oobCode})
    response = requests.post(url=url, headers=headers, data=data)
    json = response.json()

    return Response({"oobCode": oobCode})


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def confirm_password_reset(request):
    keys = [
        'oobCode',
        'newPassword',
    ]

    errors = []

    for key in keys:
        try:
            request.data[key]
        except KeyError:
            errors.append(key)

    if errors.__len__() > 0:
        return Response({"error": "Required fields are missing.", "fields": "{errors}".format(errors=errors)},
                        status.HTTP_400_BAD_REQUEST)

    oobCode = request.data["oobCode"]
    newPassword = request.data["newPassword"]

    url = 'https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={0}'.format(
        settings.FIREBASE_CONFIG['apiKey'])
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = simplejson.dumps({"oobCode": oobCode, "newPassword": newPassword})
    response = requests.post(url=url, headers=headers, data=data)
    json = response.json()
    return Response(json)


@csrf_exempt
@api_view(['GET'])
def sign_out(request):
    firebase_user = None
    request.session['uid'] = ""
    try:
        firebase_user = firebase_admin_auth.get_user(request.GET.get('uid', None))
    except:
        return Response({"error": "invalid uid / refresh token "})

    try:
        system_user = User.objects.get(email=firebase_user.email)
    except User.DoesNotExist:
        return Response({"error": "User is not registered on the system."}, status=status.HTTP_400_BAD_REQUEST)

    user_token = None
    try:
        user_token = UserToken.objects.get(id=vars(system_user)['id'])
        user_token.delete()
    except UserToken.DoesNotExist:
        return Response({"error": "User is not registered on the system. / you are not logged in."},
                        status=status.HTTP_400_BAD_REQUEST)

    del request.session['uid']
    return Response({"message": "You have been logged out."}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def isAuthenticated(request):
    try:
        sleep(1)
        auth = firebase_admin_auth.verify_id_token(request.GET.get("idToken", ""))
        return Response(
            {"authTime": auth["auth_time"], "iat": auth["iat"], "exp": auth["exp"],
             "isExpired": timezone.now().timestamp() > auth["exp"]})
    except:
        return Response({"authTime": "", "iat": "", "exp": "", "isExpired": True})


@csrf_exempt
@api_view(['GET'])
def authentication_urls(request):
    message = {
        "[GET] Users": "http://127.0.0.1:8000/authentication/user/",
        "[GET] User": "http://127.0.0.1:8000/authentication/user/<:id>",
        "[PUT] User": "http://127.0.0.1:8000/authentication/user/<:id>",
        "[DELETE] User": "http://127.0.0.1:8000/authentication/user/<:id>",

        "[GET] User Images": "http://127.0.0.1:8000/authentication/user_image/",
        "[POST] User": "http://127.0.0.1:8000/authentication/user_image/",
        "[GET] User Image": "http://127.0.0.1:8000/authentication/user_image/<:user_id>",
        "[PUT] User": "http://127.0.0.1:8000/authentication/user_image/<:user_id>",
        "[DELETE] User Image": "http://127.0.0.1:8000/authentication/user_image/<:user_id>",

        "sign_up": "http://127.0.0.1:8000/authentication/sign_up/",
        "sign_in": "http://127.0.0.1:8000/authentication/sign_in/",
        "refresh_token": "http://127.0.0.1:8000/authentication/refresh_token/",
        "reset_password": "http://127.0.0.1:8000/authentication/reset_password/",
        "verify_password_reset": "http://127.0.0.1:8000/authentication/verify_password_reset/",
        "confirm_password_reset": "http://127.0.0.1:8000/authentication/confirm_password_reset/",
        "sign_out": "http://127.0.0.1:8000/authentication/sign_out/",

        "test": "http://127.0.0.1:8000/authentication/test/"
    }
    return Response(message)
