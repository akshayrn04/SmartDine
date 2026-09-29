import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-register',
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class Register {
  private auth = inject(AuthService);
  private router = inject(Router);

  name = '';
  email = '';
  phone = '';
  password = '';
  optedIn = false;
  error = signal('');
  loading = signal(false);

  submit() {
    this.error.set('');
    this.loading.set(true);
    this.auth
      .register({
        name: this.name,
        email: this.email,
        phone: this.phone || null,
        password: this.password,
        opted_in: this.optedIn,
      })
      .subscribe({
        next: () => this.router.navigate(['/customer']),
        error: (err) => {
          const detail = err.error?.detail;
          this.error.set(typeof detail === 'string' ? detail : 'Could not create the account. Check your details.');
          this.loading.set(false);
        },
      });
  }
}