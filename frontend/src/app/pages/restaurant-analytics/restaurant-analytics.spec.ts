import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RestaurantAnalytics } from './restaurant-analytics';

describe('RestaurantAnalytics', () => {
  let component: RestaurantAnalytics;
  let fixture: ComponentFixture<RestaurantAnalytics>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestaurantAnalytics],
    }).compileComponents();

    fixture = TestBed.createComponent(RestaurantAnalytics);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
