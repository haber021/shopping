/**
 * Main JavaScript file for the ERP Shopping System
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    initializeTooltips();
    
    // Initialize alert auto-close
    initializeAlertDismiss();
    
    // Initialize sidebar toggle for mobile
    initializeSidebarToggle();
    
    // Add event listeners for dynamic elements
    addEventListeners();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize auto-closing of alert messages after 5 seconds
 */
function initializeAlertDismiss() {
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}

/**
 * Initialize sidebar toggle for mobile view
 */
function initializeSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('body').classList.toggle('sidebar-collapsed');
        });
    }
}

/**
 * Add event listeners to dynamic elements
 */
function addEventListeners() {
    // Search form submission
    const searchForms = document.querySelectorAll('.search-form');
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="search"]');
            if (searchInput.value.trim() === '') {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Date range pickers
    const dateRangePickers = document.querySelectorAll('.date-range-picker');
    dateRangePickers.forEach(picker => {
        // Any date range picker initialization would go here
    });
    
    // Product quantity inputs
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value < 1) {
                this.value = 1;
            }
        });
    });
}

/**
 * Format a number as currency
 * @param {number} value - The value to format
 * @param {string} currency - The currency symbol (default: $)
 * @returns {string} The formatted currency string
 */
function formatCurrency(value, currency = '$') {
    return `${currency}${parseFloat(value).toFixed(2)}`;
}

/**
 * Handle confirmation dialogs
 * @param {string} message - The confirmation message
 * @returns {boolean} True if confirmed, false otherwise
 */
function confirmAction(message = 'Are you sure you want to proceed?') {
    return confirm(message);
}

/**
 * Handle errors from API requests
 * @param {Error} error - The error object
 * @param {string} defaultMessage - The default error message
 */
function handleApiError(error, defaultMessage = 'An error occurred. Please try again.') {
    console.error('API Error:', error);
    alert(defaultMessage);
}

/**
 * Show a loading spinner
 * @param {HTMLElement} element - The element to show the spinner in
 * @param {string} size - The size of the spinner (sm, md, lg)
 */
function showSpinner(element, size = 'md') {
    const spinner = document.createElement('div');
    spinner.className = `spinner-border text-primary spinner-border-${size}`;
    spinner.setAttribute('role', 'status');
    
    const span = document.createElement('span');
    span.className = 'visually-hidden';
    span.textContent = 'Loading...';
    
    spinner.appendChild(span);
    
    // Clear the element and add the spinner
    element.innerHTML = '';
    element.appendChild(spinner);
}

/**
 * Check if a string is a valid email address
 * @param {string} email - The email address to validate
 * @returns {boolean} True if valid, false otherwise
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}
