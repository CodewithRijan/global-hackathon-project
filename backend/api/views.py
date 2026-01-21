"""
GalliPark API Views

ViewSets and Views for all endpoints including user management, parking spots,
bookings, and nearby spot discovery with distance calculations.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.db.models import F, Q, DecimalField
from decimal import Decimal
from math import radians, cos, sin, asin, sqrt

from .models import User, ParkingSpot, UtsavEvent, Booking, Review
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    ParkingSpotListSerializer, ParkingSpotDetailSerializer, ParkingSpotCreateSerializer,
    UtsavEventListSerializer, UtsavEventDetailSerializer,
    BookingListSerializer, BookingDetailSerializer, BookingCreateSerializer, BookingUpdateSerializer,
    ReviewSerializer
)
from .services import BookingPricingService, BookingValidationService


# ========================
# Pagination
# ========================

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for list views."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ========================
# User ViewSet
# ========================

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User management.
    
    Endpoints:
    - GET /users/ - List all users
    - POST /users/ - Create new user
    - GET /users/{id}/ - Retrieve user details
    - PUT /users/{id}/ - Update user
    - DELETE /users/{id}/ - Delete user
    - GET /users/me/ - Get current user
    - PUT /users/me/ - Update current user
    """
    
    queryset = User.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'phone_number', 'email']
    ordering_fields = ['created_at', 'rating', 'total_bookings']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Allow anyone to create, others need authentication."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get or update current user profile.
        
        GET /users/me/ - Returns current user
        PUT /users/me/ - Update current user
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserSerializer(user, context={'request': request})
            return Response(serializer.data)
        
        # PUT or PATCH
        serializer = UserUpdateSerializer(
            user, data=request.data, partial=request.method == 'PATCH',
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_bookings(self, request):
        """Get all bookings for current user."""
        bookings = Booking.objects.filter(driver=request.user).order_by('-created_at')
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = BookingListSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = BookingListSerializer(
            bookings, many=True, context={'request': request}
        )
        return Response(serializer.data)


# ========================
# Parking Spot ViewSet
# ========================

class ParkingSpotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Parking Spot management.
    
    Endpoints:
    - GET /spots/ - List all spots (with optional nearby filtering)
    - POST /spots/ - Create new spot
    - GET /spots/{id}/ - Retrieve spot details
    - PUT /spots/{id}/ - Update spot
    - DELETE /spots/{id}/ - Delete spot
    - GET /spots/nearby/ - Find spots within radius (by lat/lng)
    - GET /spots/owner/my-spots/ - Get current user's spots
    """
    
    queryset = ParkingSpot.objects.filter(is_active=True).select_related('owner')
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['address', 'city', 'description']
    ordering_fields = ['created_at', 'price_per_hour_two_wheeler']
    ordering = ['-created_at']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ParkingSpotCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ParkingSpotDetailSerializer
        elif self.action == 'retrieve':
            return ParkingSpotDetailSerializer
        return ParkingSpotListSerializer
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Find parking spots within specified radius of given coordinates.
        
        Query Parameters:
        - latitude (required): User's latitude
        - longitude (required): User's longitude
        - radius (optional): Search radius in meters (default: 500)
        
        Returns: List of spots sorted by distance
        
        Example:
        GET /spots/nearby/?latitude=27.7172&longitude=85.3240&radius=1000
        """
        try:
            # Get coordinates from query params
            latitude = float(request.query_params.get('latitude'))
            longitude = float(request.query_params.get('longitude'))
            radius = int(request.query_params.get('radius', 500))
            
        except (TypeError, ValueError) as e:
            return Response(
                {'error': 'Invalid latitude, longitude, or radius. Must be numbers.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all active spots
        spots = ParkingSpot.objects.filter(is_active=True)
        
        # Calculate distance using Haversine formula and filter
        def haversine_distance(lat1, lon1, lat2, lon2):
            """
            Calculate distance between two points in meters using Haversine formula.
            """
            # Convert to radians
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            r = 6371000  # Earth radius in meters
            
            return c * r
        
        # Add distance to each spot and filter by radius
        spots_with_distance = []
        for spot in spots:
            distance = haversine_distance(
                latitude, longitude,
                spot.latitude, spot.longitude
            )
            if distance <= radius:
                spots_with_distance.append({
                    'spot': spot,
                    'distance': distance
                })
        
        # Sort by distance
        spots_with_distance.sort(key=lambda x: x['distance'])
        
        # Extract sorted spots
        sorted_spots = [item['spot'] for item in spots_with_distance]
        
        # Paginate results
        page = self.paginate_queryset(sorted_spots)
        if page is not None:
            serializer = ParkingSpotListSerializer(
                page, many=True,
                context={'request': request, 'user_lat': latitude, 'user_lon': longitude}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = ParkingSpotListSerializer(
            sorted_spots, many=True,
            context={'request': request, 'user_lat': latitude, 'user_lon': longitude}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def available_events(self, request, pk=None):
        """
        Get all upcoming events for a parking spot.
        
        GET /spots/{id}/available_events/
        """
        spot = self.get_object()
        events = spot.utsav_events.filter(is_active=True).order_by('event_date')
        
        serializer = UtsavEventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Check spot availability for given time period.
        
        Query Parameters:
        - start_time (required): ISO format datetime
        - end_time (required): ISO format datetime
        - vehicle_type (required): 'two_wheeler' or 'four_wheeler'
        
        GET /spots/{id}/availability/?start_time=2026-01-25T10:00:00Z&end_time=2026-01-25T13:00:00Z&vehicle_type=two_wheeler
        """
        from datetime import datetime
        
        spot = self.get_object()
        
        try:
            start_time_str = request.query_params.get('start_time')
            end_time_str = request.query_params.get('end_time')
            vehicle_type = request.query_params.get('vehicle_type')
            
            if not all([start_time_str, end_time_str, vehicle_type]):
                return Response(
                    {'error': 'start_time, end_time, and vehicle_type are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse ISO format datetimes
            from django.utils.dateparse import parse_datetime
            start_time = parse_datetime(start_time_str)
            end_time = parse_datetime(end_time_str)
            
            if not start_time or not end_time:
                return Response(
                    {'error': 'Invalid datetime format. Use ISO format (e.g., 2026-01-25T10:00:00Z)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check availability
            is_available, error = BookingValidationService.check_spot_availability(
                spot, start_time, end_time, vehicle_type
            )
            
            return Response({
                'spot_id': spot.id,
                'vehicle_type': vehicle_type,
                'is_available': is_available,
                'message': error if not is_available else 'Spot is available',
                'available_capacity': (
                    spot.get_available_two_wheeler_capacity()
                    if vehicle_type == 'two_wheeler'
                    else spot.get_available_four_wheeler_capacity()
                )
            })
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_spots(self, request):
        """
        Get all parking spots owned by current user.
        
        GET /spots/owner/my-spots/
        """
        spots = ParkingSpot.objects.filter(owner=request.user).order_by('-created_at')
        page = self.paginate_queryset(spots)
        
        if page is not None:
            serializer = ParkingSpotDetailSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = ParkingSpotDetailSerializer(
            spots, many=True, context={'request': request}
        )
        return Response(serializer.data)


# ========================
# Utsav Event ViewSet
# ========================

class UtsavEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Utsav Event management (temporary event-based parking).
    
    Endpoints:
    - GET /events/ - List all events
    - POST /events/ - Create new event
    - GET /events/{id}/ - Retrieve event details
    - PUT /events/{id}/ - Update event
    - DELETE /events/{id}/ - Delete event
    - GET /events/upcoming/ - List upcoming events
    """
    
    queryset = UtsavEvent.objects.filter(is_active=True).select_related('spot')
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['event_name', 'spot__address']
    ordering_fields = ['event_date', 'temporary_price_two_wheeler']
    ordering = ['-event_date']
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'retrieve':
            return UtsavEventDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return UtsavEventDetailSerializer
        return UtsavEventListSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming events sorted by date.
        
        GET /events/upcoming/
        """
        from django.utils import timezone
        
        today = timezone.now().date()
        events = UtsavEvent.objects.filter(
            is_active=True,
            event_date__gte=today
        ).order_by('event_date')
        
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = UtsavEventListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UtsavEventListSerializer(events, many=True)
        return Response(serializer.data)


# ========================
# Booking ViewSet
# ========================

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Booking management.
    
    Endpoints:
    - GET /bookings/ - List all bookings
    - POST /bookings/ - Create new booking
    - GET /bookings/{id}/ - Retrieve booking details
    - PUT /bookings/{id}/ - Update booking
    - DELETE /bookings/{id}/ - Cancel booking
    - POST /bookings/{id}/activate/ - Activate pending booking
    - POST /bookings/{id}/complete/ - Mark booking as completed
    - POST /bookings/{id}/cancel/ - Cancel booking
    """
    
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['start_time', 'created_at', 'total_price']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return bookings visible to current user."""
        user = self.request.user
        if user.is_driver:
            # Drivers see their own bookings
            return Booking.objects.filter(driver=user).select_related(
                'driver', 'spot', 'utsav_event'
            )
        elif user.is_owner:
            # Owners see bookings for their spots
            return Booking.objects.filter(
                spot__owner=user
            ).select_related('driver', 'spot', 'utsav_event')
        return Booking.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action == 'retrieve':
            return BookingDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        return BookingListSerializer
    
    def perform_create(self, serializer):
        """Ensure driver is set to current user when creating."""
        serializer.save(driver=self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a pending booking.
        
        POST /bookings/{id}/activate/
        """
        booking = self.get_object()
        
        if booking.status != Booking.PENDING:
            return Response(
                {'error': f'Can only activate PENDING bookings. Current status: {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.activate()
        serializer = BookingDetailSerializer(booking, context={'request': request})
        return Response(
            {'message': 'Booking activated', 'booking': serializer.data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark an active booking as completed.
        
        POST /bookings/{id}/complete/
        """
        booking = self.get_object()
        
        if booking.status != Booking.ACTIVE:
            return Response(
                {'error': f'Can only complete ACTIVE bookings. Current status: {booking.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.complete()
        serializer = BookingDetailSerializer(booking, context={'request': request})
        return Response(
            {'message': 'Booking completed', 'booking': serializer.data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        
        POST /bookings/{id}/cancel/
        """
        booking = self.get_object()
        
        if booking.status == Booking.COMPLETED:
            return Response(
                {'error': 'Cannot cancel a completed booking'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.status == Booking.CANCELLED:
            return Response(
                {'error': 'Booking is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.cancel()
        serializer = BookingDetailSerializer(booking, context={'request': request})
        return Response(
            {'message': 'Booking cancelled', 'booking': serializer.data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def pricing_breakdown(self, request, pk=None):
        """
        Get detailed pricing breakdown for a booking.
        
        GET /bookings/{id}/pricing_breakdown/
        """
        booking = self.get_object()
        
        try:
            pricing = BookingPricingService.calculate_booking_price(booking)
            return Response({
                'booking_id': booking.id,
                'vehicle_type': booking.vehicle_type,
                'duration_hours': (booking.end_time - booking.start_time).total_seconds() / 3600,
                'hourly_rate': (
                    booking.utsav_event.temporary_price_two_wheeler
                    if booking.utsav_event and booking.vehicle_type == 'two_wheeler'
                    else booking.utsav_event.temporary_price_four_wheeler
                    if booking.utsav_event
                    else booking.spot.price_per_hour_two_wheeler
                    if booking.vehicle_type == 'two_wheeler'
                    else booking.spot.price_per_hour_four_wheeler
                ),
                'base_price': float(pricing['base_price']),
                'event_surcharge_percent': 20 if pricing['surcharge_applied'] else 0,
                'event_surcharge_amount': float(pricing['event_surcharge']),
                'total_price': float(pricing['total_price']),
                'overlapping_event': (
                    {
                        'id': pricing['overlapping_event'].id,
                        'name': pricing['overlapping_event'].event_name,
                        'date': pricing['overlapping_event'].event_date,
                    }
                    if pricing['overlapping_event'] else None
                )
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ========================
# Review ViewSet
# ========================

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review management.
    
    Endpoints:
    - GET /reviews/ - List all reviews
    - POST /reviews/ - Create new review
    - GET /reviews/{id}/ - Retrieve review details
    - PUT /reviews/{id}/ - Update review
    - DELETE /reviews/{id}/ - Delete review
    """
    
    queryset = Review.objects.all().select_related('booking', 'reviewer')
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter reviews by spot owner or reviewer."""
        user = self.request.user
        if user.is_owner:
            # Owners see reviews for their spots
            return Review.objects.filter(
                booking__spot__owner=user
            ).select_related('booking', 'reviewer')
        elif user.is_driver:
            # Drivers see reviews they wrote
            return Review.objects.filter(
                reviewer=user
            ).select_related('booking', 'reviewer')
        return Review.objects.all().select_related('booking', 'reviewer')
