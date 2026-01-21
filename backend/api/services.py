"""
GalliPark Service Layer

Service functions for business logic including pricing calculations,
booking validations, and complex queries.
"""

from decimal import Decimal
from django.utils import timezone
from .models import Booking, UtsavEvent


class BookingPricingService:
    """
    Service class for booking pricing calculations.
    
    Handles:
    - Base price calculation
    - Event overlap detection
    - Event surcharge application (20% for overlapping events)
    - Price validation
    """
    
    EVENT_SURCHARGE_PERCENTAGE = Decimal("0.20")  # 20% surcharge for events
    
    @staticmethod
    def calculate_booking_price(booking):
        """
        Calculate the total price for a booking with event surcharge logic.
        
        This service function ensures all price calculations are done server-side,
        preventing frontend manipulation of pricing.
        
        Args:
            booking (Booking): The booking instance to calculate price for
            
        Returns:
            dict: {
                'base_price': Decimal,
                'event_surcharge': Decimal,
                'total_price': Decimal,
                'overlapping_event': UtsavEvent or None,
                'surcharge_applied': bool
            }
            
        Raises:
            ValueError: If booking has invalid time range or pricing
        """
        # Validate booking times
        if booking.end_time <= booking.start_time:
            raise ValueError("Booking end time must be after start time")
        
        # Calculate duration in hours
        duration_seconds = (booking.end_time - booking.start_time).total_seconds()
        duration_hours = Decimal(duration_seconds) / Decimal("3600")
        
        # Determine hourly rate based on vehicle type and event
        hourly_rate = BookingPricingService._get_hourly_rate(booking)
        
        # Calculate base price
        base_price = duration_hours * hourly_rate
        
        # Check for event overlap
        overlapping_event = BookingPricingService._check_event_overlap(booking)
        
        # Apply surcharge if event overlaps
        event_surcharge = Decimal("0")
        surcharge_applied = False
        
        if overlapping_event:
            event_surcharge = base_price * BookingPricingService.EVENT_SURCHARGE_PERCENTAGE
            surcharge_applied = True
        
        total_price = base_price + event_surcharge
        
        return {
            'base_price': base_price.quantize(Decimal('0.01')),
            'event_surcharge': event_surcharge.quantize(Decimal('0.01')),
            'total_price': total_price.quantize(Decimal('0.01')),
            'overlapping_event': overlapping_event,
            'surcharge_applied': surcharge_applied
        }
    
    @staticmethod
    def _get_hourly_rate(booking):
        """
        Get the hourly rate for a booking based on vehicle type and context.
        
        Args:
            booking (Booking): The booking instance
            
        Returns:
            Decimal: Hourly rate in NPR
        """
        if booking.utsav_event:
            # Use event pricing if explicitly linked to an event
            if booking.vehicle_type == "two_wheeler":
                return booking.utsav_event.temporary_price_two_wheeler
            else:
                return booking.utsav_event.temporary_price_four_wheeler
        else:
            # Use regular spot pricing
            if booking.vehicle_type == "two_wheeler":
                return booking.spot.price_per_hour_two_wheeler
            else:
                return booking.spot.price_per_hour_four_wheeler
    
    @staticmethod
    def _check_event_overlap(booking):
        """
        Check if the booking time overlaps with any active UtsavEvent on the parking spot.
        
        Args:
            booking (Booking): The booking instance
            
        Returns:
            UtsavEvent: The first overlapping event found, or None
        """
        # Get all active events for this spot on the booking date
        events = booking.spot.utsav_events.filter(
            is_active=True,
            event_date=booking.start_time.date()
        )
        
        for event in events:
            if BookingPricingService._times_overlap(
                booking.start_time,
                booking.end_time,
                event.event_date,
                event.start_time,
                event.end_time
            ):
                return event
        
        return None
    
    @staticmethod
    def _times_overlap(booking_start, booking_end, event_date, event_start, event_end):
        """
        Check if booking time range overlaps with event time range.
        
        Args:
            booking_start (datetime): Booking start time
            booking_end (datetime): Booking end time
            event_date (date): Event date
            event_start (time): Event start time
            event_end (time): Event end time
            
        Returns:
            bool: True if times overlap, False otherwise
        """
        # Convert event times to datetime for comparison
        event_start_dt = timezone.make_aware(
            timezone.datetime.combine(event_date, event_start)
        )
        event_end_dt = timezone.make_aware(
            timezone.datetime.combine(event_date, event_end)
        )
        
        # Check for overlap: two ranges overlap if one doesn't end before the other starts
        return not (booking_end <= event_start_dt or booking_start >= event_end_dt)


class BookingValidationService:
    """
    Service class for booking validation logic.
    
    Handles:
    - Time validation
    - Capacity checking
    - Availability verification
    """
    
    @staticmethod
    def validate_booking_time(start_time, end_time):
        """
        Validate that booking times are logical and in the future.
        
        Args:
            start_time (datetime): Booking start time
            end_time (datetime): Booking end time
            
        Returns:
            tuple: (is_valid: bool, error_message: str)
        """
        if end_time <= start_time:
            return False, "End time must be after start time"
        
        if start_time < timezone.now():
            return False, "Start time cannot be in the past"
        
        if (end_time - start_time).total_seconds() < 3600:
            return False, "Minimum booking duration is 1 hour"
        
        return True, ""
    
    @staticmethod
    def check_spot_availability(spot, start_time, end_time, vehicle_type, exclude_booking=None):
        """
        Check if a parking spot is available for the given time period.
        
        Args:
            spot (ParkingSpot): The parking spot to check
            start_time (datetime): Booking start time
            end_time (datetime): Booking end time
            vehicle_type (str): Type of vehicle ('two_wheeler' or 'four_wheeler')
            exclude_booking (Booking, optional): Booking to exclude from availability check (for updates)
            
        Returns:
            tuple: (is_available: bool, error_message: str)
        """
        from django.db.models import Q
        
        # Get overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            spot=spot,
            status__in=[Booking.PENDING, Booking.ACTIVE],
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        if exclude_booking:
            overlapping_bookings = overlapping_bookings.exclude(id=exclude_booking.id)
        
        booking_count = overlapping_bookings.count()
        
        # Check capacity
        if vehicle_type == "two_wheeler":
            available_capacity = spot.get_available_two_wheeler_capacity()
            if booking_count >= spot.capacity_two_wheeler:
                return False, "No available two-wheeler spots for the requested time period"
        else:
            available_capacity = spot.get_available_four_wheeler_capacity()
            if booking_count >= spot.capacity_four_wheeler:
                return False, "No available four-wheeler spots for the requested time period"
        
        return True, ""
