from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from allauth.account.adapter import get_adapter
from .models import User, UserImage, UserToken


class ImageSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects.all())
    image = serializers.ImageField(required=True)

    class Meta:
        model = UserImage
        fields = '__all__'


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, write_only=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    dateOfBirth = serializers.DateField(required=True, write_only=True)
    image = serializers.CharField(required=False, write_only=True)
    address = serializers.CharField(required=False, write_only=True)
    city = serializers.CharField(required=False, write_only=True)
    state = serializers.CharField(required=False, write_only=True)
    country = serializers.CharField(required=False, write_only=True)
    phone = serializers.CharField(required=False, write_only=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)
    is_superuser = serializers.BooleanField(required=False, default=False, write_only=True)

    validate_password = make_password

    # def validate_password1(self, password):
    #     return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
                "The two password fields didn't match.")
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'dateOfBirth': self.validated_data.get('dateOfBirth', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'image': self.validated_data.get('image', ''),
            'address': self.validated_data.get('address', ''),
            'city': self.validated_data.get('city', ''),
            'state': self.validated_data.get('state', ''),
            'country': self.validated_data.get('country', ''),
            'phone': self.validated_data.get('phone', ''),
            'is_superuser': self.validated_data.get('is_superuser', ''),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        user.save()
        return user


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'dateOfBirth', 'image', 'address', 'city', 'state', 'country', 'phone', 'is_superuser')

    validate_password = make_password

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'dateOfBirth': self.validated_data.get('dateOfBirth', ''),
            'email': self.validated_data.get('email', ''),
            'image': self.validated_data.get('image', ''),
            'address': self.validated_data.get('address', ''),
            'city': self.validated_data.get('city', ''),
            'state': self.validated_data.get('state', ''),
            'country': self.validated_data.get('country', ''),
            'phone': self.validated_data.get('phone', ''),
            'is_superuser': self.validated_data.get('is_superuser', ''),
        }

    def save(self, request):
        isAdmin = False

        try:
            isAdmin = request.data['is_superuser']
        except:
            isAdmin = False

        if (isAdmin):
            user = User.objects.create_superuser(username=request.data['username'],
                                                 email=request.data['email'],
                                                 password=request.data['password1'],
                                                 first_name=request.data['first_name'],
                                                 last_name=request.data['last_name'],
                                                 dateOfBirth=request.data['dateOfBirth'],
                                                 )
            return user
        else:
            adapter = get_adapter()
            user = adapter.new_user(request)
            self.cleaned_data = self.get_cleaned_data()
            adapter.save_user(request, user, self)
            self.custom_signup(request, user)
            user.save()
            return user


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = '__all__'
