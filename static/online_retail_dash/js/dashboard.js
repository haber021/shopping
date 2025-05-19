/**
 * Dashboard functionality for the ERP System
 * Handles data fetching, UI updates, and filter interactions
 */

// DOM elements
const filterButtons = document.querySelectorAll('.filter-btn');
const topSellingDropdown = document.getElementById('top-selling-day');

// State
let currentPeriod = 'today';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Load initial data (today)
    fetchDashboardData('today');
    
    // Set up event listeners
    setupEventListeners();
});

/**
 * Set up event listeners for interactive elements
 */
function setupEventListeners() {
    // Time period filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const period = button.getAttribute('data-period');
            
            // Update UI
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update dropdown to match selected period
            if (topSellingDropdown) {
                topSellingDropdown.value = period;
            }
            
            // Fetch and update data
            fetchDashboardData(period);
        });
    });
    
    // Top selling products dropdown
    if (topSellingDropdown) {
        topSellingDropdown.addEventListener('change', () => {
            const period = topSellingDropdown.value;
            
            // Update buttons to match selected period
            filterButtons.forEach(btn => {
                if (btn.getAttribute('data-period') === period) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });
            
            // Fetch and update data
            fetchDashboardData(period);
        });
    }
    
    // View all orders button - for demo, just show alert
    const viewAllBtn = document.querySelector('.view-all-btn');
    if (viewAllBtn) {
        viewAllBtn.addEventListener('click', () => {
            alert('This would navigate to the Orders page in a complete application.');
        });
    }
}

/**
 * Fetch dashboard data from API
 * @param {string} period - Time period (today, yesterday, week, month)
 */
function fetchDashboardData(period) {
    currentPeriod = period;
    
    // Show loading state
    showLoadingState();
    
    // Fetch data from API
    fetch(`/api/dashboard_data?period=${period}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateDashboard(data);
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
            showErrorState();
        });
}

/**
 * Update dashboard UI with fetched data
 * @param {Object} data - Dashboard data from API
 */
function updateDashboard(data) {
    // Update KPI cards
    updateKpiCards(data.kpi);
    
    // Update charts
    updateCharts(data);
    
    // Update inventory levels
    updateInventoryLevels(data.inventory_levels);
    
    // Update top selling products
    updateTopSellingProducts(data.top_selling_products);
    
    // Update recent activities
    updateRecentActivities(data.recent_activities);
}

/**
 * Update KPI card values
 * @param {Object} kpiData - KPI data object
 */
function updateKpiCards(kpiData) {
    document.getElementById('total-orders').textContent = kpiData.total_orders;
    document.getElementById('revenue').textContent = formatCurrency(kpiData.revenue);
    document.getElementById('low-stocks-alert').textContent = kpiData.low_stocks_alert;
    document.getElementById('pending-orders').textContent = kpiData.pending_orders;
}

/**
 * Update inventory levels table
 * @param {Array} inventoryData - Inventory levels data
 */
function updateInventoryLevels(inventoryData) {
    const tableBody = document.getElementById('inventory-levels-body');
    
    if (!tableBody) return;
    
    // Clear existing content
    tableBody.innerHTML = '';
    
    // Add new rows
    inventoryData.forEach(item => {
        const row = document.createElement('tr');
        
        const statusClass = `status-${item.status.toLowerCase()}`;
        
        row.innerHTML = `
            <td>${item.category}</td>
            <td>${item.qty}</td>
            <td><span class="status-badge ${statusClass}">${item.status}</span></td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Update top selling products list
 * @param {Array} productsData - Top selling products data
 */
function updateTopSellingProducts(productsData) {
    const productsList = document.getElementById('top-selling-products');
    
    if (!productsList) return;
    
    // Clear existing content
    productsList.innerHTML = '';
    
    // Add new items
    productsData.forEach(product => {
        const item = document.createElement('li');
        
        item.innerHTML = `
            <span class="product-name">${product.name}</span>
            <span class="sold-qty">- ${product.sold} sold</span>
        `;
        
        productsList.appendChild(item);
    });
}

/**
 * Update recent activities list
 * @param {Array} activitiesData - Recent activities data
 */
function updateRecentActivities(activitiesData) {
    const activitiesList = document.getElementById('recent-activities');
    
    if (!activitiesList) return;
    
    // Clear existing content
    activitiesList.innerHTML = '';
    
    // Add new items
    activitiesData.forEach(activity => {
        const item = document.createElement('li');
        item.className = 'activity-item';
        
        const statusClass = `status-${activity.status.toLowerCase().replace(' ', '-')}`;
        
        item.innerHTML = `
            <div class="activity-header">
                <span class="order-no">Order #${activity.order_no}</span>
                <span class="activity-status ${statusClass}">${activity.status}</span>
            </div>
            <div class="activity-product">${activity.product}</div>
            <div class="activity-details">Placed by ${activity.placed_by}</div>
        `;
        
        activitiesList.appendChild(item);
    });
}

/**
 * Show loading state for dashboard
 */
function showLoadingState() {
    // For a production application, you might add loading spinners or skeleton loaders
    console.log('Loading dashboard data...');
}

/**
 * Show error state if data fetching fails
 */
function showErrorState() {
    // For a production application, display a user-friendly error message
    console.error('Failed to load dashboard data');
}

/**
 * Format currency value
 * @param {number} value - Currency value
 * @returns {string} Formatted currency string
 */
function formatCurrency(value) {
    return value.toLocaleString();
}
