import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RestaurantBookings } from './restaurant-bookings';

describe('RestaurantBookings', () => {
  let component: RestaurantBookings;
  let fixture: ComponentFixture<RestaurantBookings>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestaurantBookings],
    }).compileComponents();

    fixture = TestBed.createComponent(RestaurantBookings);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
