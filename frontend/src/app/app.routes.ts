import { Routes } from '@angular/router';
import { Landing } from './pages/landing/landing';
import { Login } from './pages/login/login';
import { Register } from './pages/register/register';
import { CustomerHome } from './pages/customer-home/customer-home';
import { MyBookings } from './pages/my-bookings/my-bookings';
import { RestaurantLayout } from './shared/restaurant-layout/restaurant-layout';
import { RestaurantDashboard } from './pages/restaurant-dashboard/restaurant-dashboard';
import { roleGuard } from './core/auth.guard';
import { RestaurantBookings } from './pages/restaurant-bookings/restaurant-bookings';

import { RestaurantAnalytics } from './pages/restaurant-analytics/restaurant-analytics';

import { RestaurantCustomers } from './pages/restaurant-customers/restaurant-customers';
import { RestaurantInsights } from './pages/restaurant-insights/restaurant-insights';
import { RestaurantCampaigns } from './pages/restaurant-campaigns/restaurant-campaigns';


export const routes: Routes = [
  { path: '', component: Landing },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'customer', component: CustomerHome, canActivate: [roleGuard('customer')] },
  { path: 'my-bookings', component: MyBookings, canActivate: [roleGuard('customer')] },
  {
    path: 'restaurant',
    component: RestaurantLayout,
    canActivate: [roleGuard('restaurant')],
    children: [
      { path: '', component: RestaurantDashboard },
      { path: 'bookings', component: RestaurantBookings },
      { path: 'customers', component: RestaurantCustomers },
      { path: 'insights', component: RestaurantInsights },
      { path: 'campaigns', component: RestaurantCampaigns },

      { path: 'campaigns', component: RestaurantCampaigns },
      { path: 'analytics', component: RestaurantAnalytics },      
    ],
  },
  { path: '**', redirectTo: '' },
];