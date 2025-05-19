document.addEventListener('DOMContentLoaded', function() {
    // Fetch dashboard stats from the API
    fetchDashboardStats();

    // Initialize sales chart
    fetch('/api/sales-chart/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Sales Chart Data:', data); // Debugging: Log the API response
            const ctx = document.getElementById('salesChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: data.datasets
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Sales Amount ($)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `$${context.parsed.y.toFixed(2)}`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching sales chart data:', error);
            const ctx = document.getElementById('salesChart').getContext('2d');
            ctx.font = '16px Arial';
            ctx.fillText('Error loading chart data', 10, 50);
        });

    // Initialize inventory chart
    fetch('/api/inventory-chart/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Inventory Chart Data:', data); // Debugging: Log the API response
            const ctx = document.getElementById('inventoryChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Current Stock',
                        data: data.current_stock,
                        backgroundColor: 'rgba(75, 192, 192, 0.7)'
                    }, {
                        label: 'Reorder Level',
                        data: data.reorder_level,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Quantity'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Category'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching inventory chart data:', error);
            const ctx = document.getElementById('inventoryChart').getContext('2d');
            ctx.font = '16px Arial';
            ctx.fillText('Error loading chart data', 10, 50);
        });
});

/**
 * Fetch dashboard statistics from the API and update the dashboard stats cards
 */
function fetchDashboardStats() {
    fetch('/api/dashboard/stats/')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('total-orders').textContent = data.total_orders;
        document.getElementById('total-revenue').textContent = `$${data.total_revenue.toFixed(2)}`;
        document.getElementById('low-stock-count').textContent = data.low_stock_count;
        document.getElementById('pending-orders').textContent = data.pending_orders;
    })
    .catch(error => {
        console.error('Error fetching dashboard stats:', error);
    });
}


/**
 * Initialize the sales chart with data from the API
 */
function initializeSalesChart() {
    fetch('/api/dashboard/sales-chart/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('salesChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Sales Amount ($)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `$${context.parsed.y.toFixed(2)}`;
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching sales chart data:', error);
            const ctx = document.getElementById('salesChart').getContext('2d');
            ctx.font = '16px Arial';
            ctx.fillText('Error loading chart data', 10, 50);
        });
}

/**
 * Initialize the inventory chart with data from the API
 */
function initializeInventoryChart() {
    fetch('/api/dashboard/inventory-chart/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const ctx = document.getElementById('inventoryChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Stock Quantity'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Category'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching inventory chart data:', error);
            const ctx = document.getElementById('inventoryChart').getContext('2d');
            ctx.font = '16px Arial';
            ctx.fillText('Error loading chart data', 10, 50);
        });
}



