from django.contrib import admin
from .models import ProfileModel



@admin.register(ProfileModel)

class ProfileModelAdmin(admin.ModelAdmin):
    list_filter = ['date_of_birth']
