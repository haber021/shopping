/**
 * Dashboard.js - Main dashboard functionality for RetailPay System
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Quick Search functionality
    const quickSearchInput = document.querySelector('input[placeholder="Quick Search"]');
    if (quickSearchInput) {
        quickSearchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                // Perform search - in real app would redirect to search results
                alert('Search functionality would be implemented here with query: ' + this.value);
            }
        });
    }

    // Responsive sidebar toggle for mobile
    const sidebarToggle = document.querySelector('.navbar-toggler');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-open');
        });
    }

    // Function to format currency
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-PH', { 
            style: 'currency', 
            currency: 'PHP',
            minimumFractionDigits: 2
        }).format(amount);
    }

    // Function to format numbers with commas
    function formatNumber(num) {
        return new Intl.NumberFormat('en-PH').format(num);
    }

    // Function to format date
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-PH', options);
    }

    // Function to create chart if element exists
    function createChartIfExists(elementId, config) {
        const element = document.getElementById(elementId);
        if (element) {
            return new Chart(element.getContext('2d'), config);
        }
        return null;
    }

    // Refresh dashboard data
    function refreshDashboardData() {
        // This would make API calls to get the latest data
        // For now we'll just simulate with console log
        console.log('Dashboard data would be refreshed here');
    }

    // Set up refresh interval (every 5 minutes)
    const refreshInterval = 5 * 60 * 1000; // 5 minutes
    setInterval(refreshDashboardData, refreshInterval);

    // Add click handlers for quick action buttons
    const quickActionButtons = document.querySelectorAll('.card:last-child .btn');
    quickActionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // This would navigate to the proper page or show a modal
            // For demo purposes we'll just log the action
            console.log(`Quick action button clicked: ${this.textContent.trim()}`);
        });
    });

    // Example: Animate counter for dashboard stats
    function animateCounter(element, target, duration = 1000) {
        if (!element) return;
        
        const start = parseInt(element.textContent.replace(/[^\d]/g, '')) || 0;
        const increment = (target - start) / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
                clearInterval(timer);
                current = target;
            }
            
            element.textContent = formatCurrency(current);
        }, 16);
    }

    // Example usage of the counter animation
    // We would call this when dashboard loads or updates
    // animateCounter(document.querySelector('.total-sales'), 45000);
});
