/**
 * Advanced Charts and Analytics for Validex
 * Real-time data visualization and analytics
 */

class ValidexCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            primary: '#007bff',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8',
            secondary: '#6c757d',
            light: '#f8f9fa',
            dark: '#343a40'
        };
        this.gradientColors = {
            primary: ['#007bff', '#0056b3'],
            success: ['#28a745', '#1e7e34'],
            warning: ['#ffc107', '#e0a800'],
            danger: ['#dc3545', '#c82333'],
            info: ['#17a2b8', '#138496']
        };
    }

    /**
     * Create gradient background for charts
     */
    createGradient(ctx, colorArray) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, colorArray[0]);
        gradient.addColorStop(1, colorArray[1]);
        return gradient;
    }

    /**
     * Initialize all dashboard charts
     */
    initDashboardCharts() {
        this.initTestCasesOverview();
        this.initTestExecutionChart();
        this.initFeatureDistribution();
        this.initPriorityBreakdown();
        this.initTestStatusTrend();
        this.initAppCoverage();
        this.initRecentActivity();
    }

    /**
     * Test Cases Overview - Doughnut Chart
     */
    initTestCasesOverview() {
        const ctx = document.getElementById('testCasesOverview');
        if (!ctx) return;

        this.charts.testCasesOverview = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed', 'Pending', 'Blocked'],
                datasets: [{
                    data: [45, 12, 8, 3],
                    backgroundColor: [
                        this.colors.success,
                        this.colors.danger,
                        this.colors.warning,
                        this.colors.secondary
                    ],
                    borderWidth: 3,
                    borderColor: '#fff',
                    hoverBorderWidth: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: true,
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed * 100) / total).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true,
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * Test Execution Chart - Line Chart
     */
    initTestExecutionChart() {
        const ctx = document.getElementById('testExecutionChart');
        if (!ctx) return;

        this.charts.testExecution = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Tests Executed',
                    data: [12, 19, 15, 25, 22, 18, 8],
                    borderColor: this.colors.primary,
                    backgroundColor: this.createGradient(ctx, this.gradientColors.primary),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: this.colors.primary,
                    pointBorderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }, {
                    label: 'Tests Passed',
                    data: [10, 16, 12, 20, 18, 15, 6],
                    borderColor: this.colors.success,
                    backgroundColor: this.createGradient(ctx, this.gradientColors.success),
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: this.colors.success,
                    pointBorderWidth: 3,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * Feature Distribution - Bar Chart
     */
    initFeatureDistribution() {
        const ctx = document.getElementById('featureDistribution');
        if (!ctx) return;

        this.charts.featureDistribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Login', 'Dashboard', 'Reports', 'Settings', 'Profile', 'Search'],
                datasets: [{
                    label: 'Test Cases',
                    data: [15, 12, 8, 6, 4, 3],
                    backgroundColor: this.createGradient(ctx, this.gradientColors.info),
                    borderColor: this.colors.info,
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.info,
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * Priority Breakdown - Polar Area Chart
     */
    initPriorityBreakdown() {
        const ctx = document.getElementById('priorityBreakdown');
        if (!ctx) return;

        this.charts.priorityBreakdown = new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [8, 15, 25, 12],
                    backgroundColor: [
                        this.colors.danger,
                        this.colors.warning,
                        this.colors.info,
                        this.colors.secondary
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            display: false
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * Test Status Trend - Area Chart
     */
    initTestStatusTrend() {
        const ctx = document.getElementById('testStatusTrend');
        if (!ctx) return;

        this.charts.testStatusTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Passed',
                    data: [20, 35, 45, 60],
                    borderColor: this.colors.success,
                    backgroundColor: this.colors.success + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Failed',
                    data: [5, 8, 12, 15],
                    borderColor: this.colors.danger,
                    backgroundColor: this.colors.danger + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Pending',
                    data: [15, 12, 8, 5],
                    borderColor: this.colors.warning,
                    backgroundColor: this.colors.warning + '20',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * App Coverage - Radar Chart
     */
    initAppCoverage() {
        const ctx = document.getElementById('appCoverage');
        if (!ctx) return;

        this.charts.appCoverage = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Login', 'Dashboard', 'Reports', 'Settings', 'Profile', 'Search', 'API', 'Database'],
                datasets: [{
                    label: 'App 1',
                    data: [85, 90, 75, 80, 70, 85, 95, 88],
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primary + '20',
                    borderWidth: 3,
                    pointBackgroundColor: this.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }, {
                    label: 'App 2',
                    data: [75, 80, 85, 70, 90, 75, 85, 82],
                    borderColor: this.colors.success,
                    backgroundColor: this.colors.success + '20',
                    borderWidth: 3,
                    pointBackgroundColor: this.colors.success,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }, {
                    label: 'App 3',
                    data: [90, 85, 80, 95, 75, 90, 80, 85],
                    borderColor: this.colors.warning,
                    backgroundColor: this.colors.warning + '20',
                    borderWidth: 3,
                    pointBackgroundColor: this.colors.warning,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: this.colors.primary,
                        borderWidth: 1,
                        cornerRadius: 8
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            font: {
                                size: 11,
                                weight: '500'
                            }
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                }
            }
        });
    }

    /**
     * Recent Activity - Timeline Chart
     */
    initRecentActivity() {
        const ctx = document.getElementById('recentActivity');
        if (!ctx) return;

        // Create a simple activity timeline
        const activityData = [
            { time: '10:30 AM', action: 'Test Case Executed', user: 'John Doe', status: 'success' },
            { time: '10:15 AM', action: 'Test Case Failed', user: 'Jane Smith', status: 'danger' },
            { time: '09:45 AM', action: 'New Test Case Added', user: 'Mike Johnson', status: 'info' },
            { time: '09:30 AM', action: 'Test Suite Completed', user: 'Sarah Wilson', status: 'success' },
            { time: '09:00 AM', action: 'Test Case Updated', user: 'David Brown', status: 'warning' }
        ];

        const timelineContainer = document.getElementById('recentActivity');
        if (timelineContainer) {
            timelineContainer.innerHTML = activityData.map(activity => `
                <div class="timeline-item">
                    <div class="timeline-marker bg-${activity.status}"></div>
                    <div class="timeline-content">
                        <div class="timeline-time">${activity.time}</div>
                        <div class="timeline-action">${activity.action}</div>
                        <div class="timeline-user">by ${activity.user}</div>
                    </div>
                </div>
            `).join('');
        }
    }

    /**
     * Update chart data dynamically
     */
    updateChart(chartName, newData) {
        if (this.charts[chartName]) {
            this.charts[chartName].data = newData;
            this.charts[chartName].update();
        }
    }

    /**
     * Destroy all charts
     */
    destroyAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }

    /**
     * Resize all charts
     */
    resizeAllCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.resize();
        });
    }
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.validexCharts = new ValidexCharts();
    
    // Initialize charts if on dashboard
    if (document.getElementById('testCasesOverview')) {
        window.validexCharts.initDashboardCharts();
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.validexCharts) {
            window.validexCharts.resizeAllCharts();
        }
    });
});
