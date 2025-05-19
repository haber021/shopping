// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Set up auto-dismiss for alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Set up event listeners for inventory updates
    setupInventoryUpdateListeners();
    
    // Set up event listeners for notifications
    setupNotificationListeners();
});

// Function to handle the inventory update AJAX request
function updateInventory(productId, quantity) {
    fetch('/api/inventory/update/', {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            productId: productId,
            quantity: parseInt(quantity)
        })
    })
    .then(response => response.json())
    .then(data => {
        // Show success message
        showAlert('Inventory updated successfully', 'success');
        
        // Update the UI
        const statusCell = document.querySelector(`#product-${productId}-status`);
        if (statusCell) {
            statusCell.textContent = data.status;
            statusCell.className = `status-${data.status}`;
        }
    })
    .catch(error => {
        console.error('Error updating inventory:', error);
        showAlert('Failed to update inventory', 'danger');
    });
}

// Function to set up inventory update listeners
function setupInventoryUpdateListeners() {
    const updateButtons = document.querySelectorAll('.btn-update-inventory');
    updateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const quantityInput = document.querySelector(`#quantity-${productId}`);
            if (quantityInput) {
                updateInventory(productId, quantityInput.value);
            }
        });
    });
}

// Function to mark notification as read
function markNotificationAsRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/read/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        // Remove the notification from the UI
        const notificationElement = document.querySelector(`#notification-${notificationId}`);
        if (notificationElement) {
            notificationElement.remove();
        }
        
        // Update the notification count
        updateNotificationCount();
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// Function to set up notification listeners
function setupNotificationListeners() {
    const markReadButtons = document.querySelectorAll('.btn-mark-read');
    markReadButtons.forEach(button => {
        button.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            markNotificationAsRead(notificationId);
        });
    });
}

// Function to update notification count
function updateNotificationCount() {
    const notificationBadge = document.querySelector('#notification-badge');
    if (notificationBadge) {
        const count = document.querySelectorAll('.notification-item').length;
        notificationBadge.textContent = count;
        if (count === 0) {
            notificationBadge.style.display = 'none';
        } else {
            notificationBadge.style.display = 'inline-block';
        }
    }
}

// Function to show an alert
function showAlert(message, type) {
    const alertsContainer = document.querySelector('.messages');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}