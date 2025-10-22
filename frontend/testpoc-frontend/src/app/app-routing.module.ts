import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LandingComponent } from './components/landing/landing.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TestCasesComponent } from './components/test-cases/test-cases.component';
import { TestCaseDetailsComponent } from './components/test-case-details/test-case-details.component';

const routes: Routes = [
  { path: '', redirectTo: '/landing', pathMatch: 'full' },
  { path: 'landing', component: LandingComponent },
  { path: 'role-selection', redirectTo: '/dashboard' },
  { path: 'dashboard', component: DashboardComponent },
  { path: 'test-cases', component: TestCasesComponent },
  { path: 'test-case/:id', component: TestCaseDetailsComponent },
  { path: '**', redirectTo: '/landing' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
