"""
GalliPark Booking Pricing Examples

This document demonstrates how to use the booking pricing calculation functions
with proper event surcharge handling.
"""

# ========================
# EXAMPLE 1: Using the Service Function
# ========================

from api.services import BookingPricingService
from api.models import Booking, ParkingSpot, User, UtsavEvent
from datetime import datetime, timedelta
from django.utils import timezone

# Create example booking
driver = User.objects.get(phone_number="9841234567")
spot = ParkingSpot.objects.get(id=1)

booking = Booking(
    driver=driver,
    spot=spot,
    vehicle_type="two_wheeler",
    start_time=timezone.now() + timedelta(days=1, hours=2),
    end_time=timezone.now() + timedelta(days=1, hours=5),
)

# Calculate price using service function
price_details = BookingPricingService.calculate_booking_price(booking)

print("Booking Price Calculation:")
print(f"  Base Price: Rs. {price_details['base_price']}")
print(f"  Event Surcharge Applied: {price_details['surcharge_applied']}")
print(f"  Event Surcharge Amount: Rs. {price_details['event_surcharge']}")
print(f"  Total Price: Rs. {price_details['total_price']}")
if price_details['overlapping_event']:
    print(f"  Overlapping Event: {price_details['overlapping_event'].event_name}")


# ========================
# EXAMPLE 2: Using the Model Method
# ========================

# After creating and saving a booking
booking.total_price = booking.calculate_total_price()
booking.save()

print(f"\nBooking saved with total price: Rs. {booking.total_price}")


# ========================
# EXAMPLE 3: Scenario - Regular Booking WITHOUT Event
# ========================

# Regular spot booking (no event)
regular_booking = Booking(
    driver=driver,
    spot=spot,  # Regular price: Rs. 50 per hour for two-wheelers
    vehicle_type="two_wheeler",
    start_time=timezone.now() + timedelta(days=2, hours=10),
    end_time=timezone.now() + timedelta(days=2, hours=13),  # 3 hours
)

price_details = BookingPricingService.calculate_booking_price(regular_booking)
# Expected: 3 hours * Rs. 50 = Rs. 150 (no surcharge)
print(f"\nRegular Booking (No Event):")
print(f"  Duration: 3 hours")
print(f"  Hourly Rate: Rs. 50")
print(f"  Base Price: Rs. {price_details['base_price']}")
print(f"  Event Surcharge: Rs. {price_details['event_surcharge']}")
print(f"  Total Price: Rs. {price_details['total_price']}")


# ========================
# EXAMPLE 4: Scenario - Booking WITH Event Overlap (20% Surcharge Applied)
# ========================

# Create a Utsav event at the spot
event = UtsavEvent.objects.create(
    spot=spot,
    event_name="Gai Jatra 2026",
    event_date=timezone.now().date() + timedelta(days=3),
    start_time=timezone.now().time(),
    end_time=(timezone.now() + timedelta(hours=8)).time(),
    temporary_capacity_two_wheeler=100,
    temporary_price_two_wheeler=60,  # Higher event pricing
)

# Booking that overlaps with the event
event_booking = Booking(
    driver=driver,
    spot=spot,
    utsav_event=event,  # Explicitly linked to event
    vehicle_type="two_wheeler",
    start_time=event.event_date.replace(hour=14, minute=0) + timedelta(days=0),
    end_time=event.event_date.replace(hour=17, minute=0) + timedelta(days=0),  # 3 hours
)

# Make the datetime aware
event_booking.start_time = timezone.make_aware(
    timezone.datetime.combine(event.event_date, event.start_time)
) + timedelta(hours=2)
event_booking.end_time = event_booking.start_time + timedelta(hours=3)

