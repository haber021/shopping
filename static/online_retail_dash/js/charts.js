/**
 * Charts initialization and updates for the ERP System dashboard
 * Uses Chart.js for data visualization
 */

// Chart instances
let salesTrendChart;
let earningSummaryChart;

// Color settings
const chartColors = {
    primary: '#3b82f6',
    secondary: '#10b981',
    grid: '#e2e8f0',
    text: '#64748b'
};

// Initialize charts
document.addEventListener('DOMContentLoaded', () => {
    initializeCharts();
});

/**
 * Initialize dashboard charts
 */
function initializeCharts() {
    const salesTrendCtx = document.getElementById('sales-trend-chart');
    const earningSummaryCtx = document.getElementById('earning-summary-chart');
    
    if (salesTrendCtx) {
        salesTrendChart = createSalesTrendChart(salesTrendCtx);
    }
    
    if (earningSummaryCtx) {
        earningSummaryChart = createEarningSummaryChart(earningSummaryCtx);
    }
}

/**
 * Create Sales Trend bar chart
 * @param {HTMLElement} ctx - Canvas context
 * @returns {Chart} Chart.js instance
 */
function createSalesTrendChart(ctx) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
            datasets: [{
                label: 'Sales',
                data: [],
                backgroundColor: chartColors.primary,
                borderColor: chartColors.primary,
                borderWidth: 0,
                borderRadius: 4,
                barThickness: 12
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
                    callbacks: {
                        label: function(context) {
                            return 'Sales: ₱' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid,
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000) {
                                return value / 1000 + 'k';
                            }
                            return value;
                        },
                        color: chartColors.text,
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: chartColors.text,
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

/**
 * Create Earning Summary line chart
 * @param {HTMLElement} ctx - Canvas context
 * @returns {Chart} Chart.js instance
 */
function createEarningSummaryChart(ctx) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
            datasets: [{
                label: 'Earnings',
                data: [],
                backgroundColor: 'transparent',
                borderColor: chartColors.secondary,
                borderWidth: 3,
                pointBackgroundColor: chartColors.secondary,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4,
                tension: 0.2
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
                    callbacks: {
                        label: function(context) {
                            return 'Earnings: ₱' + formatNumber(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: chartColors.grid,
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000) {
                                return value / 1000 + 'k';
                            }
                            return value;
                        },
                        color: chartColors.text,
                        font: {
                            size: 11
                        }
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        color: chartColors.text,
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

/**
 * Update charts with new data
 * @param {Object} data - Dashboard data
 */
function updateCharts(data) {
    if (salesTrendChart && data.sales_trend) {
        updateSalesTrendChart(data.sales_trend);
    }
    
    if (earningSummaryChart && data.earning_summary) {
        updateEarningSummaryChart(data.earning_summary);
    }
}

/**
 * Update Sales Trend chart with new data
 * @param {Array} salesData - Sales trend data
 */
function updateSalesTrendChart(salesData) {
    const chartData = salesData.map(item => item.value);
    
    salesTrendChart.data.datasets[0].data = chartData;
    salesTrendChart.update();
}

/**
 * Update Earning Summary chart with new data
 * @param {Array} earningData - Earning summary data
 */
function updateEarningSummaryChart(earningData) {
    const chartData = earningData.map(item => item.value);
    
    earningSummaryChart.data.datasets[0].data = chartData;
    earningSummaryChart.update();
}

/**
 * Format number for display in charts
 * @param {number} value - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(value) {
    return new Intl.NumberFormat().format(value);
}
