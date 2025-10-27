import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TestCasesComponent } from './components/test-cases/test-cases.component';
import { TestCaseDetailsComponent } from './components/test-case-details/test-case-details.component';
import { MockHttpInterceptor } from './services/mock-http.interceptor';

// Angular Material Modules
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatSortModule } from '@angular/material/sort';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { LandingComponent } from './components/landing/landing.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { ViewToggleComponent } from './components/view-toggle/view-toggle.component';
import { MockToggleComponent } from './components/mock-toggle/mock-toggle.component';

@NgModule({
  declarations: [
    AppComponent,
    TestCasesComponent,
    TestCaseDetailsComponent,
    LandingComponent,
    DashboardComponent,
    ViewToggleComponent,
    MockToggleComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    
    // Angular Material
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule,
    MatTabsModule,
    MatTooltipModule
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: MockHttpInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }