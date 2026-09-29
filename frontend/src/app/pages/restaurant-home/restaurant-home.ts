import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-restaurant-home',
  templateUrl: './restaurant-home.html',
  styleUrl: './restaurant-home.css',
})
export class RestaurantHome {
  private auth = inject(AuthService);
  private router = inject(Router);

  signOut() {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}