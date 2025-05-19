document.addEventListener('DOMContentLoaded', function() {
    /**
     * Initialize tooltips
     */
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    /**
     * Toggle sidebar on small screens
     */
    const toggleSidebarBtn = document.getElementById('sidebarToggle');
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('d-none');
        });
    }

    /**
     * Handle form submissions with AJAX where needed
     */
    const ajaxForms = document.querySelectorAll('form.ajax-form');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = this.getAttribute('action');
            const method = this.getAttribute('method') || 'post';
            const formData = new FormData(this);
            
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    if (data.message) {
                        showAlert(data.message, 'success');
                    }
                    
                    // Redirect if needed
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                    
                    // Reset form if needed
                    if (data.reset_form) {
                        form.reset();
                    }
                    
                    // Refresh page if needed
                    if (data.refresh) {
                        window.location.reload();
                    }
                } else {
                    // Show error message
                    if (data.message) {
                        showAlert(data.message, 'danger');
                    }
                    
                    // Show field errors
                    if (data.errors) {
                        for (const field in data.errors) {
                            const errorElement = document.getElementById(`error-${field}`);
                            if (errorElement) {
                                errorElement.textContent = data.errors[field];
                                errorElement.classList.remove('d-none');
                            }
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred. Please try again.', 'danger');
            });
        });
    });

    /**
     * Show an alert message
     */
    function showAlert(message, type = 'info') {
        const alertPlaceholder = document.getElementById('alert-placeholder');
        if (!alertPlaceholder) return;
        
        const wrapper = document.createElement('div');
        wrapper.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertPlaceholder.appendChild(wrapper);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = wrapper.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }

    /**
     * Date range picker initialization
     */
    const dateRangePickers = document.querySelectorAll('.date-range-picker');
    if (dateRangePickers.length > 0) {
        dateRangePickers.forEach(picker => {
            // Initialize date range picker here if you have a library
            // This is just a placeholder
            console.log('Date range picker initialized');
        });
    }

    /**
     * Data table search functionality
     */
    const dataTableSearchInputs = document.querySelectorAll('.datatable-search');
    dataTableSearchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);
            if (!table) return;
            
            const searchText = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const display = text.includes(searchText) ? '' : 'none';
                row.style.display = display;
            });
        });
    });

    /**
     * Handle delete confirmations
     */
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
});
