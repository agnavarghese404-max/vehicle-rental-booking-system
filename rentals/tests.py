from django.contrib.auth import get_user_model
from django.test import TestCase
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


class WebsitePagesTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='webuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='webother',
            password='testpass123'
        )

        self.customer = Customer.objects.create(
            user=self.user,
            name='Web Customer',
            email='web@example.com',
            phone='9876543200',
            driving_license='WEB123'
        )
        self.other_customer = Customer.objects.create(
            user=self.other_user,
            name='Web Other',
            email='webother@example.com',
            phone='9876543201',
            driving_license='WEB456'
        )

        self.car = Vehicle.objects.create(
            vehicle_type='car',
            name='Test Car',
            brand='Test Brand',
            model='Test Model',
            registration_number='WEB001',
            price_per_day=1000,
            is_available=True
        )
        self.bike = Vehicle.objects.create(
            vehicle_type='bike',
            name='Test Bike',
            brand='Bike Brand',
            model='Bike Model',
            registration_number='WEB002',
            price_per_day=500,
            is_available=True
        )

    def test_home_page_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_vehicle_list_shows_vehicles(self):
        response = self.client.get('/vehicles/')
        self.assertContains(response, 'Test Car')

    def test_vehicle_list_type_filter(self):
        response = self.client.get('/vehicles/?type=bike')
        self.assertContains(response, 'Test Bike')
        self.assertNotContains(response, 'Test Car')

    def test_booking_page_requires_login(self):
        response = self.client.get(f'/vehicles/{self.car.id}/book/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_customer_can_book_vehicle(self):
        self.client.login(username='webuser', password='testpass123')

        response = self.client.post(f'/vehicles/{self.car.id}/book/', {
            'start_date': '2027-03-01',
            'end_date': '2027-03-04',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.customer, self.customer)
        self.assertEqual(booking.total_amount, 3000)

    def test_overlapping_booking_is_rejected(self):
        Booking.objects.create(
            customer=self.other_customer,
            vehicle=self.car,
            start_date='2027-03-01',
            end_date='2027-03-05',
            status='pending',
            total_amount=4000
        )
        self.client.login(username='webuser', password='testpass123')

        self.client.post(f'/vehicles/{self.car.id}/book/', {
            'start_date': '2027-03-03',
            'end_date': '2027-03-06',
        })

        self.assertEqual(Booking.objects.count(), 1)

    def test_customer_can_cancel_own_booking(self):
        booking = Booking.objects.create(
            customer=self.customer,
            vehicle=self.car,
            start_date='2027-04-01',
            end_date='2027-04-03',
            status='pending',
            total_amount=2000
        )
        self.client.login(username='webuser', password='testpass123')

        self.client.post(f'/my-bookings/{booking.id}/cancel/')

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')

    def test_customer_cannot_cancel_other_customers_booking(self):
        booking = Booking.objects.create(
            customer=self.other_customer,
            vehicle=self.car,
            start_date='2027-05-01',
            end_date='2027-05-03',
            status='pending',
            total_amount=2000
        )
        self.client.login(username='webuser', password='testpass123')

        response = self.client.post(f'/my-bookings/{booking.id}/cancel/')

        self.assertEqual(response.status_code, 404)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'pending')

    def test_dashboard_is_staff_only(self):
        self.client.login(username='webuser', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 302)

        User.objects.create_user(
            username='staffuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='staffuser', password='testpass123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)

class OwnerPagesTest(TestCase):

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username='owner1', password='testpass123'
        )
        self.staff = User.objects.create_user(
            username='staff1', password='testpass123', is_staff=True
        )
        self.user = User.objects.create_user(
            username='cust1', password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name='Owner Test Customer',
            email='ownertest@example.com',
            phone='9876543299',
            driving_license='OWN123'
        )
        self.vehicle = Vehicle.objects.create(
            vehicle_type='car',
            name='Owner Test Car',
            brand='Brand',
            model='Model',
            registration_number='OWN001',
            price_per_day=1000,
            is_available=True
        )
        self.booking = Booking.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date='2027-06-01',
            end_date='2027-06-03',
            status='pending',
            total_amount=2000
        )

    def test_owner_can_open_manage_bookings(self):
        self.client.login(username='owner1', password='testpass123')
        response = self.client.get('/dashboard/bookings/')
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_open_manage_bookings(self):
        self.client.login(username='staff1', password='testpass123')
        response = self.client.get('/dashboard/bookings/')
        self.assertEqual(response.status_code, 302)

    def test_owner_can_confirm_pending_booking(self):
        self.client.login(username='owner1', password='testpass123')
        self.client.post(f'/dashboard/bookings/{self.booking.id}/confirm/')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')

    def test_customer_cannot_confirm_own_booking(self):
        self.client.login(username='cust1', password='testpass123')
        self.client.post(f'/dashboard/bookings/{self.booking.id}/confirm/')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'pending')

    def test_cancelled_booking_cannot_be_revived(self):
        self.booking.status = 'cancelled'
        self.booking.save()
        self.client.login(username='owner1', password='testpass123')
        self.client.post(f'/dashboard/bookings/{self.booking.id}/confirm/')
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')


class CalendarTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='caluser', password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            name='Calendar Customer',
            email='cal@example.com',
            phone='9876543288',
            driving_license='CAL123'
        )
        self.vehicle = Vehicle.objects.create(
            vehicle_type='car',
            name='Calendar Car',
            brand='Brand',
            model='Model',
            registration_number='CAL001',
            price_per_day=1000,
            is_available=True
        )
        self.client.login(username='caluser', password='testpass123')

    def test_booked_days_do_not_include_return_day(self):
        Booking.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date='2027-07-10',
            end_date='2027-07-13',
            status='confirmed',
            total_amount=3000
        )

        response = self.client.get(f'/vehicles/{self.vehicle.id}/book/')

        self.assertEqual(
            response.context['booked_ranges'],
            [{'from': '2027-07-10', 'to': '2027-07-12'}]
        )

    def test_cancelled_booking_does_not_block_calendar(self):
        Booking.objects.create(
            customer=self.customer,
            vehicle=self.vehicle,
            start_date='2027-08-10',
            end_date='2027-08-13',
            status='cancelled',
            total_amount=3000
        )

        response = self.client.get(f'/vehicles/{self.vehicle.id}/book/')

        self.assertEqual(response.context['booked_ranges'], [])