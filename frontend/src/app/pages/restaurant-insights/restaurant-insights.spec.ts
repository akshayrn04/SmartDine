import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RestaurantInsights } from './restaurant-insights';

describe('RestaurantInsights', () => {
  let component: RestaurantInsights;
  let fixture: ComponentFixture<RestaurantInsights>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestaurantInsights],
    }).compileComponents();

    fixture = TestBed.createComponent(RestaurantInsights);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
