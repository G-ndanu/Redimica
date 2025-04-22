from django.contrib import admin
from .models import Profile
from .models import Doctor

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'specialty', 'contact_number', 'gender')  # Customize fields as needed
    search_fields = ('first_name', 'last_name', 'specialty')