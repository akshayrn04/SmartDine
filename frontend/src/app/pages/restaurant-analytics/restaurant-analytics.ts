import { Component, inject, signal } from '@angular/core';
import { DashboardService, OccupancyDay } from '../../core/dashboard.service';
import { CampaignService } from '../../core/campaign.service';
import { occupancyTone } from '../../shared/seat-tone';

@Component({
  selector: 'app-restaurant-analytics',
  templateUrl: './restaurant-analytics.html',
  styleUrl: './restaurant-analytics.css',
})
export class RestaurantAnalytics {
  private dash = inject(DashboardService);
  private camp = inject(CampaignService);

  occ = signal<OccupancyDay[]>([]);
  cancelStats = signal<{ total_bookings: number; cancelled: number; cancellation_rate_percent: number } | null>(null);
  campaignResults = signal<any[]>([]);
  loading = signal(true);

  constructor() {
    this.dash.occupancy(7).subscribe({ next: (o) => this.occ.set(o) });
    this.dash.cancellationRate().subscribe({ next: (c) => this.cancelStats.set(c) });
    this.camp.results().subscribe({
      next: (r) => { this.campaignResults.set(r); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  tone(booked: number, total: number): string {
    return occupancyTone(booked, total);
  }
  barHeight(booked: number, total: number): number {
    return total ? Math.round((booked / total) * 100) : 0;
  }
  dayLabel(d: string): string {
    return new Date(d + 'T00:00:00').toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric' });
  }
}