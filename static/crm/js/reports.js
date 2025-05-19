document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lead Distribution by Stage Chart
    const stageDistributionCtx = document.getElementById('leadDistributionChart');
    if (stageDistributionCtx) {
        const stages = Object.keys(leadCounts);
        const counts = Object.values(leadCounts);
        
        new Chart(stageDistributionCtx, {
            type: 'pie',
            data: {
                labels: stages,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)', // New
                        'rgba(75, 192, 192, 0.7)', // Contacted
                        'rgba(255, 206, 86, 0.7)', // Proposal
                        'rgba(75, 192, 192, 0.7)', // Closed-Won
                        'rgba(255, 99, 132, 0.7)'  // Closed-Lost
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)'
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
                    title: {
                        display: true,
                        text: 'Lead Distribution by Stage'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Initialize Lead Value Distribution Chart
    const valueDistributionCtx = document.getElementById('leadValueChart');
    if (valueDistributionCtx) {
        const stages = Object.keys(leadValues);
        const values = Object.values(leadValues);
        
        new Chart(valueDistributionCtx, {
            type: 'bar',
            data: {
                labels: stages,
                datasets: [{
                    label: 'Total Value ($)',
                    data: values,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)', // New
                        'rgba(75, 192, 192, 0.7)', // Contacted
                        'rgba(255, 206, 86, 0.7)', // Proposal
                        'rgba(75, 192, 192, 0.7)', // Closed-Won
                        'rgba(255, 99, 132, 0.7)'  // Closed-Lost
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Value ($)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Lead Value by Stage'
                    }
                }
            }
        });
    }
    
    // Initialize Monthly Performance Chart
    const monthlyCtx = document.getElementById('monthlyPerformanceChart');
    if (monthlyCtx && monthlyData) {
        const data = JSON.parse(monthlyData);
        
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: data.months,
                datasets: [
                    {
                        label: 'New Leads',
                        data: data.new_leads,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: 'Won Deals',
                        data: data.won_deals,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: 'Lost Deals',
                        data: data.lost_deals,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Lead Performance'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Count'
                        }
                    }
                }
            }
        });
    }
    
    // Initialize Conversion Rate Chart
    const conversionCtx = document.getElementById('conversionRateChart');
    if (conversionCtx && monthlyData) {
        const data = JSON.parse(monthlyData);
        const conversionRates = [];
        
        // Calculate conversion rates (won deals / new leads)
        for (let i = 0; i < data.months.length; i++) {
            const newLeads = data.new_leads[i];
            const wonDeals = data.won_deals[i];
            const rate = newLeads > 0 ? (wonDeals / newLeads) * 100 : 0;
            conversionRates.push(parseFloat(rate.toFixed(1)));
        }
        
        new Chart(conversionCtx, {
            type: 'bar',
            data: {
                labels: data.months,
                datasets: [{
                    label: 'Conversion Rate (%)',
                    data: conversionRates,
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Conversion Rate (%)'
                        },
                        max: 100
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Conversion Rate'
                    }
                }
            }
        });
    }
    
    // Handle time period selection
    const timePeriodSelect = document.getElementById('timePeriod');
    if (timePeriodSelect) {
        timePeriodSelect.addEventListener('change', function() {
            const months = this.value;
            const url = new URL(window.location);
            url.searchParams.set('months', months);
            window.location.href = url.toString();
        });
    }
    
    // Initialize export functionality
    const exportButtons = document.querySelectorAll('[data-export]');
    if (exportButtons.length > 0) {
        exportButtons.forEach(button => {
            button.addEventListener('click', function() {
                const chartId = this.getAttribute('data-chart');
                const format = this.getAttribute('data-export');
                const chart = Chart.getChart(chartId);
                
                if (chart) {
                    if (format === 'png') {
                        // Export as PNG
                        const link = document.createElement('a');
                        link.href = chart.toBase64Image();
                        link.download = `${chartId}-export.png`;
                        link.click();
                    } else if (format === 'pdf') {
                        // For PDF we would typically use a library like jsPDF
                        // This is a simplified version
                        alert('PDF export functionality would be implemented here with jsPDF');
                    }
                }
            });
        });
    }
});
