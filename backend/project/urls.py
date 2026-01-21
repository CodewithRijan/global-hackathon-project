"""
GalliPark URL Configuration

Main URL routing using Django REST Framework's router for automatic endpoint generation.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    UserViewSet, ParkingSpotViewSet, UtsavEventViewSet,
    BookingViewSet, ReviewViewSet
)

# Create DRF router
router = DefaultRouter()

# Register viewsets with router
router.register(r'users', UserViewSet, basename='user')
router.register(r'spots', ParkingSpotViewSet, basename='parking-spot')
router.register(r'events', UtsavEventViewSet, basename='utsav-event')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/', include(router.urls)),
    
    # DRF Authentication
    path('api-auth/', include('rest_framework.urls')),
]
