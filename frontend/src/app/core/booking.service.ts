import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from './auth.service';

export interface SlotAvailability {
  date: string;
  slot_start: string;
  total_seats: number;
  booked_seats: number;
  blocked_seats: number;
  available_seats: number;
}

export interface Booking {
  id: number;
  date: string;
  slot_start: string;
  party_size: number;
  status: string;
}

@Injectable({ providedIn: 'root' })
export class BookingService {
  private http = inject(HttpClient);

  dayAvailability(date: string) {
    return this.http.get<SlotAvailability[]>(`${API_URL}/availability/day`, { params: { date } });
  }
  create(date: string, slot_start: string, party_size: number) {
    return this.http.post<Booking>(`${API_URL}/bookings`, { date, slot_start, party_size });
  }
  mine() {
    return this.http.get<Booking[]>(`${API_URL}/bookings/me`);
  }
  cancel(id: number) {
    return this.http.delete(`${API_URL}/bookings/${id}`);
  }
  allBookings() {
    return this.http.get<Booking[]>(`${API_URL}/bookings`);
  }
  restaurantCancel(id: number) {
    return this.http.delete(`${API_URL}/bookings/${id}/restaurant-cancel`);
  }
  blockSeats(date: string, slot_start: string, seats_blocked: number, reason: string) {
    return this.http.post(`${API_URL}/seat-blocks`, { date, slot_start, seats_blocked, reason });
  }


}