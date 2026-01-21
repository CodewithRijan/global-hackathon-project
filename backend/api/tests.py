"""
GalliPark Booking Pricing Unit Tests

Comprehensive test suite for booking price calculation with event surcharge logic.
"""

from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, datetime, time
from django.contrib.gis.geos import Point

from api.models import Booking, ParkingSpot, User, UtsavEvent
from api.services import BookingPricingService, BookingValidationService


class BookingPricingServiceTests(TestCase):
    """Test suite for BookingPricingService"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test fixtures"""
        # Create test user
        cls.user = User.objects.create_user(
            phone_number="9841234567",
            password="testpass123",
            full_name="Test User",
            is_driver=True,
            is_owner=True
        )
        
        # Create parking spot
        cls.spot = ParkingSpot.objects.create(
            owner=cls.user,
            location=Point(85.3240, 27.7172),  # Kathmandu
            address="Thamel, Kathmandu",
            city="Kathmandu",
            capacity_two_wheeler=20,
            capacity_four_wheeler=10,
            price_per_hour_two_wheeler=Decimal("50.00"),
            price_per_hour_four_wheeler=Decimal("100.00"),
            is_active=True
        )
        
        # Create Utsav event
        cls.event_date = timezone.now().date() + timedelta(days=5)
        cls.event = UtsavEvent.objects.create(
            spot=cls.spot,
            event_name="Gai Jatra 2026",
            event_date=cls.event_date,
            start_time=time(12, 0),  # 12:00 PM
            end_time=time(20, 0),     # 8:00 PM
            temporary_capacity_two_wheeler=100,
            temporary_capacity_four_wheeler=50,
            temporary_price_two_wheeler=Decimal("60.00"),
            temporary_price_four_wheeler=Decimal("120.00"),
            is_active=True
        )
    
    def test_regular_booking_two_wheeler_price_calculation(self):
        """Test price calculation for regular 2-wheeler booking without event"""
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="two_wheeler",
            start_time=timezone.now() + timedelta(days=1, hours=2),
            end_time=timezone.now() + timedelta(days=1, hours=5),  # 3 hours
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # 3 hours * Rs. 50 = Rs. 150
        self.assertEqual(pricing['base_price'], Decimal('150.00'))
        self.assertEqual(pricing['event_surcharge'], Decimal('0.00'))
        self.assertEqual(pricing['total_price'], Decimal('150.00'))
        self.assertFalse(pricing['surcharge_applied'])
        self.assertIsNone(pricing['overlapping_event'])
    
    def test_regular_booking_four_wheeler_price_calculation(self):
        """Test price calculation for regular 4-wheeler booking without event"""
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="four_wheeler",
            start_time=timezone.now() + timedelta(days=1, hours=10),
            end_time=timezone.now() + timedelta(days=1, hours=12),  # 2 hours
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # 2 hours * Rs. 100 = Rs. 200
        self.assertEqual(pricing['base_price'], Decimal('200.00'))
        self.assertEqual(pricing['event_surcharge'], Decimal('0.00'))
        self.assertEqual(pricing['total_price'], Decimal('200.00'))
        self.assertFalse(pricing['surcharge_applied'])
    
    def test_event_booking_two_wheeler_with_surcharge(self):
        """Test 2-wheeler booking with 20% event surcharge"""
        # Create booking that overlaps with event
        booking_start = timezone.make_aware(
            datetime.combine(self.event_date, time(14, 0))  # 2:00 PM
        )
        booking_end = booking_start + timedelta(hours=3)
        
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="two_wheeler",
            start_time=booking_start,
            end_time=booking_end,
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # 3 hours * Rs. 60 = Rs. 180 base
        # Rs. 180 * 0.20 = Rs. 36 surcharge
        # Total = Rs. 216
        self.assertEqual(pricing['base_price'], Decimal('180.00'))
        self.assertEqual(pricing['event_surcharge'], Decimal('36.00'))
        self.assertEqual(pricing['total_price'], Decimal('216.00'))
        self.assertTrue(pricing['surcharge_applied'])
        self.assertEqual(pricing['overlapping_event'].id, self.event.id)
    
    def test_event_booking_four_wheeler_with_surcharge(self):
        """Test 4-wheeler booking with 20% event surcharge"""
        booking_start = timezone.make_aware(
            datetime.combine(self.event_date, time(15, 0))  # 3:00 PM
        )
        booking_end = booking_start + timedelta(hours=2)
        
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="four_wheeler",
            start_time=booking_start,
            end_time=booking_end,
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # 2 hours * Rs. 120 = Rs. 240 base
        # Rs. 240 * 0.20 = Rs. 48 surcharge
        # Total = Rs. 288
        self.assertEqual(pricing['base_price'], Decimal('240.00'))
        self.assertEqual(pricing['event_surcharge'], Decimal('48.00'))
        self.assertEqual(pricing['total_price'], Decimal('288.00'))
        self.assertTrue(pricing['surcharge_applied'])
    
    def test_fractional_hour_booking_price(self):
        """Test price calculation for fractional hour duration"""
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="two_wheeler",
            start_time=timezone.now() + timedelta(days=2, hours=10),
            end_time=timezone.now() + timedelta(days=2, hours=11, minutes=30),  # 1.5 hours
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # 1.5 hours * Rs. 50 = Rs. 75
        self.assertEqual(pricing['base_price'], Decimal('75.00'))
        self.assertEqual(pricing['total_price'], Decimal('75.00'))
    
    def test_event_booking_explicit_utsav_event_link(self):
        """Test booking explicitly linked to UtsavEvent"""
        booking_start = timezone.make_aware(
            datetime.combine(self.event_date, time(13, 0))
        )
        booking_end = booking_start + timedelta(hours=4)
        
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            utsav_event=self.event,  # Explicitly linked
            vehicle_type="two_wheeler",
            start_time=booking_start,
            end_time=booking_end,
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # Should use event pricing and apply surcharge
        # 4 hours * Rs. 60 = Rs. 240
        # Rs. 240 * 0.20 = Rs. 48
        # Total = Rs. 288
        self.assertEqual(pricing['base_price'], Decimal('240.00'))
        self.assertEqual(pricing['event_surcharge'], Decimal('48.00'))
        self.assertEqual(pricing['total_price'], Decimal('288.00'))
    
    def test_booking_before_event_no_surcharge(self):
        """Test booking that ends before event starts - no surcharge"""
        # Event is 12:00 - 20:00, booking ends at 11:00
        booking_start = timezone.make_aware(
            datetime.combine(self.event_date, time(9, 0))
        )
        booking_end = timezone.make_aware(
            datetime.combine(self.event_date, time(11, 0))
        )
        
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="two_wheeler",
            start_time=booking_start,
            end_time=booking_end,
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # Should NOT apply surcharge
        self.assertEqual(pricing['event_surcharge'], Decimal('0.00'))
        self.assertFalse(pricing['surcharge_applied'])
    
    def test_booking_after_event_no_surcharge(self):
        """Test booking that starts after event ends - no surcharge"""
        # Event is 12:00 - 20:00, booking starts at 21:00
        booking_start = timezone.make_aware(
            datetime.combine(self.event_date, time(21, 0))
        )
        booking_end = timezone.make_aware(
            datetime.combine(self.event_date, time(23, 0))
        )
        
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="two_wheeler",
            start_time=booking_start,
            end_time=booking_end,
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # Should NOT apply surcharge
        self.assertEqual(pricing['event_surcharge'], Decimal('0.00'))
        self.assertFalse(pricing['surcharge_applied'])
    
    def test_booking_partial_event_overlap(self):
        """Test booking that partially overlaps with event"""
        # Event is 12:00 - 20:00, booking is 18:00 - 22:00 (2 hour overlap)
        booking_start = timezone.make_aware(
            datetime.combine(self.event_date, time(18, 0))
        )
        booking_end = timezone.make_aware(
            datetime.combine(self.event_date, time(22, 0))
        )
        
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="two_wheeler",
            start_time=booking_start,
            end_time=booking_end,
        )
        
        pricing = BookingPricingService.calculate_booking_price(booking)
        
        # Should apply surcharge (event overlaps)
        # 4 hours * Rs. 50 = Rs. 200
        # Rs. 200 * 0.20 = Rs. 40
        # Total = Rs. 240
        self.assertEqual(pricing['base_price'], Decimal('200.00'))
        self.assertEqual(pricing['event_surcharge'], Decimal('40.00'))
        self.assertEqual(pricing['total_price'], Decimal('240.00'))
        self.assertTrue(pricing['surcharge_applied'])
    
    def test_invalid_booking_time_raises_error(self):
        """Test that invalid time ranges raise ValueError"""
        booking = Booking(
            driver=self.user,
            spot=self.spot,
            vehicle_type="two_wheeler",
            start_time=timezone.now() + timedelta(hours=5),
            end_time=timezone.now() + timedelta(hours=2),  # End before start!
        )
        
        with self.assertRaises(ValueError):
            BookingPricingService.calculate_booking_price(booking)


