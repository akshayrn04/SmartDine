import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs';

export const API_URL = 'https://smartdine-api.onrender.com/api';

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
}

export interface RegisterPayload {
  name: string;
  email: string;
  phone: string | null;
  password: string;
  opted_in: boolean;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);

  token = signal<string | null>(localStorage.getItem('token'));
  role = signal<string | null>(localStorage.getItem('role'));

  login(email: string, password: string) {
    return this.http
      .post<TokenResponse>(`${API_URL}/auth/login`, { email, password })
      .pipe(tap((res) => this.save(res)));
  }

  register(payload: RegisterPayload) {
    return this.http
      .post<TokenResponse>(`${API_URL}/auth/register`, payload)
      .pipe(tap((res) => this.save(res)));
  }

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    this.token.set(null);
    this.role.set(null);
  }

  private save(res: TokenResponse) {
    localStorage.setItem('token', res.access_token);
    localStorage.setItem('role', res.role);
    this.token.set(res.access_token);
    this.role.set(res.role);
  }
}