price_details = BookingPricingService.calculate_booking_price(event_booking)
# Expected: 3 hours * Rs. 60 = Rs. 180 base
#          + (Rs. 180 * 0.20) = Rs. 36 surcharge
#          = Rs. 216 total
print(f"\nEvent Booking (With 20% Surcharge):")
print(f"  Duration: 3 hours")
print(f"  Hourly Rate: Rs. 60 (event rate)")
print(f"  Base Price: Rs. {price_details['base_price']}")
print(f"  Event Surcharge (20%): Rs. {price_details['event_surcharge']}")
print(f"  Total Price: Rs. {price_details['total_price']}")
print(f"  Event: {price_details['overlapping_event'].event_name if price_details['overlapping_event'] else 'None'}")


# ========================
# EXAMPLE 5: Creating Booking with Service and Saving
# ========================

def create_booking_with_pricing(driver, spot, vehicle_type, start_time, end_time):
    """
    Helper function to create a booking and calculate price in one go.
    """
    from api.services import BookingValidationService
    
    # Validate booking time
    is_valid, error_msg = BookingValidationService.validate_booking_time(start_time, end_time)
    if not is_valid:
        raise ValueError(f"Invalid booking time: {error_msg}")
    
    # Check spot availability
    is_available, error_msg = BookingValidationService.check_spot_availability(
        spot, start_time, end_time, vehicle_type
    )
    if not is_available:
        raise ValueError(f"Spot not available: {error_msg}")
    
    # Create booking
    booking = Booking(
        driver=driver,
        spot=spot,
        vehicle_type=vehicle_type,
        start_time=start_time,
        end_time=end_time,
    )
    
    # Calculate price
    price_details = BookingPricingService.calculate_booking_price(booking)
    
    # Set the calculated price (backend ensures no manipulation)
    booking.total_price = price_details['total_price']
    booking.save()
    
    return booking, price_details


# Usage
new_booking, pricing = create_booking_with_pricing(
    driver=driver,
    spot=spot,
    vehicle_type="two_wheeler",
    start_time=timezone.now() + timedelta(days=5, hours=10),
    end_time=timezone.now() + timedelta(days=5, hours=12),
)

print(f"\nNewly Created Booking #{ new_booking.id}:")
print(f"  Total Price: Rs. {pricing['total_price']}")
print(f"  Status: {new_booking.status}")


# ========================
# EXAMPLE 6: Checking Event Overlap Before Booking
# ========================

# Check if a time period overlaps with any events
from api.services import BookingPricingService

test_start = timezone.now() + timedelta(days=3, hours=14)
test_end = test_start + timedelta(hours=2)

test_booking = Booking(
    driver=driver,
    spot=spot,
    vehicle_type="two_wheeler",
    start_time=test_start,
    end_time=test_end,
)

overlapping_event = BookingPricingService._check_event_overlap(test_booking)

if overlapping_event:
    print(f"\nEvent Overlap Detected:")
    print(f"  Event: {overlapping_event.event_name}")
    print(f"  Event Date: {overlapping_event.event_date}")
    print(f"  Event Time: {overlapping_event.start_time} - {overlapping_event.end_time}")
    print(f"  Surcharge: 20% will be applied to base price")
else:
    print(f"\nNo event overlap - regular pricing applies")


# ========================
# IMPLEMENTATION NOTES
# ========================

"""
1. BACKEND PRICE CALCULATION:
   - All prices are calculated on the backend to prevent frontend manipulation
   - The service function returns detailed pricing breakdown
   - Use this before saving booking to ensure accuracy

2. EVENT SURCHARGE LOGIC:
   - 20% surcharge applied when booking overlaps with UtsavEvent
   - Overlap check is done on the booking date with event time range
   - Surcharge = base_price * 0.20
   - Total = base_price + surcharge

3. TIME VALIDATION:
   - Always validate booking times before creating booking
   - Minimum booking duration: 1 hour
   - Cannot book in the past
   - End time must be after start time

4. AVAILABILITY CHECK:
   - Verify spot has available capacity for vehicle type
   - Check for overlapping active/pending bookings
   - Account for both regular and event-based capacity

5. BEST PRACTICES:
   - Always use BookingPricingService for price calculations
   - Validate times with BookingValidationService
   - Check availability before confirming booking
   - Save the calculated total_price to Booking model
   - Use transaction decorators for atomic operations
"""
