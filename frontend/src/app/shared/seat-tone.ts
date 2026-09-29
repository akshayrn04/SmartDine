// basil = plenty free, turmeric = filling up, pomegranate = nearly full
export function seatTone(free: number, total: number): string {
  const ratio = free / total;
  return ratio >= 0.6 ? 'var(--basil)' : ratio >= 0.3 ? 'var(--turmeric)' : 'var(--pom)';
}
export function occupancyTone(booked: number, total: number): string {
  return seatTone(total - booked, total);
}