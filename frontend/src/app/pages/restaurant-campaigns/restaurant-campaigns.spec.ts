import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RestaurantCampaigns } from './restaurant-campaigns';

describe('RestaurantCampaigns', () => {
  let component: RestaurantCampaigns;
  let fixture: ComponentFixture<RestaurantCampaigns>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RestaurantCampaigns],
    }).compileComponents();

    fixture = TestBed.createComponent(RestaurantCampaigns);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
