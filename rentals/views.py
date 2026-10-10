from django.db import models
from datetime import timedelta
from django.db.models import Q, Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsBookingOwnerOrAdmin


from .models import Vehicle, Booking, Customer
from .serializers import (
    VehicleSerializer,
    BookingSerializer,
    CustomerSerializer,
    RegistrationSerializer,
    LoginSerializer,
)

class RegisterAPIView(APIView):

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            customer = serializer.save()

            return Response(
                {
                    "message": "Registration successful.",
                    "customer": CustomerSerializer(customer).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginAPIView(APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )

        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        login(request, user)

        return Response({
            "message": "Login successful."
        })


class LogoutAPIView(APIView):

    def post(self, request):
        logout(request)

        return Response({
            "message": "Logout successful."
        })

class VehicleListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]

        return []

    def get(self, request):
        vehicles = Vehicle.objects.all()

        available = request.query_params.get('available')

        if available == 'true':
            vehicles = vehicles.filter(is_available=True)

        elif available == 'false':
            vehicles = vehicles.filter(is_available=False)

        vehicle_type = request.query_params.get('type')

        if vehicle_type:
            vehicles = vehicles.filter(vehicle_type=vehicle_type)

        search = request.query_params.get('search')

        if search:
            vehicles = vehicles.filter(
                models.Q(name__icontains=search) |
                models.Q(brand__icontains=search)
            )

        max_price = request.query_params.get('max_price')

        if max_price:
            vehicles = vehicles.filter(price_per_day__lte=max_price)

        min_price = request.query_params.get('min_price')

        if min_price:
            vehicles = vehicles.filter(price_per_day__gte=min_price)

        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VehicleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdminUser()]
        return []

    def get_vehicle(self, pk):
        try:
            return Vehicle.objects.get(pk=pk)
        except Vehicle.DoesNotExist:
            raise NotFound(detail="Vehicle not found.")

    def get(self, request, pk):
        vehicle = self.get_vehicle(pk)
        serializer = VehicleSerializer(vehicle)
        return Response(serializer.data)

    def put(self, request, pk):
        vehicle = self.get_vehicle(pk)
        serializer = VehicleSerializer(vehicle, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        vehicle = self.get_vehicle(pk)
        vehicle.delete()
        return Response({"message": "Vehicle deleted successfully"})


class BookingListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            bookings = Booking.objects.all()
        else:
            customer = Customer.objects.get(user=request.user)
            bookings = Booking.objects.filter(customer=customer)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    def post(self, request):
        customer = Customer.objects.get(user=request.user)

        data = request.data.copy()
        data['customer'] = customer.id

        serializer = BookingSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsBookingOwnerOrAdmin]

    def get_booking(self, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            raise NotFound(detail="Booking not found.")

        self.check_object_permissions(self.request, booking)

        return booking


    def get(self, request, pk):
        booking = self.get_booking(pk)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    
    def post(self, request, pk):
        booking = self.get_booking(pk)

        if booking.status == 'cancelled':
            return Response(
                {"detail": "Booking is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == 'completed':
            return Response(
                {"detail": "Completed bookings cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save()

        return Response({
            "message": "Booking cancelled successfully.",
            "booking_id": booking.id,
            "status": booking.status
        })

    def put(self, request, pk):
        booking = self.get_booking(pk)

        data = request.data.copy()
        data['customer'] = booking.customer.id

        serializer = BookingSerializer(booking, data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    
    def delete(self, request, pk):
        booking = self.get_booking(pk)
        booking.delete()
        return Response({"message": "Booking deleted successfully"})


class CustomerListAPIView(APIView):
    def get_permissions(self):
        return [IsAdminUser()]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomerDetailAPIView(APIView):
    def get_permissions(self):
        return [IsAdminUser()]

    def get_customer(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            raise NotFound(detail="Customer not found.")

    def get(self, request, pk):
        customer = self.get_customer(pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def put(self, request, pk):
        customer = self.get_customer(pk)
        serializer = CustomerSerializer(customer, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        customer = self.get_customer(pk)
        customer.delete()
        return Response({"message": "Customer deleted successfully"})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required


def home(request):
    featured_vehicles = Vehicle.objects.filter(is_available=True).order_by('-id')[:3]
    return render(request, 'home.html', {'featured_vehicles': featured_vehicles})


def vehicle_list_page(request):
    vehicles = Vehicle.objects.all()

    query = request.GET.get('q', '')
    vehicle_type = request.GET.get('type', '')

    if query:
        vehicles = vehicles.filter(Q(name__icontains=query) | Q(brand__icontains=query))
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)

    return render(request, 'vehicle_list.html', {
        'vehicles': vehicles,
        'query': query,
        'selected_type': vehicle_type,
    })

def vehicle_detail_page(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    return render(request, 'vehicle_detail.html', {'vehicle': vehicle})

def register_page(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.POST)

        if serializer.is_valid():
            serializer.save()
            return redirect('home')

        return render(request, 'register.html', {
            'errors': serializer.errors,
            'form_data': request.POST,
        })

    return render(request, 'register.html')

def login_page(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.POST)

        if serializer.is_valid():
            user = authenticate(
                request,
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
            )

            if user is not None:
                login(request, user)
                return redirect('home')

            error = "Invalid username or password."
        else:
            error = "Please enter both username and password."

        return render(request, 'login.html', {
            'error': error,
            'username': request.POST.get('username', ''),
        })

    return render(request, 'login.html')

def logout_page(request):
    if request.method == 'POST':
        logout(request)
    return redirect('home')


@login_required(login_url='login')
def my_bookings_page(request):
    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return render(request, 'my_bookings.html', {'bookings': []})

    bookings = Booking.objects.filter(customer=customer).select_related('vehicle').order_by('-created_at')

    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required(login_url='login')
def cancel_booking_page(request, pk):
    customer = Customer.objects.filter(user=request.user).first()
    booking = get_object_or_404(Booking, pk=pk, customer=customer)

    if request.method == 'POST' and booking.status in ('pending', 'confirmed'):
        booking.status = 'cancelled'
        booking.save()

    return redirect('my_bookings')

@staff_member_required(login_url='login')
def dashboard_page(request):
    revenue = Booking.objects.filter(
        status__in=['confirmed', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'total_vehicles': Vehicle.objects.count(),
        'available_vehicles': Vehicle.objects.filter(is_available=True).count(),
        'total_customers': Customer.objects.count(),
        'total_bookings': Booking.objects.count(),
        'pending_bookings': Booking.objects.filter(status='pending').count(),
        'revenue': revenue,
        'recent_bookings': Booking.objects.select_related('customer', 'vehicle').order_by('-created_at')[:5],
    }
    return render(request, 'dashboard.html', context)

def is_owner(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_owner, login_url='login')
def owner_bookings_page(request):
    status = request.GET.get('status', '')

    bookings = Booking.objects.select_related('customer', 'vehicle').order_by('-created_at')
    if status:
        bookings = bookings.filter(status=status)

    return render(request, 'owner_bookings.html', {
        'bookings': bookings,
        'selected_status': status,
    })

@user_passes_test(is_owner, login_url='login')
def owner_booking_action(request, pk, action):
    booking = get_object_or_404(Booking, pk=pk)

    rules = {
        'confirm': (['pending'], 'confirmed'),
        'complete': (['confirmed'], 'completed'),
        'cancel': (['pending', 'confirmed'], 'cancelled'),
    }

    if request.method == 'POST' and action in rules:
        allowed_from, new_status = rules[action]
        if booking.status in allowed_from:
            Booking.objects.filter(pk=booking.pk).update(status=new_status)

    return redirect('owner_bookings')

def get_booked_ranges(vehicle):
    bookings = Booking.objects.filter(vehicle=vehicle).exclude(status='cancelled')
    return [
        {
            'from': b.start_date.isoformat(),
            'to': (b.end_date - timedelta(days=1)).isoformat(),
        }
        for b in bookings
    ]


@login_required(login_url='login')
def book_vehicle_page(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    try:
        customer = Customer.objects.get(user=request.user)
    except Customer.DoesNotExist:
        return render(request, 'book_vehicle.html', {
            'vehicle': vehicle,
            'booked_ranges': get_booked_ranges(vehicle),
            'errors': {'account': ['Only customer accounts can book vehicles.']},
        })

    if request.method == 'POST':
        data = {
            'customer': customer.id,
            'vehicle': vehicle.id,
            'start_date': request.POST.get('start_date'),
            'end_date': request.POST.get('end_date'),
        }
        serializer = BookingSerializer(data=data)

        if serializer.is_valid():
            booking = serializer.save()
            return render(request, 'book_vehicle.html', {
                'vehicle': vehicle,
                'booking': booking,
                'booked_ranges': get_booked_ranges(vehicle),
            })

        return render(request, 'book_vehicle.html', {
            'vehicle': vehicle,
            'booked_ranges': get_booked_ranges(vehicle),
            'errors': serializer.errors,
            'form_data': request.POST,
        })

    return render(request, 'book_vehicle.html', {
        'vehicle': vehicle,
        'booked_ranges': get_booked_ranges(vehicle),
    })