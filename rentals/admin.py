from django.contrib import admin
from .models import Vehicle, Customer, Booking


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'model', 'vehicle_type', 'price_per_day', 'is_available')
    list_filter = ('vehicle_type', 'is_available')
    search_fields = ('name', 'brand', 'registration_number')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'driving_license')
    search_fields = ('name', 'email', 'driving_license')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    readonly_fields = ('total_amount',)
    list_display = ('id', 'customer', 'vehicle', 'start_date', 'end_date', 'total_amount', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('customer__name', 'vehicle__name', 'vehicle__registration_number')
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    @admin.action(description='Mark selected bookings as Confirmed')
    def mark_confirmed(self, request, queryset):
        count = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{count} booking(s) confirmed.')

    @admin.action(description='Mark selected bookings as Completed')
    def mark_completed(self, request, queryset):
        count = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f'{count} booking(s) completed.')

    @admin.action(description='Mark selected bookings as Cancelled')
    def mark_cancelled(self, request, queryset):
        count = queryset.filter(status__in=['pending', 'confirmed']).update(status='cancelled')
        self.message_user(request, f'{count} booking(s) cancelled.')