import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_URL } from './auth.service';

export interface Prediction {
  date: string;
  slot_start: string;
  predicted_occupancy: number;
  predicted_seats: number;
}

export interface Campaign {
  id: number;
  target_date: string;
  slot_start: string;
  predicted_occupancy: string;
  offer_type: string;
  offer_value: string | null;
  status: string;
}

@Injectable({ providedIn: 'root' })
export class CampaignService {
  private http = inject(HttpClient);

  predictions(days_ahead = 7) {
    return this.http.get<Prediction[]>(`${API_URL}/ai/predictions`, { params: { days_ahead } });
  }
  list() {
    return this.http.get<Campaign[]>(`${API_URL}/campaigns`);
  }
  create(target_date: string, slot_start: string) {
    return this.http.post<Campaign>(`${API_URL}/campaigns`, { target_date, slot_start });
  }
  approve(id: number) {
    return this.http.post<Campaign>(`${API_URL}/campaigns/${id}/approve`, {});
  }
  reject(id: number) {
    return this.http.post<Campaign>(`${API_URL}/campaigns/${id}/reject`, {});
  }
  notifications(id: number) {
    return this.http.get<any[]>(`${API_URL}/campaigns/${id}/notifications`);
  }

  results() {
    return this.http.get<any[]>(`${API_URL}/campaigns`.replace('/campaigns', '/analytics/campaigns'));
  }  
}