import { Component, computed, input } from '@angular/core';
import { seatTone } from '../seat-tone';

@Component({
  selector: 'app-seat-table',
  templateUrl: './seat-table.html',
  styleUrl: './seat-table.css',
})
export class SeatTable {
  total = input.required<number>();
  taken = input.required<number>();

  seats = computed(() => {
    const n = this.total();
    return Array.from({ length: n }, (_, i) => {
      const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
      return { x: Math.cos(angle) * 22, y: Math.sin(angle) * 22, taken: i < this.taken() };
    });
  });

  tone = computed(() => seatTone(this.total() - this.taken(), this.total()));
}