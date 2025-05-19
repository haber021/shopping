document.addEventListener('DOMContentLoaded', function() {
    // Handle search functionality
    const searchForm = document.getElementById('contactSearchForm');
    const searchInput = document.getElementById('contactSearch');
    const clearSearchBtn = document.getElementById('clearSearch');
    
    if (searchForm && clearSearchBtn) {
        clearSearchBtn.addEventListener('click', function() {
            searchInput.value = '';
            searchForm.submit();
        });
    }
    
    // Handle sort functionality
    const sortOptions = document.querySelectorAll('.sort-option');
    if (sortOptions.length > 0) {
        sortOptions.forEach(option => {
            option.addEventListener('click', function() {
                const sortValue = this.getAttribute('data-sort');
                document.getElementById('sortField').value = sortValue;
                searchForm.submit();
            });
        });
    }
    
    // Handle tag filtering
    const tagFilters = document.querySelectorAll('.tag-filter');
    if (tagFilters.length > 0) {
        tagFilters.forEach(tag => {
            tag.addEventListener('click', function() {
                const tagValue = this.textContent.trim();
                searchInput.value = tagValue;
                searchForm.submit();
            });
        });
    }
    
    // Initialize contact form validation
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            if (!contactForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            contactForm.classList.add('was-validated');
        });
    }
    
    // Initialize delete confirmation
    const deleteButtons = document.querySelectorAll('[data-action="delete-contact"]');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const contactId = this.getAttribute('data-id');
                const contactName = this.getAttribute('data-name');
                
                if (confirm(`Are you sure you want to delete contact "${contactName}"? This action cannot be undone.`)) {
                    const form = document.getElementById('deleteContactForm');
                    form.action = `/contacts/${contactId}/delete`;
                    form.submit();
                }
            });
        });
    }
});
