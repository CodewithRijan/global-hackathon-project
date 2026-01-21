"""
GalliPark Backend Models

Core data models for the parking marketplace application including:
- Custom User model with owner/driver roles ( CustomUserManager and User)
- ParkingSpot model with geolocation
- UtsavEvent model for temporary event-based parking
- Booking model for managing parking transactions
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


# ========================
# User Management
# ========================

class CustomUserManager(BaseUserManager):
    """
    Custom user manager for phone-based authentication.
    Handles creation of regular users and superusers.
    """

    def create_user(self, phone_number, password=None, **extra_fields):
        """
        Create and save a regular user with phone number as unique identifier.
        """
        if not phone_number:
            raise ValueError("Phone number is required")
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """
        Create and save a superuser with phone number as unique identifier.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model for GalliPark application.
    
    Attributes:
        phone_number: Primary identifier for the user 
        is_owner: Boolean flag indicating if user is a parking space owner
        is_driver: Boolean flag indicating if user is a driver seeking parking
        full_name: User's full name
        profile_picture: User's profile picture
        rating: Average rating from other users (0-5)
        total_bookings: Total number of bookings made/hosted
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Primary identifier for authentication"
    )
    is_owner = models.BooleanField(
        default=False,
        help_text="User can list and manage parking spots"
    )
    is_driver = models.BooleanField(
        default=False,
        help_text="User can book parking spots"
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("5"))]
    )
    total_bookings = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["is_owner"]),
            models.Index(fields=["is_driver"]),
        ]

    def __str__(self):
        return f"{self.full_name or 'User'} ({self.phone_number})"

    def get_role(self):
        """
        Returns user's role(s) as a string.
        """
        roles = []
        if self.is_owner:
            roles.append("Owner")
        if self.is_driver:
            roles.append("Driver")
        return ", ".join(roles) if roles else "No Role"


# ========================
# Parking Spot Management
# ========================

class ParkingSpot(models.Model):
    """
    Represents a parking spot/area offered by a host (owner).
    
    Attributes:
        owner: Foreign key to the User who owns this spot
        location: Point field with geolocation (requires PostGIS)
        address: Human-readable address for the parking spot
        city: City where the parking spot is located
        description: Detailed description of the parking spot
        capacity_two_wheeler: Number of two-wheeler spots available
        capacity_four_wheeler: Number of four-wheeler spots available (optional)
        price_per_hour_two_wheeler: Price per hour for two-wheelers
        price_per_hour_four_wheeler: Price per hour for four-wheelers (optional)
        is_active: Whether the spot is currently available for booking
        land_pictures: Multiple pictures of the parking area
        amenities: JSON field for additional amenities (covered, lit, etc.)
        created_at: Creation timestamp
        updated_at: Last modification timestamp
    """
    
    AMENITY_CHOICES = [
        ("covered", "Covered Parking"),
        ("lit", "Well Lit"),
        ("secure", "Security Guard"),
        ("cctv", "CCTV Surveillance"),
        ("electric", "EV Charging"),
        ("toilet", "Toilet Facility"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="parking_spots",
        limit_choices_to={"is_owner": True}
    )
    
    # Geolocation
    latitude = models.FloatField(
        help_text="Latitude coordinate of the parking spot"
    )
    longitude = models.FloatField(
        help_text="Longitude coordinate of the parking spot"
    )
    address = models.CharField(
        max_length=500,
        help_text="Detailed address of the parking spot"
    )
    city = models.CharField(
        max_length=100,
        default="Kathmandu",
        help_text="City where parking spot is located"
    )
    
    # Description and Images
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the parking area"
    )
    
    # Capacity Management
    capacity_two_wheeler = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Maximum number of two-wheelers"
    )
    capacity_four_wheeler = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Maximum number of four-wheelers"
    )
    
    # Pricing (in NPR - Nepalese Rupees)
    price_per_hour_two_wheeler = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Price per hour for two-wheelers in NPR"
    )
    price_per_hour_four_wheeler = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Price per hour for four-wheelers in NPR"
    )
    
    # Status and Amenities
    is_active = models.BooleanField(
        default=True,
        help_text="Whether spot is available for booking"
    )
    amenities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of available amenities"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return f"{self.address} - {self.owner.full_name}"

    def get_available_two_wheeler_capacity(self):
        """
        Calculate available capacity for two-wheelers
        by subtracting active bookings.
        """
        active_bookings = self.bookings.filter(
            status__in=[Booking.PENDING, Booking.ACTIVE]
        ).count()
        return max(0, self.capacity_two_wheeler - active_bookings)

    def get_available_four_wheeler_capacity(self):
        """
        Calculate available capacity for four-wheelers
        by subtracting active bookings.
        """
        active_bookings = self.bookings.filter(
            status__in=[Booking.PENDING, Booking.ACTIVE]
        ).count()
        return max(0, self.capacity_four_wheeler - active_bookings)


