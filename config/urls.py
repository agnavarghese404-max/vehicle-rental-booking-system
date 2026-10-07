"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rentals.views import home, vehicle_list_page, vehicle_detail_page, register_page, login_page, logout_page, book_vehicle_page,  my_bookings_page,   cancel_booking_page, dashboard_page
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('vehicles/', vehicle_list_page, name='vehicles'),
    path('vehicles/<int:pk>/', vehicle_detail_page, name='vehicle_detail'),
    path('vehicles/<int:pk>/book/', book_vehicle_page, name='book_vehicle'),
    path('register/', register_page, name='register'),
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout'),
    path('my-bookings/', my_bookings_page, name='my_bookings'),
    path('my-bookings/<int:pk>/cancel/', cancel_booking_page, name='cancel_booking'),
    path('dashboard/', dashboard_page, name='dashboard'),
    path('admin/', admin.site.urls),
    path('api/', include('rentals.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)