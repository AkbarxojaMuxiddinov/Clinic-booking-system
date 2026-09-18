from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Client, Service, Booking

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email', 'telegram_id')
    search_fields = ('full_name', 'phone', 'email')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'booking_date', 'status')
    list_filter = ('status', 'booking_date')


