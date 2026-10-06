from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Customer, Vehicle, Booking


User = get_user_model()


class BookingAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )

        self.customer = Customer.objects.create(
            user=self.user,
            name='Test Customer',
            email='test@example.com',
            phone='9876543210',
            driving_license='TEST123'
        )

        self.other_customer = Customer.objects.create(
            user=self.other_user,
            name='Other Customer',
            email='other@example.com',
            phone='9876543211',
            driving_license='TEST456'
        )

        self.vehicle = Vehicle.objects.create(
            vehicle_type='car',
            name='Test Car',
            brand='Test Brand',
            model='Test Model',
            registration_number='TEST001',
            price_per_day=1000,
            is_available=True
        )

    def test_booking_requires_login(self):
        response = self.client.get('/api/bookings/')

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_customer_can_view_own_bookings(self):
        Booking.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date='2027-01-01',
            end_date='2027-01-03',
            status='pending',
            total_amount=2000
        )

        self.client.login(
            username='testuser',
            password='testpass123'
        )

        response = self.client.get('/api/bookings/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(len(response.data), 1)

    def test_customer_cannot_view_another_customer_booking(self):
        booking = Booking.objects.create(
            customer=self.other_customer,
            vehicle=self.vehicle,
            start_date='2027-02-01',
            end_date='2027-02-03',
            status='pending',
            total_amount=2000
        )

        self.client.login(
            username='testuser',
            password='testpass123'
        )

        response = self.client.get(
            f'/api/bookings/{booking.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )