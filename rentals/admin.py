from django.contrib import admin
from .models import Vehicle, Customer, Booking

admin.site.register(Vehicle)
admin.site.register(Customer)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    readonly_fields = ('total_amount',)