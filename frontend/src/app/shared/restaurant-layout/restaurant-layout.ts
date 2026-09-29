import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-restaurant-layout',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './restaurant-layout.html',
  styleUrl: './restaurant-layout.css',
})
export class RestaurantLayout {
  private auth = inject(AuthService);
  private router = inject(Router);

  links = [
    { path: '/restaurant', label: 'Today', exact: true },
    { path: '/restaurant/bookings', label: 'Bookings', exact: false },
    { path: '/restaurant/customers', label: 'Customers', exact: false },
    { path: '/restaurant/insights', label: 'AI insights', exact: false },
    { path: '/restaurant/campaigns', label: 'Campaigns', exact: false },
    { path: '/restaurant/analytics', label: 'Analytics', exact: false },
  ];

  signOut() {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}