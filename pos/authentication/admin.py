from django.contrib import admin

from .models import User, UserImage, UserToken

admin.site.register(User)
admin.site.register(UserImage)
admin.site.register(UserToken)
