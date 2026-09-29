import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

export const roleGuard = (role: 'customer' | 'restaurant'): CanActivateFn => () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.role() === role ? true : router.createUrlTree(['/']);
};