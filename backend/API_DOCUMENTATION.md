# GalliPark API Documentation

Complete REST API documentation for the GalliPark micro-parking marketplace.

---

## Base URL

```
http://localhost:8000/api/
```

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Endpoints](#user-endpoints)
3. [Parking Spot Endpoints](#parking-spot-endpoints)
4. [Utsav Event Endpoints](#utsav-event-endpoints)
5. [Booking Endpoints](#booking-endpoints)
6. [Review Endpoints](#review-endpoints)
7. [Error Responses](#error-responses)
8. [Example Workflows](#example-workflows)

---

## Authentication

### Token-Based (SimpleJWT)

This API uses JWT tokens for stateless authentication.

**Get Token:**
```
POST /api/token/
{
    "phone_number": "9841234567",
    "password": "yourpassword"
}
```

**Use Token:**
```
Authorization: Bearer <your_token>
```

**Refresh Token:**
```
POST /api/token/refresh/
{
    "refresh": "<refresh_token>"
}
```

---

## User Endpoints

### List All Users
```
GET /api/users/
```

**Query Parameters:**
- `search`: Search by name, phone, or email
- `ordering`: Order by `created_at`, `rating`, `total_bookings`
- `page`: Page number
- `page_size`: Results per page (default: 20, max: 100)

**Example:**
```
GET /api/users/?search=John&ordering=-rating&page=1
```

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "phone_number": "9841234567",
      "full_name": "John Doe",
      "email": "john@example.com",
      "is_owner": true,
      "is_driver": true,
      "rating": 4.5,
      "total_bookings": 25,
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-01-20T14:30:00Z"
    }
  ]
}
```

### Create User (Register)
```
POST /api/users/
```

**Request:**
```json
{
  "phone_number": "9841234567",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "full_name": "John Doe",
  "email": "john@example.com",
  "is_owner": true,
  "is_driver": true
}
```

**Response (201 Created):**
```json
{
  "id": 45,
  "phone_number": "9841234567",
  "full_name": "John Doe",
  "email": "john@example.com",
  "is_owner": true,
  "is_driver": true,
  "rating": 0.0,
  "total_bookings": 0,
  "created_at": "2026-01-21T10:00:00Z"
}
```

### Get Current User
```
GET /api/users/me/
Authorization: Bearer <token>
```

### Update Current User
```
PUT /api/users/me/
Authorization: Bearer <token>
```

**Request:**
```json
{
  "full_name": "John Doe Updated",
  "email": "newemail@example.com",
  "is_owner": true,
  "is_driver": false
}
```

### Get User's Bookings
```
GET /api/users/my_bookings/
Authorization: Bearer <token>
```

---

## Parking Spot Endpoints

### List All Parking Spots
```
GET /api/spots/
```

**Query Parameters:**
- `search`: Search by address, city, description
- `ordering`: Order by `created_at`, `price_per_hour_two_wheeler`
- `page`: Page number
- `page_size`: Results per page

**Response:**
```json
{
  "count": 320,
  "results": [
    {
      "id": 1,
      "location": {
        "type": "Point",
        "coordinates": [85.3240, 27.7172]
      },
      "address": "Thamel, Kathmandu",
      "city": "Kathmandu",
      "capacity_two_wheeler": 20,
      "capacity_four_wheeler": 10,
      "price_per_hour_two_wheeler": 50.0,
      "price_per_hour_four_wheeler": 100.0,
      "is_active": true,
      "owner_name": "John Doe",
      "distance_meters": 234.5,
      "available_two_wheeler": 15,
      "available_four_wheeler": 8,
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

### Find Nearby Parking Spots (Within 500m)
```
GET /api/spots/nearby/?latitude=27.7172&longitude=85.3240&radius=500
```

**Query Parameters:**
- `latitude` (required): User's latitude
- `longitude` (required): User's longitude
- `radius` (optional): Search radius in meters (default: 500)
- `page`: Page number for results
- `page_size`: Results per page

**Response:**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "address": "Thamel, Kathmandu",
      "distance_meters": 45.3,
      "available_two_wheeler": 15,
      "price_per_hour_two_wheeler": 50.0,
      ...
    },
    {
      "id": 5,
      "address": "Lazimpat, Kathmandu",
      "distance_meters": 128.7,
      "available_two_wheeler": 8,
      ...
    }
  ]
}
```

### Get Parking Spot Details
```
GET /api/spots/{id}/
```

**Response:**
```json
{
  "id": 1,
  "owner": {...},
  "location": {...},
  "address": "Thamel, Kathmandu",
  "description": "Secure parking with CCTV",
  "capacity_two_wheeler": 20,
  "capacity_four_wheeler": 10,
  "price_per_hour_two_wheeler": 50.0,
  "price_per_hour_four_wheeler": 100.0,
  "is_active": true,
  "amenities": ["covered", "lit", "cctv"],
  "images": [
    {
      "id": 1,
      "image": "http://...",
      "uploaded_at": "2026-01-15T10:00:00Z"
    }
  ],
  "available_two_wheeler": 15,
  "available_four_wheeler": 8,
  "distance_meters": null,
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z"
}
```

### Create Parking Spot
```
POST /api/spots/
Authorization: Bearer <token>
```

**Request:**
```json
{
  "latitude": 27.7172,
  "longitude": 85.3240,
  "address": "Thamel, Kathmandu",
  "city": "Kathmandu",
  "description": "Secure parking with CCTV surveillance",
  "capacity_two_wheeler": 20,
  "capacity_four_wheeler": 10,
  "price_per_hour_two_wheeler": 50.0,
  "price_per_hour_four_wheeler": 100.0,
  "is_active": true,
  "amenities": ["covered", "lit", "cctv", "secure"]
}
```

### Check Spot Availability
```
GET /api/spots/{id}/availability/?start_time=2026-01-25T10:00:00Z&end_time=2026-01-25T13:00:00Z&vehicle_type=two_wheeler
```

**Query Parameters:**
- `start_time` (required): ISO format datetime
- `end_time` (required): ISO format datetime
- `vehicle_type` (required): 'two_wheeler' or 'four_wheeler'

**Response:**
```json
{
  "spot_id": 1,
  "vehicle_type": "two_wheeler",
  "is_available": true,
  "message": "Spot is available",
  "available_capacity": 15
}
```

### Get Spot's Events
```
GET /api/spots/{id}/available_events/
```

### Get Current User's Spots
```
GET /api/spots/my_spots/
Authorization: Bearer <token>
```

---

## Utsav Event Endpoints

### List All Events
```
GET /api/events/
```

**Query Parameters:**
- `search`: Search by event name or spot address
- `ordering`: Order by `event_date`, `temporary_price_two_wheeler`
- `page`: Page number

**Response:**
```json
{
  "count": 45,
  "results": [
    {
      "id": 1,
      "spot": 5,
      "spot_address": "Thamel, Kathmandu",
      "event_name": "Gai Jatra 2026",
      "event_date": "2026-08-15",
      "start_time": "12:00:00",
      "end_time": "20:00:00",
      "temporary_capacity_two_wheeler": 100,
      "temporary_capacity_four_wheeler": 50,
      "temporary_price_two_wheeler": 60.0,
      "temporary_price_four_wheeler": 120.0,
      "is_active": true,
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

### Get Upcoming Events
```
GET /api/events/upcoming/
```

### Get Event Details
```
GET /api/events/{id}/
```

**Response:**
```json
{
  "id": 1,
  "spot": {...},
  "event_name": "Gai Jatra 2026",
  "event_date": "2026-08-15",
  "start_time": "12:00:00",
  "end_time": "20:00:00",
  "description": "Grand carnival at Thamel",
  "temporary_capacity_two_wheeler": 100,
  "temporary_capacity_four_wheeler": 50,
  "temporary_price_two_wheeler": 60.0,
  "temporary_price_four_wheeler": 120.0,
  "is_active": true,
  "available_two_wheeler": 75,
  "available_four_wheeler": 40,
  "is_event_ongoing": false,
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z"
}
```

---

## Booking Endpoints

### List All Bookings
```
GET /api/bookings/
Authorization: Bearer <token>
```

**Query Parameters:**
- `ordering`: Order by `start_time`, `created_at`, `total_price`
- `page`: Page number

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "driver": 10,
      "driver_name": "Jane Driver",
      "spot": 5,
      "spot_address": "Thamel, Kathmandu",
      "utsav_event": null,
      "event_name": null,
      "vehicle_type": "two_wheeler",
      "start_time": "2026-01-25T10:00:00Z",
      "end_time": "2026-01-25T13:00:00Z",
      "total_price": 150.0,
      "status": "pending",
      "surcharge_applied": false,
      "created_at": "2026-01-21T10:00:00Z"
    }
  ]
}
```

### Create Booking
```
POST /api/bookings/
Authorization: Bearer <token>
```

**Request:**
```json
{
  "spot": 5,
  "utsav_event": null,
  "vehicle_type": "two_wheeler",
  "start_time": "2026-01-25T10:00:00Z",
  "end_time": "2026-01-25T13:00:00Z",
  "notes": "Need secure parking"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "driver": 10,
  "spot": 5,
  "vehicle_type": "two_wheeler",
  "start_time": "2026-01-25T10:00:00Z",
  "end_time": "2026-01-25T13:00:00Z",
  "total_price": 150.0,
  "status": "pending",
  "notes": "Need secure parking",
  "created_at": "2026-01-21T10:00:00Z"
}
```

### Get Booking Details
```
GET /api/bookings/{id}/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "driver": {...},
  "spot": {...},
  "utsav_event": null,
  "vehicle_type": "two_wheeler",
  "start_time": "2026-01-25T10:00:00Z",
  "end_time": "2026-01-25T13:00:00Z",
  "total_price": 150.0,
  "base_price": 150.0,
  "event_surcharge": 0.0,
  "surcharge_applied": false,
  "event_name": null,
  "status": "pending",
  "notes": "Need secure parking",
  "created_at": "2026-01-21T10:00:00Z",
  "updated_at": "2026-01-21T10:00:00Z"
}
```

### Get Pricing Breakdown
```
GET /api/bookings/{id}/pricing_breakdown/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "booking_id": 1,
  "vehicle_type": "two_wheeler",
  "duration_hours": 3.0,
  "hourly_rate": 60.0,
  "base_price": 180.0,
  "event_surcharge_percent": 20,
  "event_surcharge_amount": 36.0,
  "total_price": 216.0,
  "overlapping_event": {
    "id": 5,
    "name": "Gai Jatra 2026",
    "date": "2026-08-15"
  }
}
```

### Activate Booking
```
POST /api/bookings/{id}/activate/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Booking activated",
  "booking": {...}
}
```

### Complete Booking
```
POST /api/bookings/{id}/complete/
Authorization: Bearer <token>
```

### Cancel Booking
```
POST /api/bookings/{id}/cancel/
Authorization: Bearer <token>
```

---

## Review Endpoints

### List Reviews
```
GET /api/reviews/
Authorization: Bearer <token>
```

**Query Parameters:**
- `ordering`: Order by `rating`, `created_at`

**Response:**
```json
{
  "count": 200,
  "results": [
    {
      "id": 1,
      "booking": 10,
      "reviewer": 15,
      "reviewer_name": "Jane Driver",
      "rating": 5,
      "comment": "Excellent spot! Very secure and clean.",
      "created_at": "2026-01-20T10:00:00Z"
    }
  ]
}
```

### Create Review
```
POST /api/reviews/
Authorization: Bearer <token>
```

**Request:**
```json
{
  "booking": 10,
  "rating": 5,
  "comment": "Excellent spot! Very secure and clean."
}
```

### Update Review
```
PUT /api/reviews/{id}/
Authorization: Bearer <token>
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid latitude, longitude, or radius. Must be numbers."
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Example Workflows

### Workflow 1: Driver Finding Parking and Booking

**Step 1: Register as Driver**
```bash
POST /api/users/
{
  "phone_number": "9841234567",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "full_name": "Jane Driver",
  "is_driver": true
}
```

**Step 2: Find Nearby Spots**
```bash
GET /api/spots/nearby/?latitude=27.7172&longitude=85.3240&radius=500
```

**Step 3: Check Spot Availability**
```bash
GET /api/spots/1/availability/?start_time=2026-01-25T10:00:00Z&end_time=2026-01-25T13:00:00Z&vehicle_type=two_wheeler
```

**Step 4: Create Booking**
```bash
POST /api/bookings/
Authorization: Bearer <token>
{
  "spot": 1,
  "vehicle_type": "two_wheeler",
  "start_time": "2026-01-25T10:00:00Z",
  "end_time": "2026-01-25T13:00:00Z"
}
```

**Step 5: Get Pricing Details**
```bash
GET /api/bookings/1/pricing_breakdown/
Authorization: Bearer <token>
```

### Workflow 2: Owner Creating Event-Based Parking

**Step 1: Create Parking Spot**
```bash
POST /api/spots/
Authorization: Bearer <owner_token>
{
  "latitude": 27.7172,
  "longitude": 85.3240,
  "address": "Party Palace, Thamel",
  "capacity_two_wheeler": 50,
  "price_per_hour_two_wheeler": 50.0
}
```

**Step 2: Create Event**
```bash
POST /api/events/
Authorization: Bearer <owner_token>
{
  "spot": 1,
  "event_name": "Gai Jatra 2026",
  "event_date": "2026-08-15",
  "start_time": "12:00:00",
  "end_time": "20:00:00",
  "temporary_capacity_two_wheeler": 100,
  "temporary_price_two_wheeler": 60.0
}
```

**Step 3: View Bookings**
```bash
GET /api/bookings/
Authorization: Bearer <owner_token>
```

### Workflow 3: Viewing Pricing with Event Surcharge

**Scenario: Booking during Utsav Event**

When a driver books during event time:
- Regular price: Rs. 50/hour
- Event price: Rs. 60/hour
- Duration: 3 hours
- Event surcharge: 20%

**Calculation:**
```
Base price = 3 × 60 = 180 NPR
Surcharge = 180 × 0.20 = 36 NPR
Total = 216 NPR
```

**Response from pricing_breakdown:**
```json
{
  "base_price": 180.0,
  "event_surcharge_percent": 20,
  "event_surcharge_amount": 36.0,
  "total_price": 216.0,
  "overlapping_event": {
    "name": "Gai Jatra 2026"
  }
}
```

---

## Rate Limiting

Currently no rate limiting is configured. This should be added for production.

---

## Pagination

All list endpoints use pagination with:
- Default page size: 20
- Maximum page size: 100
- Query parameter: `?page_size=50`

Example:
```
GET /api/spots/?page=2&page_size=50
```

---

## Filtering and Ordering

### Search Filters
- Users: `name`, `phone`, `email`
- Spots: `address`, `city`, `description`
- Events: `event_name`, `spot.address`

Example:
```
GET /api/spots/?search=Thamel
```

### Ordering
Most endpoints support ordering by multiple fields.

Example:
```
GET /api/spots/?ordering=-price_per_hour_two_wheeler,created_at
```

---

**Last Updated:** January 21, 2026
