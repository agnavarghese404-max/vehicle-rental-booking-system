from django.db import models
from django.conf import settings

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('suv', 'SUV'),
        ('van', 'Van'),
    ]
    
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model} - {self.registration_number}"


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    driving_license = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check that end date is not before start date
        if self.end_date < self.start_date:
            raise ValidationError(
                "End date cannot be before start date."
            )

        # Calculate total rental amount automatically
        days = (self.end_date - self.start_date).days

        if days <= 0:
            raise ValidationError(
                "Booking must be for at least one day."
            )

        self.total_amount = self.vehicle.price_per_day * days


        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            vehicle=self.vehicle,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        ).exclude(pk=self.pk).exclude(status='cancelled')

        if overlapping_bookings.exists():
            raise ValidationError(
                "This vehicle is already booked for the selected dates."
            )

    def __str__(self):
        return f"{self.customer.name} - {self.vehicle}"
