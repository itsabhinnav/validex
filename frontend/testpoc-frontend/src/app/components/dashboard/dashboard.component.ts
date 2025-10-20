import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

interface DashboardStats {
  apps: string[];
  testTypes: string[];
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  totalCases: number = 0;
  fileCount: number = 0;
  stats: DashboardStats = {
    apps: [],
    testTypes: []
  };

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.loadDashboardData();
  }

  loadDashboardData() {
    // This would call the Flask API to get dashboard data
    // For now, we'll use mock data
    this.totalCases = 150;
    this.fileCount = 8;
    this.stats = {
      apps: ['App1', 'App2', 'App3'],
      testTypes: ['Unit', 'Integration', 'E2E']
    };
  }
}