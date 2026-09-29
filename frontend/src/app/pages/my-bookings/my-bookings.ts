import { Component, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { BookingService, Booking } from '../../core/booking.service';

function todayIso(): string {
  const d = new Date();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${m}-${day}`;
}

@Component({
  selector: 'app-my-bookings',
  imports: [RouterLink],
  templateUrl: './my-bookings.html',
  styleUrl: './my-bookings.css',
})
export class MyBookings {
  private bookings = inject(BookingService);

  all = signal<Booking[]>([]);
  loading = signal(true);
  cancellingId = signal<number | null>(null);
  message = signal<{ ok: boolean; text: string } | null>(null);

  upcoming = computed(() =>
    this.all()
      .filter((b) => b.status === 'CONFIRMED' && !this.isPast(b))
      .sort((a, b) => (a.date + a.slot_start).localeCompare(b.date + b.slot_start))
  );

  past = computed(() =>
    this.all()
      .filter((b) => b.status !== 'CONFIRMED' || this.isPast(b))
      .sort((a, b) => (b.date + b.slot_start).localeCompare(a.date + a.slot_start))
  );

  constructor() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.bookings.mine().subscribe({
      next: (list) => {
        this.all.set(list);
        this.loading.set(false);
      },
      error: () => {
        this.message.set({ ok: false, text: 'Could not load your bookings. Is the backend running?' });
        this.loading.set(false);
      },
    });
  }

  isPast(b: Booking): boolean {
    const now = new Date();
    const todayStr = todayIso();
    if (b.date < todayStr) return true;
    if (b.date > todayStr) return false;
    return b.slot_start <= now.toTimeString().slice(0, 8);
  }

  dateLabel(dateIso: string): string {
    return new Date(dateIso + 'T00:00:00').toLocaleDateString('en-GB', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
    });
  }

  hourLabel(t: string): string {
    const h = +t.slice(0, 2);
    const m = t.slice(3, 5);
    return `${h % 12 || 12}${m === '00' ? '' : ':' + m} ${h < 12 ? 'AM' : 'PM'}`;
  }

  cancel(b: Booking) {
    this.message.set(null);
    this.cancellingId.set(b.id);
    this.bookings.cancel(b.id).subscribe({
      next: () => {
        this.message.set({ ok: true, text: 'Booking cancelled.' });
        this.cancellingId.set(null);
        this.load();
      },
      error: (err) => {
        const detail = err.error?.detail;
        this.message.set({ ok: false, text: typeof detail === 'string' ? detail : 'Could not cancel this booking.' });
        this.cancellingId.set(null);
      },
    });
  }
}