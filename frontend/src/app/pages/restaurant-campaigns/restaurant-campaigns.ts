import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CampaignService, Campaign } from '../../core/campaign.service';

@Component({
  selector: 'app-restaurant-campaigns',
  imports: [FormsModule],
  templateUrl: './restaurant-campaigns.html',
  styleUrl: './restaurant-campaigns.css',
})
export class RestaurantCampaigns {
  private svc = inject(CampaignService);

  list = signal<Campaign[]>([]);
  loading = signal(true);
  message = signal<{ ok: boolean; text: string } | null>(null);
  busyId = signal<number | null>(null);
  openId = signal<number | null>(null);
  notifs = signal<any[]>([]);

  newSlot = '';
  creating = signal(false);

  constructor() { this.load(); }

  load() {
    this.loading.set(true);
    this.svc.list().subscribe({
      next: (l) => { this.list.set(l); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }

  todayIso(): string {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }

  createForSlot() {
    if (!this.newSlot) return;
    this.creating.set(true);
    this.message.set(null);
    this.svc.create(this.todayIso(), this.newSlot + ':00').subscribe({
      next: () => { this.creating.set(false); this.newSlot = ''; this.load(); },
      error: (err) => {
        const detail = err.error?.detail;
        this.message.set({ ok: false, text: typeof detail === 'string' ? detail : 'Could not create a campaign.' });
        this.creating.set(false);
      },
    });
  }

  toggleOpen(c: Campaign) {
    if (this.openId() === c.id) { this.openId.set(null); return; }
    this.openId.set(c.id);
    this.svc.notifications(c.id).subscribe({ next: (n) => this.notifs.set(n) });
  }

  approve(c: Campaign) {
    this.busyId.set(c.id);
    this.svc.approve(c.id).subscribe({
      next: () => { this.message.set({ ok: true, text: 'Campaign approved and sent.' }); this.busyId.set(null); this.load(); },
      error: (err) => {
        const detail = err.error?.detail;
        this.message.set({ ok: false, text: typeof detail === 'string' ? detail : 'Could not approve.' });
        this.busyId.set(null);
        this.load();
      },
    });
  }

  reject(c: Campaign) {
    this.busyId.set(c.id);
    this.svc.reject(c.id).subscribe({
      next: () => { this.message.set({ ok: true, text: 'Campaign rejected.' }); this.busyId.set(null); this.load(); },
      error: () => this.busyId.set(null),
    });
  }

  hourLabel(t: string): string {
    const h = +t.slice(0, 2);
    return `${h % 12 || 12} ${h < 12 ? 'AM' : 'PM'}`;
  }
}