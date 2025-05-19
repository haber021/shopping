/**
 * Chart initialization and configuration for the dashboard
 */
document.addEventListener('DOMContentLoaded', function() {
    // Configure Chart.js defaults
    Chart.defaults.font.family = "'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.color = '#666';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    Chart.defaults.plugins.legend.position = 'top';

    // Employee Attendance Chart
    const attendanceChartElement = document.getElementById('employeeAttendanceChart');
    if (attendanceChartElement) {
        const attendanceChart = new Chart(attendanceChartElement, {
            type: 'pie',
            data: {
                labels: ['Present', 'Late', 'Absent'],
                datasets: [{
                    label: 'Attendance',
                    data: [85, 8, 7],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(220, 53, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                return `${label}: ${value}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Weekly Attendance Trend Chart
    const weeklyAttendanceElement = document.getElementById('weeklyAttendanceChart');
    if (weeklyAttendanceElement) {
        const weeklyAttendanceChart = new Chart(weeklyAttendanceElement, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Present %',
                    data: [92, 89, 88, 90, 87, 84, 82],
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    borderColor: 'rgba(13, 110, 253, 1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 80,
                        max: 100
                    }
                }
            }
        });
    }

    // Employee Distribution by Department
    const deptDistributionElement = document.getElementById('departmentDistributionChart');
    if (deptDistributionElement) {
        const deptDistributionChart = new Chart(deptDistributionElement, {
            type: 'bar',
            data: {
                labels: ['Sales', 'Marketing', 'HR', 'IT', 'Operations', 'Finance', 'Warehouse'],
                datasets: [{
                    label: 'Number of Employees',
                    data: [45, 30, 20, 25, 35, 20, 41],
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.8)',
                        'rgba(220, 53, 69, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(111, 66, 193, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(108, 117, 125, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Recruitment Status Chart
    const recruitmentStatusElement = document.getElementById('recruitmentStatusChart');
    if (recruitmentStatusElement) {
        const recruitmentStatusChart = new Chart(recruitmentStatusElement, {
            type: 'doughnut',
            data: {
                labels: ['New Applications', 'Screening', 'Interview', 'Assessment', 'Offer', 'Hired', 'Rejected'],
                datasets: [{
                    label: 'Recruitment Status',
                    data: [15, 8, 5, 3, 2, 4, 7],
                    backgroundColor: [
                        'rgba(13, 110, 253, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(23, 162, 184, 0.8)',
                        'rgba(111, 66, 193, 0.8)',
                        'rgba(0, 123, 255, 0.8)',
                        'rgba(220, 53, 69, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                cutout: '60%'
            }
        });
    }

    // Leave Trends Chart
    const leaveTrendsElement = document.getElementById('leaveTrendsChart');
    if (leaveTrendsElement) {
        const leaveTrendsChart = new Chart(leaveTrendsElement, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'Sick Leave',
                        data: [4, 5, 7, 5, 4, 3, 4, 6, 5, 6, 7, 8],
                        borderColor: 'rgba(220, 53, 69, 1)',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Vacation',
                        data: [2, 3, 5, 6, 7, 10, 12, 15, 10, 6, 4, 8],
                        borderColor: 'rgba(40, 167, 69, 1)',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Personal',
                        data: [1, 2, 1, 3, 2, 2, 3, 2, 2, 3, 2, 3],
                        borderColor: 'rgba(255, 193, 7, 1)',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Days'
                        }
                    }
                }
            }
        });
    }

    // Sales vs Staffing Chart
    const salesStaffingElement = document.getElementById('salesStaffingChart');
    if (salesStaffingElement) {
        const salesStaffingChart = new Chart(salesStaffingElement, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [
                    {
                        label: 'Sales (in $1000)',
                        data: [120, 115, 130, 140, 160, 170],
                        backgroundColor: 'rgba(13, 110, 253, 0.8)',
                        order: 2
                    },
                    {
                        label: 'Staff Hours',
                        data: [800, 820, 840, 860, 900, 920],
                        type: 'line',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        fill: false,
                        order: 1
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        type: 'linear',
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Sales ($1000)'
                        }
                    },
                    y1: {
                        beginAtZero: true,
                        type: 'linear',
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Staff Hours'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }

    // Function to update charts with real data
    window.updateCharts = function(data) {
        if (!data) return;
        
        // Example of updating attendance chart
        if (data.attendance && attendanceChart) {
            attendanceChart.data.datasets[0].data = [
                data.attendance.present,
                data.attendance.late,
                data.attendance.absent
            ];
            attendanceChart.update();
        }
        
        // More chart updates can be added here
    };
});
