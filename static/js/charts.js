/**
 * Create a line chart
 * @param {string} elementId - The ID of the canvas element
 * @param {Object} chartData - The data for the chart
 * @param {Object} options - Optional configuration for the chart
 * @returns {Chart} The created chart instance
 */
function createLineChart(elementId, chartData, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            legend: {
                position: 'top'
            }
        }
    };
    
    // Merge default options with provided options
    const chartOptions = {...defaultOptions, ...options};
    
    return new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: chartOptions
    });
}

/**
 * Create a bar chart
 * @param {string} elementId - The ID of the canvas element
 * @param {Object} chartData - The data for the chart
 * @param {Object} options - Optional configuration for the chart
 * @returns {Chart} The created chart instance
 */
function createBarChart(elementId, chartData, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            legend: {
                position: 'top'
            }
        }
    };
    
    // Merge default options with provided options
    const chartOptions = {...defaultOptions, ...options};
    
    return new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: chartOptions
    });
}

/**
 * Create a pie chart
 * @param {string} elementId - The ID of the canvas element
 * @param {Object} chartData - The data for the chart
 * @param {Object} options - Optional configuration for the chart
 * @returns {Chart} The created chart instance
 */
function createPieChart(elementId, chartData, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right'
            }
        }
    };
    
    // Merge default options with provided options
    const chartOptions = {...defaultOptions, ...options};
    
    return new Chart(ctx, {
        type: 'pie',
        data: chartData,
        options: chartOptions
    });
}

/**
 * Create a doughnut chart
 * @param {string} elementId - The ID of the canvas element
 * @param {Object} chartData - The data for the chart
 * @param {Object} options - Optional configuration for the chart
 * @returns {Chart} The created chart instance
 */
function createDoughnutChart(elementId, chartData, options = {}) {
    const ctx = document.getElementById(elementId).getContext('2d');
    
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right'
            }
        }
    };
    
    // Merge default options with provided options
    const chartOptions = {...defaultOptions, ...options};
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: chartData,
        options: chartOptions
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
 * Generate a random color
 * @param {number} alpha - The alpha value (0-1) for the color
 * @returns {string} A random RGBA color string
 */
function getRandomColor(alpha = 0.7) {
    const r = Math.floor(Math.random() * 255);
    const g = Math.floor(Math.random() * 255);
    const b = Math.floor(Math.random() * 255);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Generate an array of random colors
 * @param {number} count - The number of colors to generate
 * @param {number} alpha - The alpha value (0-1) for the colors
 * @returns {string[]} An array of random RGBA color strings
 */
function generateRandomColors(count, alpha = 0.7) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(getRandomColor(alpha));
    }
    return colors;
}
