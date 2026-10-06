# Vehicle Rental & Booking System

A backend REST API for managing vehicles, customers, and vehicle bookings.

## Technologies

- Python
- Django
- Django REST Framework
- MySQL
- SQLite
- HTML/CSS/Bootstrap/JavaScript

## Features

- Vehicle management
- Customer management
- Vehicle booking
- Booking validation
- Booking cancellation
- User authentication
- Customer and admin permissions
- REST API endpoints


## API Endpoints

### Vehicles

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/vehicles/` | List all vehicles |
| POST | `/api/vehicles/` | Create a vehicle |
| GET | `/api/vehicles/<id>/` | View a vehicle |
| PUT | `/api/vehicles/<id>/` | Update a vehicle |
| DELETE | `/api/vehicles/<id>/` | Delete a vehicle |

### Customers

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/customers/` | List customers |
| POST | `/api/customers/` | Create a customer |
| GET | `/api/customers/<id>/` | View a customer |
| PUT | `/api/customers/<id>/` | Update a customer |
| DELETE | `/api/customers/<id>/` | Delete a customer |

### Bookings

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/bookings/` | View bookings |
| POST | `/api/bookings/` | Create a booking |
| GET | `/api/bookings/<id>/` | View a booking |
| PUT | `/api/bookings/<id>/` | Update a booking |
| DELETE | `/api/bookings/<id>/` | Delete a booking |
| POST | `/api/bookings/<id>/cancel/` | Cancel a booking |

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a new customer |
| POST | `/api/auth/login/` | Log in a user |
| POST | `/api/auth/logout/` | Log out the current user |