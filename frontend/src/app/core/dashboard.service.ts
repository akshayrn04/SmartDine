import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from './auth.service';
import { SlotAvailability } from './booking.service';

export interface DashboardData {
  date: string;
  total_bookings_today: number;
  total_seats_booked_today: number;
  cancellations_today: number;
  total_seats: number;
  slots: SlotAvailability[];
}

export interface OccupancyDay {
  date: string;
  seats_booked: number;
  total_seats: number;
}

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private http = inject(HttpClient);

  dashboard() {
    return this.http.get<DashboardData>(`${API_URL}/analytics/dashboard`);
  }
  occupancy(days = 7) {
    return this.http.get<OccupancyDay[]>(`${API_URL}/analytics/occupancy`, { params: { days } });
  }

  customers() {
    return this.http.get<any[]>(`${API_URL}/customers`);
  }  

  cancellationRate() {
    return this.http.get<{ total_bookings: number; cancelled: number; cancellation_rate_percent: number }>(
      `${API_URL}/analytics/cancellation-rate`
    );
  }

}