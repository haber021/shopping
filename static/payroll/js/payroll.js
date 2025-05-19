/**
 * Payroll.js - Payroll functionality for RetailPay System
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
        return new Intl.NumberFormat('en-PH', { 
            style: 'currency', 
            currency: 'PHP',
            minimumFractionDigits: 2
        }).format(amount);
    }

    // Employee filters functionality
    const employeeFilters = document.querySelector('form[action*="employee_list"]');
    if (employeeFilters) {
        // Add event listener to reset button
        const resetButton = employeeFilters.querySelector('a.btn-outline-secondary');
        if (resetButton) {
            resetButton.addEventListener('click', function(e) {
                // Reset all form fields
                employeeFilters.querySelectorAll('select, input').forEach(field => {
                    field.value = field.tagName === 'SELECT' && field.name === 'status' ? 'active' : '';
                });
                
                // Submit the form
                employeeFilters.submit();
                e.preventDefault();
            });
        }
    }

    // Handling pay head assignment form
    const payHeadForm = document.querySelector('form[name="add_pay_head"]');
    if (payHeadForm) {
        const payHeadSelect = payHeadForm.querySelector('select[name="pay_head"]');
        const amountInput = payHeadForm.querySelector('input[name="amount"]');
        
        payHeadSelect?.addEventListener('change', function() {
            // In a real app, we might pre-fill suggested amounts based on the selected pay head
            // For now, just ensure the amount field is enabled when a pay head is selected
            if (this.value) {
                amountInput.disabled = false;
            } else {
                amountInput.disabled = true;
                amountInput.value = '';
            }
        });
    }

    // Salary Slip PDF Generation
    const pdfButton = document.querySelector('a[href*="format=pdf"]');
    if (pdfButton) {
        pdfButton.addEventListener('click', function() {
            // Show loading indicator
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Generating...';
            
            // The actual download will happen via the href link
            // This is just visual feedback
            setTimeout(() => {
                this.innerHTML = originalText;
            }, 1500);
        });
    }

    // Handling date validations for payroll run
    const payrollForm = document.querySelector('form[action*="run-payroll"]');
    if (payrollForm) {
        const startDateInput = payrollForm.querySelector('input[name="start_date"]');
        const endDateInput = payrollForm.querySelector('input[name="end_date"]');
        
        if (startDateInput && endDateInput) {
            // Ensure end date is after start date
            endDateInput.addEventListener('change', function() {
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(this.value);
                
                if (endDate <= startDate) {
                    alert('End date must be after start date');
                    this.value = '';
                }
            });
            
            // Auto-generate description when dates change
            function updateDescription() {
                const descInput = payrollForm.querySelector('input[name="description"]');
                if (!descInput || descInput.value.trim() !== '') return;
                
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(endDateInput.value);
                
                if (isNaN(startDate.getTime()) || isNaN(endDate.getTime())) return;
                
                const monthNames = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"];
                
                // If dates span a single month
                if (startDate.getMonth() === endDate.getMonth() && startDate.getFullYear() === endDate.getFullYear()) {
                    descInput.value = `Monthly Payroll - ${monthNames[startDate.getMonth()]} ${startDate.getFullYear()}`;
                } else {
                    descInput.value = `Payroll ${startDate.getDate()} ${monthNames[startDate.getMonth()]} - ${endDate.getDate()} ${monthNames[endDate.getMonth()]} ${endDate.getFullYear()}`;
                }
            }
            
            startDateInput.addEventListener('change', updateDescription);
            endDateInput.addEventListener('change', updateDescription);
        }
    }

    // Employee detail page pay heads editing
    const payHeadRows = document.querySelectorAll('table tbody tr[data-pay-head-id]');
    payHeadRows.forEach(row => {
        const editBtn = row.querySelector('.btn-outline-primary');
        const deleteBtn = row.querySelector('.btn-outline-danger');
        
        if (editBtn) {
            editBtn.addEventListener('click', function() {
                const payHeadId = row.dataset.payHeadId;
                const payHeadName = row.querySelector('td:first-child').textContent;
                const currentAmount = row.querySelector('td:nth-child(3)').textContent.replace(/[^0-9.]/g, '');
                
                // This would normally open a modal or inline edit
                // For simplicity, we'll use a prompt
                const newAmount = prompt(`Update amount for ${payHeadName}:`, currentAmount);
                
                if (newAmount !== null && !isNaN(newAmount) && newAmount > 0) {
                    // In a real app, this would make an AJAX call to update the amount
                    console.log(`Updating pay head ${payHeadId} to amount ${newAmount}`);
                    
                    // Update the display (this is just for demo)
                    row.querySelector('td:nth-child(3)').textContent = formatCurrency(parseFloat(newAmount));
                }
            });
        }
        
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                const payHeadName = row.querySelector('td:first-child').textContent;
                
                if (confirm(`Are you sure you want to remove ${payHeadName}?`)) {
                    // In a real app, this would make an AJAX call to delete the pay head
                    console.log(`Removing pay head ${row.dataset.payHeadId}`);
                    
                    // Remove the row (this is just for demo)
                    row.remove();
                }
            });
        }
    });
});
