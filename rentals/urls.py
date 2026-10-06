from django.urls import path
from .views import (
    VehicleListAPIView,
    VehicleDetailAPIView,
    BookingListAPIView,
    BookingDetailAPIView,
    CustomerListAPIView,
    CustomerDetailAPIView,
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
)

urlpatterns = [
    path('vehicles/', VehicleListAPIView.as_view()),
    path('vehicles/<int:pk>/', VehicleDetailAPIView.as_view()),
    path('bookings/', BookingListAPIView.as_view()),
    path('bookings/<int:pk>/', BookingDetailAPIView.as_view()),
    path('bookings/<int:pk>/cancel/', BookingDetailAPIView.as_view()),
    path('customers/', CustomerListAPIView.as_view()),
    path('customers/<int:pk>/', CustomerDetailAPIView.as_view()),
    path('auth/register/', RegisterAPIView.as_view()),
    path('auth/login/', LoginAPIView.as_view()),
    path('auth/logout/', LogoutAPIView.as_view()),
]