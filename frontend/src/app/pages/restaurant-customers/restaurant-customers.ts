import { Component, inject, signal } from '@angular/core';
import { DashboardService } from '../../core/dashboard.service';

@Component({
  selector: 'app-restaurant-customers',
  templateUrl: './restaurant-customers.html',
  styleUrl: './restaurant-customers.css',
})
export class RestaurantCustomers {
  private svc = inject(DashboardService);
  list = signal<any[]>([]);
  loading = signal(true);

  constructor() {
    this.svc.customers().subscribe({
      next: (c) => { this.list.set(c); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }
}