document.addEventListener('DOMContentLoaded', function() {
    // Initialize calendar view if FullCalendar is loaded
    const calendarEl = document.getElementById('taskCalendar');
    if (calendarEl && typeof FullCalendar !== 'undefined') {
        const calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,listWeek'
            },
            events: '/api/tasks/calendar',
            eventTimeFormat: {
                hour: 'numeric',
                minute: '2-digit',
                meridiem: 'short'
            },
            eventClick: function(info) {
                // Show task details in a modal or redirect to task detail page
                const taskId = info.event.id;
                window.location.href = `/tasks/${taskId}/edit`;
            },
            eventDidMount: function(info) {
                // Add tooltip for tasks
                const taskTitle = info.event.title;
                const taskStatus = info.event.extendedProps.status;
                const taskPriority = info.event.extendedProps.priority;
                const taskType = info.event.extendedProps.type;
                
                const tooltip = `
                    <div>
                        <strong>${taskTitle}</strong><br>
                        Status: ${taskStatus}<br>
                        Priority: ${taskPriority}<br>
                        Type: ${taskType}
                    </div>
                `;
                
                new bootstrap.Tooltip(info.el, {
                    title: tooltip,
                    html: true,
                    placement: 'top',
                    container: 'body'
                });
            }
        });
        
        calendar.render();
    }
    
    // Handle task view toggle
    const viewToggleButtons = document.querySelectorAll('[data-task-view]');
    if (viewToggleButtons.length > 0) {
        viewToggleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const view = this.getAttribute('data-task-view');
                const url = new URL(window.location);
                url.searchParams.set('view', view);
                window.location.href = url.toString();
            });
        });
    }
    
    // Handle task status toggle
    const taskStatusToggles = document.querySelectorAll('.task-status-toggle');
    if (taskStatusToggles.length > 0) {
        taskStatusToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const taskId = this.getAttribute('data-task-id');
                const taskRow = document.getElementById(`task-${taskId}`);
                
                // Update task status via AJAX
                toggleTaskStatus(taskId, function(success, newStatus) {
                    if (success) {
                        // Update UI
                        if (newStatus === 'Completed') {
                            toggle.classList.remove('btn-outline-secondary');
                            toggle.classList.add('btn-success');
                            toggle.innerHTML = '<i class="fas fa-check"></i>';
                            taskRow.classList.add('text-muted');
                        } else {
                            toggle.classList.remove('btn-success');
                            toggle.classList.add('btn-outline-secondary');
                            toggle.innerHTML = '<i class="fas fa-circle"></i>';
                            taskRow.classList.remove('text-muted');
                        }
                        
                        // Update status badge
                        const statusBadge = taskRow.querySelector('.status-badge');
                        if (statusBadge) {
                            statusBadge.textContent = newStatus;
                            statusBadge.className = 'badge status-badge';
                            statusBadge.classList.add(newStatus === 'Completed' ? 'bg-success' : 'bg-primary');
                        }
                        
                        // Show toast notification
                        showToast(`Task marked as ${newStatus}`);
                    }
                });
            });
        });
    }
    
    // Function to toggle task status via AJAX
    function toggleTaskStatus(taskId, callback) {
        fetch(`/tasks/${taskId}/toggle-status`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            callback(data.success, data.status);
        })
        .catch(error => {
            console.error('Error toggling task status:', error);
            callback(false);
        });
    }
    
    // Initialize task form validation
    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        taskForm.addEventListener('submit', function(event) {
            if (!taskForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            taskForm.classList.add('was-validated');
        });
    }
    
    // Handle filter functionality
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const form = document.getElementById('taskFilterForm');
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
    
    // Handle delete task
    const deleteButtons = document.querySelectorAll('[data-action="delete-task"]');
    if (deleteButtons.length > 0) {
        deleteButtons.forEach(button => {
            button.addEventListener('click', function() {
                const taskId = this.getAttribute('data-id');
                const taskTitle = this.getAttribute('data-title');
                
                if (confirm(`Are you sure you want to delete task "${taskTitle}"? This action cannot be undone.`)) {
                    const form = document.getElementById('deleteTaskForm');
                    form.action = `/tasks/${taskId}/delete`;
                    form.submit();
                }
            });
        });
    }
});
