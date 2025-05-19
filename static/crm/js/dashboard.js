document.addEventListener('DOMContentLoaded', function() {
    // Create the sales pipeline chart
    const pipelineCtx = document.getElementById('salesPipelineChart');
    if (pipelineCtx) {
        const leadStages = Object.keys(leadCounts);
        const leadCountsData = Object.values(leadCounts);
        const leadValuesData = Object.values(leadValues);
        
        new Chart(pipelineCtx, {
            type: 'bar',
            data: {
                labels: leadStages,
                datasets: [
                    {
                        label: 'Number of Leads',
                        data: leadCountsData,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Value ($)',
                        data: leadValuesData,
                        backgroundColor: 'rgba(255, 99, 132, 0.7)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        yAxisID: 'y1',
                        type: 'line'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Number of Leads'
                        }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Value ($)'
                        },
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }
    
    // Create the monthly lead performance chart
    const monthlyLeadCtx = document.getElementById('monthlyLeadChart');
    if (monthlyLeadCtx && monthlyData) {
        const data = JSON.parse(monthlyData);
        
        new Chart(monthlyLeadCtx, {
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
    
    // Handle quick action buttons
    const quickAddContactBtn = document.getElementById('quickAddContact');
    if (quickAddContactBtn) {
        quickAddContactBtn.addEventListener('click', function() {
            window.location.href = '/contacts/new';
        });
    }
    
    const quickScheduleTaskBtn = document.getElementById('quickScheduleTask');
    if (quickScheduleTaskBtn) {
        quickScheduleTaskBtn.addEventListener('click', function() {
            // Open the task modal if it exists
            const taskModal = new bootstrap.Modal(document.getElementById('newTaskModal'));
            if (taskModal) {
                taskModal.show();
            } else {
                window.location.href = '/tasks';
            }
        });
    }
});
