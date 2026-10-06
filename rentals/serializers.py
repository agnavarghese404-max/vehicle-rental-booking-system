from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from .models import Vehicle, Customer, Booking
User = get_user_model()

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    driving_license = serializers.CharField(max_length=50)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A customer with this email already exists."
            )
        return value

    def validate_driving_license(self, value):
        if Customer.objects.filter(driving_license=value).exists():
            raise serializers.ValidationError(
                "A customer with this driving license already exists."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        username = validated_data.pop('username')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=validated_data['email']
        )

        return Customer.objects.create(
            user=user,
            **validated_data
        )

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class BookingSerializer(serializers.ModelSerializer):

    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    customer_name = serializers.CharField(
        source='customer.name',
        read_only=True
    )

    vehicle_name = serializers.CharField(
        source='vehicle.name',
        read_only=True
    )

    vehicle_brand = serializers.CharField(
        source='vehicle.brand',
        read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id',
            'customer',
            'customer_name',
            'vehicle',
            'vehicle_name',
            'vehicle_brand',
            'start_date',
            'end_date',
            'total_amount',
            'status',
            'created_at'
        ]



    def validate(self, data):
        booking = Booking(**data)

        # Validate dates, calculate amount,
        # and check overlapping bookings
        booking.clean()

        data['total_amount'] = booking.total_amount

        return data
