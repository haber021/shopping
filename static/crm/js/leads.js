document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop for kanban
    const leadCards = document.querySelectorAll('.lead-card');
    const stageColumns = document.querySelectorAll('.stage-column');
    
    if (leadCards.length > 0 && stageColumns.length > 0) {
        leadCards.forEach(card => {
            card.setAttribute('draggable', true);
            
            card.addEventListener('dragstart', function(e) {
                e.dataTransfer.setData('text/plain', card.id);
                card.classList.add('dragging');
            });
            
            card.addEventListener('dragend', function() {
                card.classList.remove('dragging');
            });
        });
        
        stageColumns.forEach(column => {
            column.addEventListener('dragover', function(e) {
                e.preventDefault();
                column.classList.add('drag-over');
            });
            
            column.addEventListener('dragleave', function() {
                column.classList.remove('drag-over');
            });
            
            column.addEventListener('drop', function(e) {
                e.preventDefault();
                column.classList.remove('drag-over');
                
                const leadId = e.dataTransfer.getData('text/plain');
                const leadCard = document.getElementById(leadId);
                const newStage = column.getAttribute('data-stage');
                const oldStage = leadCard.getAttribute('data-stage');
                
                if (newStage !== oldStage) {
                    // Update lead stage via AJAX
                    updateLeadStage(leadId.replace('lead-', ''), newStage, function(success) {
                        if (success) {
                            // Update UI
                            const stageContent = column.querySelector('.stage-content');
                            stageContent.appendChild(leadCard);
                            leadCard.setAttribute('data-stage', newStage);
                            
                            // Update card style based on stage
                            leadCard.className = 'card lead-card mb-2';
                            if (newStage === 'Closed-Won') {
                                leadCard.classList.add('border-success');
                            } else if (newStage === 'Closed-Lost') {
                                leadCard.classList.add('border-danger');
                            } else {
                                leadCard.classList.add('border-primary');
                            }
                            
                            // Show toast notification
                            showToast(`Lead moved to ${newStage} stage`);
                        }
                    });
                }
            });
        });
    }
    
    // Function to update lead stage via AJAX
    function updateLeadStage(leadId, newStage, callback) {
        const formData = new FormData();
        formData.append('stage', newStage);
        
        fetch(`/leads/${leadId}/update-stage`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            callback(data.success);
        })
        .catch(error => {
            console.error('Error updating lead stage:', error);
            callback(false);
        });
    }
    
    // Initialize add/edit lead modal
    const leadForm = document.getElementById('leadForm');
    if (leadForm) {
        leadForm.addEventListener('submit', function(event) {
            if (!leadForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            leadForm.classList.add('was-validated');
        });
    }
    
    // Handle filter functionality
    const stageFilter = document.getElementById('stageFilter');
    if (stageFilter) {
        stageFilter.addEventListener('change', function() {
            const form = document.getElementById('leadFilterForm');
            form.submit();
        });
    }
    
    // Function to show toast notification
    function showToast(message) {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;
        
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 3000
        });
        
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }
    
    // Handle delete lead
    const deleteButtons = document.querySelectorAll('[data-action="delete-lead"]');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const leadId = this.getAttribute('data-id');
                const leadTitle = this.getAttribute('data-title');
                
                if (confirm(`Are you sure you want to delete lead "${leadTitle}"? This action cannot be undone.`)) {
                    const form = document.getElementById('deleteLeadForm');
                    form.action = `/leads/${leadId}/delete`;
                    form.submit();
                }
            });
        });
    }
});
