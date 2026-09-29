import { Component, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';
import { BookingService, SlotAvailability } from '../../core/booking.service';
import { SeatTable } from '../../shared/seat-table/seat-table';
import { seatTone } from '../../shared/seat-tone';
import { RouterLink } from '@angular/router';


const DAYS_SHOWN = 7;

function iso(d: Date): string {
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

@Component({
  selector: 'app-customer-home',
  imports: [SeatTable, RouterLink],
  templateUrl: './customer-home.html',
  styleUrl: './customer-home.css',
})
export class CustomerHome {
  private auth = inject(AuthService);
  private router = inject(Router);
  private bookings = inject(BookingService);

  days = Array.from({ length: DAYS_SHOWN }, (_, i) => {
    const d = new Date();
    d.setDate(d.getDate() + i);
    return { iso: iso(d), label: d.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric' }) };
  });

  selectedDay = signal(this.days[0].iso);
  party = signal(2);
  slots = signal<SlotAvailability[]>([]);
  loading = signal(true);
  busy = signal(false);
  message = signal<{ ok: boolean; text: string } | null>(null);
  maxParty = computed(() => this.slots()[0]?.total_seats ?? 10);

  constructor() {
    this.load(true);
  }

  load(showSpinner: boolean) {
    if (showSpinner) this.loading.set(true);
    this.bookings.dayAvailability(this.selectedDay()).subscribe({
      next: (s) => {
        this.slots.set(s);
        this.loading.set(false);
      },
      error: () => {
        this.message.set({ ok: false, text: 'Could not load times. Is the backend running?' });
        this.loading.set(false);
      },
    });
  }

  pickDay(day: string) {
    this.selectedDay.set(day);
    this.message.set(null);
    this.load(true);
  }

  changeParty(step: number) {
    this.party.set(Math.min(this.maxParty(), Math.max(1, this.party() + step)));
  }

  isPast(s: SlotAvailability): boolean {
    return s.date === iso(new Date()) && s.slot_start <= new Date().toTimeString().slice(0, 8);
  }

  canBook(s: SlotAvailability): boolean {
    return !this.isPast(s) && s.available_seats >= this.party();
  }

  tone(s: SlotAvailability): string {
    return seatTone(s.available_seats, s.total_seats);
  }

  hourLabel(t: string): string {
    const h = +t.slice(0, 2);
    const m = t.slice(3, 5);
    return `${h % 12 || 12}${m === '00' ? '' : ':' + m} ${h < 12 ? 'AM' : 'PM'}`;
  }

  book(s: SlotAvailability) {
    this.message.set(null);
    this.busy.set(true);
    this.bookings.create(s.date, s.slot_start, this.party()).subscribe({
      next: () => {
        this.message.set({ ok: true, text: `Booked a table for ${this.party()} at ${this.hourLabel(s.slot_start)}.` });
        this.busy.set(false);
        this.load(false);
      },
      error: (err) => {
        const detail = err.error?.detail;
        this.message.set({ ok: false, text: typeof detail === 'string' ? detail : 'Could not book this slot.' });
        this.busy.set(false);
        this.load(false);
      },
    });
  }

  signOut() {
    this.auth.logout();
    this.router.navigate(['/']);
  }
}