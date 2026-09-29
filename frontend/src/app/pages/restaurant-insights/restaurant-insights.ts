import { Component, inject, signal } from '@angular/core';
import { CampaignService, Prediction } from '../../core/campaign.service';
import { seatTone } from '../../shared/seat-tone';

@Component({
  selector: 'app-restaurant-insights',
  templateUrl: './restaurant-insights.html',
  styleUrl: './restaurant-insights.css',
})
export class RestaurantInsights {
  private svc = inject(CampaignService);
  rows = signal<Prediction[]>([]);
  loading = signal(true);

  constructor() {
    this.svc.predictions(7).subscribe({
      next: (r) => { this.rows.set(r); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  tone(occ: number): string {
    return seatTone(1 - occ, 1);
  }
  hourLabel(t: string): string {
    const h = +t.slice(0, 2);
    return `${h % 12 || 12} ${h < 12 ? 'AM' : 'PM'}`;
  }
}