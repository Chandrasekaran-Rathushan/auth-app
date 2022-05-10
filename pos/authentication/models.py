import datetime

from cloudinary.models import CloudinaryField
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.utils import timezone


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')
        if not password:
            raise ValueError('The given password must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.is_superuser = is_superuser
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username=username, email=email, password=password,
                                 **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, is_staff=True, is_superuser=True,
                                 **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now())
    dateOfBirth = models.DateTimeField(blank=True, null=True)
    address = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    country = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]


class UserImage(models.Model):
    id = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    image = CloudinaryField("image")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            user = User.objects.get(email=self.id)
            user.image = f"{'https://res.cloudinary.com/du6anfr7y/image/upload/v1644128933/' + str(self.image)}"
            user.save()

        except Exception as e:
            print(e)


class UserToken(models.Model):
    user_token_id = models.AutoField(primary_key=True)
    id = models.ForeignKey(User, on_delete=models.CASCADE)
    kind = models.CharField(max_length=255)
    localId = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    displayName = models.CharField(max_length=255)
    idToken = models.TextField()
    registered = models.BooleanField()
    refreshToken = models.TextField()
    expiresIn = models.CharField(max_length=255)
    created_date = models.DateTimeField(default=timezone.now())