class BookingValidationServiceTests(TestCase):
    """Test suite for BookingValidationService"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test fixtures"""
        cls.user = User.objects.create_user(
            phone_number="9841234567",
            password="testpass123",
            is_driver=True,
            is_owner=True
        )
        
        cls.spot = ParkingSpot.objects.create(
            owner=cls.user,
            location=Point(85.3240, 27.7172),
            address="Thamel, Kathmandu",
            capacity_two_wheeler=5,
            capacity_four_wheeler=3,
            price_per_hour_two_wheeler=Decimal("50.00"),
            price_per_hour_four_wheeler=Decimal("100.00"),
            is_active=True
        )
    
    def test_valid_booking_time(self):
        """Test valid booking time validation"""
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=3)
        
        is_valid, error = BookingValidationService.validate_booking_time(start, end)
        
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
    
    def test_invalid_end_before_start(self):
        """Test validation fails when end time is before start time"""
        start = timezone.now() + timedelta(hours=5)
        end = timezone.now() + timedelta(hours=2)
        
        is_valid, error = BookingValidationService.validate_booking_time(start, end)
        
        self.assertFalse(is_valid)
        self.assertIn("End time must be after start time", error)
    
    def test_invalid_start_in_past(self):
        """Test validation fails for past start time"""
        start = timezone.now() - timedelta(hours=1)
        end = timezone.now() + timedelta(hours=2)
        
        is_valid, error = BookingValidationService.validate_booking_time(start, end)
        
        self.assertFalse(is_valid)
        self.assertIn("Start time cannot be in the past", error)
    
    def test_invalid_duration_less_than_one_hour(self):
        """Test validation fails for less than 1 hour duration"""
        start = timezone.now() + timedelta(hours=1)
        end = start + timedelta(minutes=30)  # Only 30 minutes
        
        is_valid, error = BookingValidationService.validate_booking_time(start, end)
        
        self.assertFalse(is_valid)
        self.assertIn("Minimum booking duration is 1 hour", error)
    
    def test_spot_availability_empty_spot(self):
        """Test availability check for empty spot"""
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=3)
        
        is_available, error = BookingValidationService.check_spot_availability(
            self.spot, start, end, "two_wheeler"
        )
        
        self.assertTrue(is_available)
        self.assertEqual(error, "")
    
    def test_spot_availability_at_capacity(self):
        """Test availability check when spot is at full capacity"""
        # Create 5 overlapping bookings (matching capacity)
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=3)
        
        for i in range(5):
            Booking.objects.create(
                driver=self.user,
                spot=self.spot,
                vehicle_type="two_wheeler",
                start_time=start,
                end_time=end,
                total_price=Decimal("150.00"),
                status=Booking.ACTIVE
            )
        
        # Try to book when at capacity
        is_available, error = BookingValidationService.check_spot_availability(
            self.spot, start, end, "two_wheeler"
        )
        
        self.assertFalse(is_available)
        self.assertIn("No available two-wheeler spots", error)
