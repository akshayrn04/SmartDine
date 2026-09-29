import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BookingService, Booking } from '../../core/booking.service';

@Component({
  selector: 'app-restaurant-bookings',
  imports: [FormsModule],
  templateUrl: './restaurant-bookings.html',
  styleUrl: './restaurant-bookings.css',
})
export class RestaurantBookings {
  private svc = inject(BookingService);

  all = signal<Booking[]>([]);
  loading = signal(true);
  cancellingId = signal<number | null>(null);
  message = signal<{ ok: boolean; text: string } | null>(null);
  filterDate = signal('');
  filterDateModel = '';
  
  blockDate = '';
  blockSlot = '13:00';
  blockSeats = 1;
  blockReason = '';
  blocking = signal(false);
  blockMsg = signal<{ ok: boolean; text: string } | null>(null);

  filtered = computed(() => {
    const d = this.filterDate();
    const list = this.all();
    return (d ? list.filter((b) => b.date === d) : list)
      .slice()
      .sort((a, b) => (b.date + b.slot_start).localeCompare(a.date + a.slot_start));
  });

  constructor() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.svc.allBookings().subscribe({
      next: (list) => { this.all.set(list); this.loading.set(false); },
      error: () => { this.message.set({ ok: false, text: 'Could not load bookings.' }); this.loading.set(false); },
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
    this.svc.restaurantCancel(b.id).subscribe({
      next: () => { this.message.set({ ok: true, text: 'Booking cancelled and customer notified.' }); this.cancellingId.set(null); this.load(); },
      error: (err) => {
        const detail = err.error?.detail;
        this.message.set({ ok: false, text: typeof detail === 'string' ? detail : 'Could not cancel.' });
        this.cancellingId.set(null);
      },
    });
  }

  submitBlock() {
    if (!this.blockDate || !this.blockSlot || this.blockSeats < 1) return;
    this.blocking.set(true);
    this.blockMsg.set(null);
    this.svc.blockSeats(this.blockDate, this.blockSlot + ':00', this.blockSeats, this.blockReason).subscribe({
      next: () => {
        this.blockMsg.set({ ok: true, text: 'Seats blocked.' });
        this.blocking.set(false);
        this.blockReason = '';
      },
      error: (err) => {
        const detail = err.error?.detail;
        this.blockMsg.set({ ok: false, text: typeof detail === 'string' ? detail : 'Could not block seats.' });
        this.blocking.set(false);
      },
    });
  }
}