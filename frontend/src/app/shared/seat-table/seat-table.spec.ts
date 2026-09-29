import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SeatTable } from './seat-table';

describe('SeatTable', () => {
  let component: SeatTable;
  let fixture: ComponentFixture<SeatTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SeatTable],
    }).compileComponents();

    fixture = TestBed.createComponent(SeatTable);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
