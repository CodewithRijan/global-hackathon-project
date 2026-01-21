
import { ParkingSpot } from '../types';

export const PARKING_SPOTS: ParkingSpot[] = [
  {
    id: '1',
    name: 'Baneshwor Heights',
    location: 'Baneshwor, Kathmandu',
    distance: '200m away',
    rating: 4.8,
    reviewsCount: 120,
    pricePerHour: 20,
    imageUrl: 'https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&q=80&w=800',
    type: 'Both',
    amenities: ['CCTV Camera', 'Covered', 'Guarded', '24/7 Access'],
    host: {
      name: 'Sanjeev K.',
      avatar: 'https://picsum.photos/seed/sanjeev/200/200',
      responseTime: '5 mins',
      verified: true
    },
    capacity: 20,
    availableSpots: 4,
    description: 'Secure indoor parking space located just 5 minutes walk from Baneshwor Chowk. The area is well-lit and monitored by CCTV 24/7. Ideal for daily commuters or overnight parking. Entry via the blue gate next to the bakery.',
    coordinates: { lat: 27.6934, lng: 85.3331 }
  },
  {
    id: '2',
    name: 'Thamel Tourist Hub',
    location: 'Thamel, Kathmandu',
    distance: '0.5km away',
    rating: 4.5,
    reviewsCount: 85,
    pricePerHour: 15,
    imageUrl: 'https://images.unsplash.com/photo-1573348722427-f1d6819fdf98?auto=format&fit=crop&q=80&w=800',
    type: 'Scooter',
    amenities: ['CCTV Camera', 'Centrally Located'],
    host: {
      name: 'Pema T.',
      avatar: 'https://picsum.photos/seed/pema/200/200',
      responseTime: '10 mins',
      verified: true
    },
    capacity: 15,
    availableSpots: 2,
    description: 'Convenient spot for shoppers and tourists in the heart of Thamel. Very tight security but easy in and out for scooters.',
    coordinates: { lat: 27.7150, lng: 85.3123 }
  },
  {
    id: '3',
    name: 'Durbar Marg Basement',
    location: 'Durbar Marg, Kathmandu',
    distance: '1.2km away',
    rating: 4.2,
    reviewsCount: 210,
    pricePerHour: 25,
    imageUrl: 'https://images.unsplash.com/photo-1590674899484-d5640e854abe?auto=format&fit=crop&q=80&w=800',
    type: 'Both',
    amenities: ['CCTV Camera', 'Security Guard', 'Underground'],
    host: {
      name: 'Anup S.',
      avatar: 'https://picsum.photos/seed/anup/200/200',
      responseTime: '2 mins',
      verified: true
    },
    capacity: 50,
    availableSpots: 12,
    description: 'High-end parking facility in the most premium shopping district. Safe for expensive bikes.',
    coordinates: { lat: 27.7101, lng: 85.3164 }
  }
];
