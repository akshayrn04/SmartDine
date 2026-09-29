import { Component, inject, signal } from '@angular/core';
import { DashboardService, DashboardData } from '../../core/dashboard.service';
import { occupancyTone } from '../../shared/seat-tone';

@Component({
  selector: 'app-restaurant-dashboard',
  templateUrl: './restaurant-dashboard.html',
  styleUrl: './restaurant-dashboard.css',
})
export class RestaurantDashboard {
  private svc = inject(DashboardService);

  data = signal<DashboardData | null>(null);
  loading = signal(true);
  error = signal('');

  constructor() {
    this.svc.dashboard().subscribe({
      next: (d) => {
        this.data.set(d);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load the dashboard. Is the backend running?');
        this.loading.set(false);
      },
    });
  }

  tone(booked: number, total: number): string {
    return occupancyTone(booked, total);
  }

  barHeight(booked: number, total: number): number {
    return total ? Math.round((booked / total) * 100) : 0;
  }

  hourLabel(t: string): string {
    const h = +t.slice(0, 2);
    return `${h % 12 || 12}${h < 12 ? 'a' : 'p'}`;
  }
}