class ParkingSpotImage(models.Model):
    """
    Stores multiple images for a parking spot.
    
    Attributes:
        spot: Foreign key to ParkingSpot
        image: Image file
        uploaded_at: Upload timestamp
    """
    
    spot = models.ForeignKey(
        ParkingSpot,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(
        upload_to="parking_spots/%Y/%m/%d/",
        help_text="Picture of the parking area"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Image for {self.spot.address}"


# ========================
# Event-based Parking
# ========================

class UtsavEvent(models.Model):
    """
    Represents a temporary event/festival (Utsav) where a parking spot
    becomes available for high-capacity parking.
    
    Attributes:
        spot: Foreign key to ParkingSpot
        event_name: Name of the event/festival
        event_date: Date of the event
        start_time: Event start time
        end_time: Event end time
        temporary_capacity_two_wheeler: Additional capacity for two-wheelers
        temporary_capacity_four_wheeler: Additional capacity for four-wheelers
        temporary_price_two_wheeler: Special price during event for two-wheelers
        temporary_price_four_wheeler: Special price during event for four-wheelers
        description: Event details
        is_active: Whether event is still active for bookings
        created_at: Creation timestamp
    """
    
    spot = models.ForeignKey(
        ParkingSpot,
        on_delete=models.CASCADE,
        related_name="utsav_events",
        help_text="Parking spot hosting the event"
    )
    
    event_name = models.CharField(
        max_length=255,
        help_text="Name of the event/festival (e.g., 'Gai Jatra 2026')"
    )
    event_date = models.DateField(
        help_text="Date of the event"
    )
    start_time = models.TimeField(
        help_text="Event start time"
    )
    end_time = models.TimeField(
        help_text="Event end time"
    )
    
    # Capacity for the event
    temporary_capacity_two_wheeler = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total two-wheeler capacity during event"
    )
    temporary_capacity_four_wheeler = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total four-wheeler capacity during event"
    )
    
    # Event-specific pricing
    temporary_price_two_wheeler = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Special price per hour for two-wheelers during event"
    )
    temporary_price_four_wheeler = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Special price per hour for four-wheelers during event"
    )
    
    # Details
    description = models.TextField(
        blank=True,
        help_text="Additional event details"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether event is accepting bookings"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date"]
        indexes = [
            models.Index(fields=["spot"]),
            models.Index(fields=["event_date"]),
            models.Index(fields=["is_active"]),
        ]
        unique_together = [["spot", "event_date"]]

    def __str__(self):
        return f"{self.event_name} at {self.spot.address} on {self.event_date}"

    def is_event_ongoing(self):
        """
        Check if the event is currently happening.
        """
        today = timezone.now().date()
        now = timezone.now().time()
        
        if today == self.event_date:
            return self.start_time <= now <= self.end_time
        return False

    def get_available_two_wheeler_capacity(self):
        """
        Calculate available capacity during event.
        """
        active_bookings = self.bookings.filter(
            status__in=[Booking.PENDING, Booking.ACTIVE]
        ).count()
        return max(0, self.temporary_capacity_two_wheeler - active_bookings)

    def get_available_four_wheeler_capacity(self):
        """
        Calculate available capacity during event.
        """
        active_bookings = self.bookings.filter(
            status__in=[Booking.PENDING, Booking.ACTIVE]
        ).count()
        return max(0, self.temporary_capacity_four_wheeler - active_bookings)


# ========================
# Booking Management
# ========================

