from django.contrib import admin
from .models import UserProfile, SecureFolder, SecureData, AccessLog

admin.site.register(UserProfile)
admin.site.register(SecureFolder)
admin.site.register(SecureData)
admin.site.register(AccessLog)
