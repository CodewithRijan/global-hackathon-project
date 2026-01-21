"""
GalliPark API Serializers

Serializers for all models including User, ParkingSpot, UtsavEvent, Booking, and Review.
Handles conversion between Python objects and JSON with proper validation.
"""

from rest_framework import serializers
from decimal import Decimal
import math

from .models import User, ParkingSpot, ParkingSpotImage, UtsavEvent, Booking, Review
from .services import BookingPricingService, BookingValidationService


# ========================
# User Serializers
# ========================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with authentication details.
    """
    
    class Meta:
        model = User
        fields = [
            'id', 'phone_number', 'full_name', 'email', 'is_owner', 'is_driver',
            'profile_picture', 'rating', 'total_bookings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_bookings']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration/creation with password.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password must be at least 8 characters"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Confirm password"
    )
    
    class Meta:
        model = User
        fields = [
            'phone_number', 'password', 'password_confirm', 'full_name',
            'email', 'is_owner', 'is_driver'
        ]
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    """
    
    class Meta:
        model = User
        fields = [
            'full_name', 'email', 'profile_picture', 'is_owner', 'is_driver'
        ]


# ========================
# Parking Spot Serializers
# ========================

class ParkingSpotImageSerializer(serializers.ModelSerializer):
    """
    Serializer for parking spot images.
    """
    
    class Meta:
        model = ParkingSpotImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class ParkingSpotListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing parking spots with minimal information.
    """
    owner_name = serializers.CharField(
        source='owner.full_name',
        read_only=True,
        help_text="Owner's full name"
    )
    distance_meters = serializers.SerializerMethodField(
        help_text="Distance from user location (if provided)"
    )
    available_two_wheeler = serializers.SerializerMethodField()
    available_four_wheeler = serializers.SerializerMethodField()
    
    class Meta:
        model = ParkingSpot
        fields = [
            'id', 'latitude', 'longitude', 'address', 'city', 'capacity_two_wheeler',
            'capacity_four_wheeler', 'price_per_hour_two_wheeler',
            'price_per_hour_four_wheeler', 'is_active', 'rating',
            'owner_name', 'distance_meters', 'available_two_wheeler',
            'available_four_wheeler', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_distance_meters(self, obj):
        """Calculate distance from user location if provided in context."""
        user_lat = self.context.get('user_lat')
        user_lon = self.context.get('user_lon')
        
        if user_lat is not None and user_lon is not None:
            # Haversine formula
            from math import radians, cos, sin, asin, sqrt
            
            lat1, lon1, lat2, lon2 = map(
                radians, [user_lat, user_lon, obj.latitude, obj.longitude]
            )
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            r = 6371000  # Earth radius in meters
            
            return round(c * r, 2)
        
        return None
    
    def get_available_two_wheeler(self, obj):
        """Get available two-wheeler capacity."""
        return obj.get_available_two_wheeler_capacity()
    
    def get_available_four_wheeler(self, obj):
        """Get available four-wheeler capacity."""
        return obj.get_available_four_wheeler_capacity()


class ParkingSpotDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed parking spot information including images and amenities.
    """
    images = ParkingSpotImageSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True, required=False)
    available_two_wheeler = serializers.SerializerMethodField()
    available_four_wheeler = serializers.SerializerMethodField()
    distance_meters = serializers.SerializerMethodField()
    
    class Meta:
        model = ParkingSpot
        fields = [
            'id', 'owner', 'owner_id', 'latitude', 'longitude', 'address', 'city',
            'description', 'capacity_two_wheeler', 'capacity_four_wheeler',
            'price_per_hour_two_wheeler', 'price_per_hour_four_wheeler',
            'is_active', 'amenities', 'images', 'available_two_wheeler',
            'available_four_wheeler', 'distance_meters', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_available_two_wheeler(self, obj):
        """Get available two-wheeler capacity."""
        return obj.get_available_two_wheeler_capacity()
    
    def get_available_four_wheeler(self, obj):
        """Get available four-wheeler capacity."""
        return obj.get_available_four_wheeler_capacity()
    
    def get_distance_meters(self, obj):
        """Calculate distance from user location if provided."""
        user_lat = self.context.get('user_lat')
        user_lon = self.context.get('user_lon')
        if user_lat is not None and user_lon is not None:
            from math import radians, cos, sin, asin, sqrt
            
            lat1, lon1, lat2, lon2 = map(
                radians, [user_lat, user_lon, obj.latitude, obj.longitude]
            )
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            r = 6371000  # Earth radius in meters
            
            return round(c * r, 2)
        return None


class ParkingSpotCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating parking spots.
    """
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    
    class Meta:
        model = ParkingSpot
        fields = [
            'latitude', 'longitude', 'address', 'city', 'description',
            'capacity_two_wheeler', 'capacity_four_wheeler',
            'price_per_hour_two_wheeler', 'price_per_hour_four_wheeler',
            'is_active', 'amenities'
        ]
    
    def create(self, validated_data):
        """Create parking spot with latitude/longitude."""
        # Get owner from request context
        owner = self.context['request'].user
        validated_data['owner'] = owner
        
        return ParkingSpot.objects.create(**validated_data)


# ========================
# Utsav Event Serializers
# ========================

class UtsavEventListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing Utsav events.
    """
    spot_address = serializers.CharField(
        source='spot.address',
        read_only=True
    )
    
    class Meta:
        model = UtsavEvent
        fields = [
            'id', 'spot', 'spot_address', 'event_name', 'event_date',
            'start_time', 'end_time', 'temporary_capacity_two_wheeler',
            'temporary_capacity_four_wheeler', 'temporary_price_two_wheeler',
            'temporary_price_four_wheeler', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UtsavEventDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Utsav event information.
    """
    spot = ParkingSpotDetailSerializer(read_only=True)
    spot_id = serializers.IntegerField(write_only=True, required=False)
    available_two_wheeler = serializers.SerializerMethodField()
    available_four_wheeler = serializers.SerializerMethodField()
    is_event_ongoing = serializers.SerializerMethodField()
    
    class Meta:
        model = UtsavEvent
        fields = [
            'id', 'spot', 'spot_id', 'event_name', 'event_date',
            'start_time', 'end_time', 'description',
            'temporary_capacity_two_wheeler', 'temporary_capacity_four_wheeler',
            'temporary_price_two_wheeler', 'temporary_price_four_wheeler',
            'is_active', 'available_two_wheeler', 'available_four_wheeler',
            'is_event_ongoing', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_available_two_wheeler(self, obj):
        """Get available capacity for event."""
        return obj.get_available_two_wheeler_capacity()
    
    def get_available_four_wheeler(self, obj):
        """Get available capacity for event."""
        return obj.get_available_four_wheeler_capacity()
    
    def get_is_event_ongoing(self, obj):
        """Check if event is currently happening."""
        return obj.is_event_ongoing()


# ========================
# Booking Serializers
# ========================

class BookingListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing bookings with key information.
    """
    driver_name = serializers.CharField(
        source='driver.full_name',
        read_only=True
    )
    spot_address = serializers.CharField(
        source='spot.address',
        read_only=True
    )
    event_name = serializers.SerializerMethodField()
    surcharge_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'driver', 'driver_name', 'spot', 'spot_address',
            'utsav_event', 'event_name', 'vehicle_type', 'start_time',
            'end_time', 'total_price', 'status', 'surcharge_applied',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'total_price']
    
    def get_event_name(self, obj):
        """Get event name if booking is linked to event."""
        if obj.utsav_event:
            return obj.utsav_event.event_name
        
        # Check for dynamic overlap
        overlapping = obj.check_event_overlap()
        return overlapping.event_name if overlapping else None
    
    def get_surcharge_applied(self, obj):
        """Check if surcharge was applied."""
        overlapping = obj.check_event_overlap()
        return overlapping is not None


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed booking information with pricing breakdown.
    """
    driver = UserSerializer(read_only=True)
    driver_id = serializers.IntegerField(write_only=True, required=False)
    spot = ParkingSpotDetailSerializer(read_only=True)
    spot_id = serializers.IntegerField(write_only=True, required=False)
    utsav_event = UtsavEventListSerializer(read_only=True)
    utsav_event_id = serializers.IntegerField(write_only=True, required=False)
    
    # Pricing breakdown
    base_price = serializers.SerializerMethodField()
    event_surcharge = serializers.SerializerMethodField()
    surcharge_applied = serializers.SerializerMethodField()
    event_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'driver', 'driver_id', 'spot', 'spot_id', 'utsav_event',
            'utsav_event_id', 'vehicle_type', 'start_time', 'end_time',
            'total_price', 'base_price', 'event_surcharge', 'surcharge_applied',
            'event_name', 'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']
    
    def get_base_price(self, obj):
        """Calculate and return base price."""
        try:
            pricing = BookingPricingService.calculate_booking_price(obj)
            return pricing['base_price']
        except ValueError:
            return None
    
    def get_event_surcharge(self, obj):
        """Calculate and return event surcharge."""
        try:
            pricing = BookingPricingService.calculate_booking_price(obj)
            return pricing['event_surcharge']
        except ValueError:
            return None
    
    def get_surcharge_applied(self, obj):
        """Check if surcharge applies."""
        try:
            pricing = BookingPricingService.calculate_booking_price(obj)
            return pricing['surcharge_applied']
        except ValueError:
            return False
    
    def get_event_name(self, obj):
        """Get event name if applicable."""
        if obj.utsav_event:
            return obj.utsav_event.event_name
        overlapping = obj.check_event_overlap()
        return overlapping.event_name if overlapping else None


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating bookings with backend price calculation.
    """
    driver_id = serializers.IntegerField(required=False)
    
    class Meta:
        model = Booking
        fields = [
            'spot', 'utsav_event', 'vehicle_type', 'start_time',
            'end_time', 'notes', 'driver_id'
        ]
    
    def validate(self, data):
        """Validate booking times and spot availability."""
        start_time = data['start_time']
        end_time = data['end_time']
        
        # Validate times
        is_valid, error = BookingValidationService.validate_booking_time(start_time, end_time)
        if not is_valid:
            raise serializers.ValidationError({'time': error})
        
        # Check availability
        is_available, error = BookingValidationService.check_spot_availability(
            data['spot'], start_time, end_time, data['vehicle_type']
        )
        if not is_available:
            raise serializers.ValidationError({'spot': error})
        
        return data
    
    def create(self, validated_data):
        """Create booking with backend-calculated price."""
        # Use request user as driver if not specified
        if 'driver_id' not in validated_data or not validated_data['driver_id']:
            validated_data['driver'] = self.context['request'].user
        else:
            validated_data.pop('driver_id')
        
        # Create booking instance
        booking = Booking(**validated_data)
        
        # Calculate price using service
        try:
            pricing = BookingPricingService.calculate_booking_price(booking)
            booking.total_price = pricing['total_price']
        except ValueError as e:
            raise serializers.ValidationError({'pricing': str(e)})
        
        booking.save()
        return booking


class BookingUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating booking information.
    """
    
    class Meta:
        model = Booking
        fields = ['status', 'notes']


# ========================
# Review Serializers
# ========================

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for reviews and ratings.
    """
    reviewer_name = serializers.CharField(
        source='reviewer.full_name',
        read_only=True
    )
    booking_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'booking_id', 'reviewer', 'reviewer_name',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at']
    
    def create(self, validated_data):
        """Create review with current user as reviewer."""
        validated_data['reviewer'] = self.context['request'].user
        return Review.objects.create(**validated_data)