class Booking(models.Model):
    """
    Represents a booking of a parking spot by a driver.
    
    Attributes:
        driver: Foreign key to User (driver)
        spot: Foreign key to ParkingSpot
        utsav_event: Optional foreign key to UtsavEvent (if booking is for event)
        vehicle_type: Type of vehicle ('two_wheeler' or 'four_wheeler')
        start_time: When parking starts
        end_time: When parking ends
        total_price: Total calculated price (set by backend)
        status: Current booking status
        notes: Additional notes from driver or owner
        created_at: Booking creation timestamp
        updated_at: Last modification timestamp
    """
    
    VEHICLE_TYPE_CHOICES = [
        ("two_wheeler", "Two Wheeler"),
        ("four_wheeler", "Four Wheeler"),
    ]
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
        limit_choices_to={"is_driver": True}
    )
    spot = models.ForeignKey(
        ParkingSpot,
        on_delete=models.CASCADE,
        related_name="bookings"
    )
    utsav_event = models.ForeignKey(
        UtsavEvent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
        help_text="Link to event if booking is for temporary event parking"
    )
    
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPE_CHOICES,
        help_text="Type of vehicle being parked"
    )
    
    # Booking Time Details
    start_time = models.DateTimeField(
        help_text="When the parking period starts"
    )
    end_time = models.DateTimeField(
        help_text="When the parking period ends"
    )
    
    # Pricing (calculated by backend to prevent manipulation)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Total price calculated by backend (NPR)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        help_text="Current status of the booking"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes from driver or owner"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["driver"]),
            models.Index(fields=["spot"]),
            models.Index(fields=["status"]),
            models.Index(fields=["start_time"]),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.driver.full_name} at {self.spot.address}"

    def check_event_overlap(self):
        """
        Check if the booking time overlaps with any UtsavEvent for the parking spot.
        
        Returns:
            UtsavEvent: The overlapping event if found, None otherwise
        """
        from django.db.models import Q
        
        # Get all active events for this spot
        events = self.spot.utsav_events.filter(
            is_active=True,
            event_date=self.start_time.date()
        )
        
        for event in events:
            # Convert event times to datetime for comparison
            event_start = timezone.make_aware(
                timezone.datetime.combine(event.event_date, event.start_time)
            )
            event_end = timezone.make_aware(
                timezone.datetime.combine(event.event_date, event.end_time)
            )
            
            # Check if booking overlaps with event
            if not (self.end_time <= event_start or self.start_time >= event_end):
                return event
        
        return None

    def calculate_total_price(self):
        """
        Calculate the total price for the booking based on duration and vehicle type.
        Applies a 20% 'Event Surcharge' if booking overlaps with an UtsavEvent.
        
        Backend-side calculation ensures prices cannot be manipulated by frontend.
        
        Returns:
            Decimal: Total price in NPR
        """
        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        
        # Determine pricing based on event or regular spot
        if self.utsav_event:
            if self.vehicle_type == "two_wheeler":
                hourly_rate = self.utsav_event.temporary_price_two_wheeler
            else:
                hourly_rate = self.utsav_event.temporary_price_four_wheeler
        else:
            if self.vehicle_type == "two_wheeler":
                hourly_rate = self.spot.price_per_hour_two_wheeler
            else:
                hourly_rate = self.spot.price_per_hour_four_wheeler
        
        # Calculate base price
        base_price = Decimal(duration_hours) * hourly_rate
        
        # Check for event overlap and apply 20% surcharge
        overlapping_event = self.check_event_overlap()
        if overlapping_event:
            event_surcharge = base_price * Decimal("0.20")  # 20% surcharge
            total_price = base_price + event_surcharge
            return total_price
        
        return base_price

    def is_valid_booking_time(self):
        """
        Validate that booking times are logical.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if self.end_time <= self.start_time:
            return False, "End time must be after start time"
        
        if self.start_time < timezone.now():
            return False, "Start time cannot be in the past"
        
        return True, ""

    def cancel(self):
        """
        Cancel the booking and update status.
        """
        if self.status != self.CANCELLED:
            self.status = self.CANCELLED
            self.save()

    def activate(self):
        """
        Activate the booking (mark as active).
        """
        if self.status == self.PENDING:
            self.status = self.ACTIVE
            self.save()

    def complete(self):
        """
        Mark the booking as completed.
        """
        if self.status == self.ACTIVE:
            self.status = self.COMPLETED
            self.save()


# ========================
# Review and Rating
# ========================

class Review(models.Model):
    """
    Represents a review for a parking spot or user.
    
    Attributes:
        booking: Foreign key to completed booking
        reviewer: User who is writing the review
        rating: Rating from 1-5
        comment: Review text
        created_at: When review was posted
    """
    
    RATING_CHOICES = [
        (1, "Poor"),
        (2, "Fair"),
        (3, "Good"),
        (4, "Very Good"),
        (5, "Excellent"),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="review"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(
        blank=True,
        help_text="Detailed feedback about the parking experience"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["booking"]),
            models.Index(fields=["reviewer"]),
        ]

    def __str__(self):
        return f"Review for {self.booking} - {self.rating} stars"
