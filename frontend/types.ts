
export interface ParkingSpot {
  id: string;
  name: string;
  location: string;
  distance: string;
  rating: number;
  reviewsCount: number;
  pricePerHour: number;
  imageUrl: string;
  type: 'Scooter' | 'Motorbike' | 'Both';
  amenities: string[];
  host: {
    name: string;
    avatar: string;
    responseTime: string;
    verified: boolean;
  };
  capacity: number;
  availableSpots: number;
  description: string;
  coordinates: {
    lat: number;
    lng: number;
  };
}

export interface Booking {
  id: string;
  spotId: string;
  spotName: string;
  date: string;
  startTime: string;
  duration: number;
  cost: number;
  status: 'Completed' | 'Pending' | 'Cancelled';
  plateNumber: string;
  location: string;
  qrCode: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  plateNumber: string;
}

export enum PaymentMethod {
  ESEWA = 'esewa',
  KHALTI = 'khalti',
  CARD = 'card'
}

export enum UserRole {
  Driver = 'driver',
  Partner = 'partner',
}

export interface SignUpFormData {
  phoneNumber: string;
  fullName: string;
  password: string;
  confirmPassword: string;
  isOwner: boolean;
  isDriver: boolean;
  profilePicture: File | null;
}
