import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RestaurantCustomers } from './restaurant-customers';

describe('RestaurantCustomers', () => {
  let component: RestaurantCustomers;
  let fixture: ComponentFixture<RestaurantCustomers>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestaurantCustomers],
    }).compileComponents();

    fixture = TestBed.createComponent(RestaurantCustomers);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
