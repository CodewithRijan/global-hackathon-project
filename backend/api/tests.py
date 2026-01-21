"""
GalliPark Booking Pricing Unit Tests

Comprehensive test suite for booking price calculation with event surcharge logic.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta, datetime, time
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

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
            latitude=27.7172,
            longitude=85.3240,
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
            utsav_event=self.event,  # Explicitly link to event
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
            utsav_event=self.event,  # Explicitly link to event
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
            latitude=27.7172,
            longitude=85.3240,
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


# ========================
# Authentication & JWT Tests
# ========================

class UserAuthenticationTests(APITestCase):
    """Test suite for user authentication and JWT token management"""
    
    def setUp(self):
        """Set up test client and test users"""
        self.client = APIClient()
        self.register_url = '/api/users/'
        self.me_url = '/api/users/me/'
        
        # Create test users
        self.user_data = {
            'phone_number': '9841234567',
            'password': 'securepass123',
            'password_confirm': 'securepass123',
            'full_name': 'Test Driver',
            'is_driver': True,
        }
        
        self.owner_data = {
            'phone_number': '9849876543',
            'password': 'ownerpass123',
            'password_confirm': 'ownerpass123',
            'full_name': 'Test Owner',
            'is_owner': True,
        }
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['phone_number'], self.user_data['phone_number'])
        self.assertEqual(response.data['full_name'], self.user_data['full_name'])
        self.assertTrue(response.data['is_driver'])
        
        # Verify user was created in database
        user = User.objects.get(phone_number=self.user_data['phone_number'])
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_user_registration_password_mismatch(self):
        """Test registration fails when passwords don't match"""
        invalid_data = {
            **self.user_data,
            'password_confirm': 'differentpass123'
        }
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data or str(response.data).lower())
    
    def test_user_registration_short_password(self):
        """Test registration fails with password less than 8 characters"""
        invalid_data = {
            **self.user_data,
            'password': 'short',
            'password_confirm': 'short'
        }
        response = self.client.post(self.register_url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_duplicate_phone(self):
        """Test registration fails with duplicate phone number"""
        # Create first user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Try to create another with same phone
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)
    
    def test_token_creation_on_user_registration(self):
        """Test that authentication token is created when user registers"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify token was created
        user = User.objects.get(phone_number=self.user_data['phone_number'])
        token = Token.objects.get(user=user)
        self.assertIsNotNone(token.key)
    
    def test_token_authentication_with_valid_token(self):
        """Test that requests with valid token are authenticated"""
        # Register user
        self.client.post(self.register_url, self.user_data, format='json')
        user = User.objects.get(phone_number=self.user_data['phone_number'])
        token = Token.objects.get(user=user)
        
        # Make authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.user_data['phone_number'])
    
    def test_request_without_token_fails(self):
        """Test that requests without token are rejected"""
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('credentials', str(response.data).lower() or 'not provided' in str(response.data).lower())
    
    def test_request_with_invalid_token_fails(self):
        """Test that requests with invalid token are rejected"""
        invalid_token = 'invalid_token_12345'
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {invalid_token}')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_request_with_malformed_auth_header_fails(self):
        """Test that malformed Authorization header is rejected"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_format')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_request_with_expired_token_fails(self):
        """Test that expired tokens are rejected"""
        # Register user
        self.client.post(self.register_url, self.user_data, format='json')
        user = User.objects.get(phone_number=self.user_data['phone_number'])
        
        # Create a new token and manually expire it
        old_token = Token.objects.get(user=user)
        old_token.delete()
        
        # Try request with deleted token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {old_token.key}')
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_different_users_cannot_access_each_other_data(self):
        """Test that users can only access their own authenticated data"""
        # Create two users
        self.client.post(self.register_url, self.user_data, format='json')
        self.client.post(self.register_url, self.owner_data, format='json')
        
        # Get tokens for both
        user1 = User.objects.get(phone_number=self.user_data['phone_number'])
        user2 = User.objects.get(phone_number=self.owner_data['phone_number'])
        token1 = Token.objects.get(user=user1)
        
        # User1 authenticates with their token and requests /me/
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token1.key}')
        response = self.client.get(self.me_url)
        
        # Should get their own data, not user2's
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.user_data['phone_number'])
        self.assertNotEqual(response.data['phone_number'], self.owner_data['phone_number'])


