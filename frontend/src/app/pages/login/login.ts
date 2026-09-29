

import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-login',
  imports: [FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  private auth = inject(AuthService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  role = this.route.snapshot.queryParamMap.get('role') === 'restaurant' ? 'restaurant' : 'customer';
  email = '';
  password = '';
  error = signal('');
  loading = signal(false);

  submit() {
    this.error.set('');
    this.loading.set(true);
    this.auth.login(this.email, this.password).subscribe({
      next: (res) => {
        if (res.role !== this.role) {
          this.auth.logout();
          this.error.set(
            this.role === 'restaurant'
              ? 'This account is not a restaurant account.'
              : 'This is a restaurant account. Use the restaurant sign in.'
          );
          this.loading.set(false);
          return;
        }
        this.router.navigate([res.role === 'restaurant' ? '/restaurant' : '/customer']);
      },
      error: (err) => {
        this.error.set(
          err.status === 401
            ? 'Email or password is incorrect.'
            : 'Could not reach the server. Is the backend running?'
        );
        this.loading.set(false);
      },
    });
  }
}