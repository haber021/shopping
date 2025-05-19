/**
 * Retail.js - Retail functionality for RetailPay System
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Function to format currency
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', { 
            style: 'currency', 
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }

    // Function to format date
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString('en-US', options);
    }

    // Product filters functionality
    const productFilters = document.querySelector('form[action*="product_list"]');
    if (productFilters) {
        // Add event listener to category select
        const categorySelect = productFilters.querySelector('select[name="category"]');
        if (categorySelect) {
            categorySelect.addEventListener('change', function() {
                // Automatically submit the form when category changes
                // This would be enhanced with better UX in a real app
                // productFilters.submit();
            });
        }

        // Add event listener to reset button
        const resetButton = productFilters.querySelector('a.btn-outline-secondary');
        if (resetButton) {
            resetButton.addEventListener('click', function(e) {
                // Reset all form fields
                productFilters.querySelectorAll('select, input').forEach(field => {
                    field.value = '';
                });
                
                // Submit the form
                productFilters.submit();
                e.preventDefault();
            });
        }
    }

    // Image preview functionality for product form
    const imageUrlInput = document.querySelector('input[id$="image_url"]');
    const imagePreview = document.getElementById('imagePreview');
    
    if (imageUrlInput && imagePreview) {
        imageUrlInput.addEventListener('blur', function() {
            updateImagePreview();
        });
        
        function updateImagePreview() {
            const url = imageUrlInput.value.trim();
            if (url) {
                imagePreview.innerHTML = `<img src="${url}" alt="Product Preview" class="img-fluid">`;
            } else {
                imagePreview.innerHTML = `
                    <i class="fas fa-box fa-5x text-secondary"></i>
                    <p class="mt-3">No image URL provided</p>
                `;
            }
        }
    }

    // Handle order status changes
    const orderStatusDropdowns = document.querySelectorAll('.dropdown-menu:has(a:contains("Mark as"))');
    orderStatusDropdowns.forEach(dropdown => {
        const statusLinks = dropdown.querySelectorAll('a');
        statusLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                const orderId = this.closest('tr').querySelector('td:first-child').textContent;
                const newStatus = this.textContent.replace('Mark as ', '').trim();
                
                // In a real app, this would make an AJAX call to update the status
                // For now, just show an alert
                alert(`Order #${orderId} status would be updated to ${newStatus}`);
                e.preventDefault();
            });
        });
    });

    // Low stock warning highlight
    const lowStockItems = document.querySelectorAll('.badge.bg-warning');
    lowStockItems.forEach(badge => {
        // Add a subtle animation to draw attention
        badge.classList.add('pulse-warning');
        
        // For items that are critically low (< 5), we could add an extra class
        const quantity = parseInt(badge.textContent.split(':')[1]);
        if (quantity < 5) {
            badge.classList.add('critical-stock');
        }
    });

    // Order total calculation for order creation form
    const orderForm = document.getElementById('orderForm');
    const orderItemsTable = document.getElementById('orderItemsTable');
    
    if (orderForm && orderItemsTable) {
        // Function to update order total based on items
        function updateOrderTotal() {
            let total = 0;
            const itemRows = orderItemsTable.querySelectorAll('tbody tr:not(#noItemsRow)');
            
            itemRows.forEach(row => {
                const price = parseFloat(row.querySelector('td:nth-child(2)').textContent.replace(/[^0-9.]/g, ''));
                const quantity = parseInt(row.querySelector('td:nth-child(3)').textContent);
                total += price * quantity;
            });
            
            // Update total displays
            const totalElements = document.querySelectorAll('[id$="orderTotal"], [id$="summaryTotal"], [id$="summarySubtotal"]');
            totalElements.forEach(el => {
                el.textContent = formatCurrency(total);
            });
            
            // Update form hidden input
            const totalInput = document.querySelector('input[name$="total_amount"]');
            if (totalInput) {
                totalInput.value = total.toFixed(2);
            }
        }
        
        // Call update function when items are added/removed
        // (This would connect to the actual add/remove item functionality)
    }

    // Order print functionality
    const printOrderButton = document.querySelector('a:has(i.fa-print)');
    if (printOrderButton) {
        printOrderButton.addEventListener('click', function(e) {
            window.print();
            e.preventDefault();
        });
    }

    // Inventory quick stock update
    const stockUpdateButtons = document.querySelectorAll('.update-stock-btn');
    stockUpdateButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const currentStock = parseInt(this.dataset.currentStock);
            
            // Simple prompt for quick update - would be a modal in real app
            const newStock = prompt(`Update stock for Product #${productId}:`, currentStock);
            
            if (newStock !== null && !isNaN(newStock)) {
                // In a real app, this would make an AJAX call to update the stock
                console.log(`Updating stock for Product #${productId} to ${newStock}`);
                
                // Update the display (this is just for demo)
                const stockCell = this.closest('tr').querySelector('td:nth-child(6)');
                stockCell.textContent = newStock;
                
                // Update low stock warning if needed
                if (newStock <= 10) {
                    stockCell.innerHTML = `<span class="badge bg-warning text-dark">Low: ${newStock}</span>`;
                } else if (newStock <= 0) {
                    stockCell.innerHTML = `<span class="badge bg-danger">Out of Stock</span>`;
                }
            }
        });
    });
});