class ProtectedEndpointsTests(APITestCase):
    """Test suite for ensuring protected endpoints require authentication"""
    
    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        
        # Create test user and parking spot
        self.user = User.objects.create_user(
            phone_number='9841234567',
            password='testpass123',
            full_name='Test Owner',
            is_owner=True,
            is_driver=True
        )
        
        self.spot = ParkingSpot.objects.create(
            owner=self.user,
            latitude=27.7172,
            longitude=85.3240,
            address='Thamel, Kathmandu',
            city='Kathmandu',
            capacity_two_wheeler=10,
            capacity_four_wheeler=5,
            price_per_hour_two_wheeler=Decimal("50.00"),
            price_per_hour_four_wheeler=Decimal("100.00"),
            is_active=True
        )
        
        self.token = Token.objects.get(user=self.user)
    
    def test_list_users_requires_authentication(self):
        """Test that GET /users/ requires authentication"""
        # Without token
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_parking_spots_requires_authentication(self):
        """Test that GET /spots/ requires authentication"""
        # Without token
        response = self.client.get('/api/spots/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/spots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_parking_spot_requires_authentication(self):
        """Test that POST /spots/ requires authentication"""
        spot_data = {
            'address': 'New Spot',
            'city': 'Kathmandu',
            'latitude': 27.7,
            'longitude': 85.3,
            'capacity_two_wheeler': 5,
            'capacity_four_wheeler': 2,
            'price_per_hour_two_wheeler': Decimal("50.00"),
            'price_per_hour_four_wheeler': Decimal("100.00"),
        }
        
        # Without token
        response = self.client.post('/api/spots/', spot_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/spots/', spot_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_list_bookings_requires_authentication(self):
        """Test that GET /bookings/ requires authentication"""
        # Without token
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/bookings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_booking_requires_authentication(self):
        """Test that POST /bookings/ requires authentication"""
        booking_data = {
            'spot': self.spot.id,
            'vehicle_type': 'two_wheeler',
            'start_time': (timezone.now() + timedelta(days=1, hours=1)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=1, hours=4)).isoformat(),
        }
        
        # Without token
        response = self.client.post('/api/bookings/', booking_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/bookings/', booking_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST])
    
    def test_list_events_requires_authentication(self):
        """Test that GET /events/ requires authentication"""
        # Without token
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_current_user_requires_authentication(self):
        """Test that GET /users/me/ requires authentication"""
        # Without token
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)
    
    def test_update_current_user_requires_authentication(self):
        """Test that PUT /users/me/ requires authentication"""
        update_data = {'full_name': 'Updated Name'}
        
        # Without token
        response = self.client.put('/api/users/me/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # With valid token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.put('/api/users/me/', update_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])


class TokenSecurityTests(APITestCase):
    """Test suite for token security and best practices"""
    
    def setUp(self):
        """Set up test client and test user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number='9841234567',
            password='testpass123',
            full_name='Test User',
            is_driver=True
        )
        self.token = Token.objects.get(user=self.user)
    
    def test_token_is_unique_per_user(self):
        """Test that each user has a unique token"""
        user2 = User.objects.create_user(
            phone_number='9842345678',
            password='testpass123',
            full_name='Test User 2',
            is_driver=True
        )
        token2 = Token.objects.get(user=user2)
        
        self.assertNotEqual(self.token.key, token2.key)
    
    def test_token_persists_across_requests(self):
        """Test that token remains valid across multiple requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Make multiple requests with same token
        for _ in range(3):
            response = self.client.get('/api/users/me/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_token_format_validation(self):
        """Test that tokens require proper format (Token <key>)"""
        # Wrong format: missing "Token" prefix
        self.client.credentials(HTTP_AUTHORIZATION=self.token.key)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Wrong format: wrong prefix
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Correct format
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_case_sensitive_token(self):
        """Test that tokens are case-sensitive"""
        # Modify case of token
        modified_token = self.token.key[:-5] + self.token.key[-5:].lower() if self.token.key[-5:].isupper() else self.token.key[:-5] + self.token.key[-5:].upper()
        
        if modified_token != self.token.key:  # Only test if case actually changes
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {modified_token}')
            response = self.client.get('/api/users/me/')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_public_user_registration_endpoint(self):
        """Test that user registration endpoint is public (no auth required)"""
        user_data = {
            'phone_number': '9843456789',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'full_name': 'Public User',
            'is_driver': True,
        }
        
        # Should work without token
        response = self.client.post('/api/users/', user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify token was auto-created for new user
        new_user = User.objects.get(phone_number=user_data['phone_number'])
        token = Token.objects.get(user=new_user)
        self.assertIsNotNone(token.key)
