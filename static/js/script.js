// Custom JavaScript for Assignment Management System

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancements
    enhanceFormValidation();
    
    // File upload preview
    setupFileUploadPreview();
    
    // Search functionality
    setupSearch();
    
    // Filter functionality
    setupFilters();
});

// Form validation enhancements
function enhanceFormValidation() {
    var forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Add loading state to submit button
            var submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable after 3 seconds (in case of errors)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
        
        // Store original button text
        var submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.getAttribute('data-original-text')) {
            submitBtn.setAttribute('data-original-text', submitBtn.innerHTML);
        }
    });
}

// File upload preview
function setupFileUploadPreview() {
    var fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(event) {
            var file = event.target.files[0];
            if (file) {
                var fileName = file.name;
                var fileSize = (file.size / 1024 / 1024).toFixed(2) + ' MB';
                
                // Create or update file info display
                var fileInfoId = input.id + '_info';
                var fileInfo = document.getElementById(fileInfoId);
                
                if (!fileInfo) {
                    fileInfo = document.createElement('div');
                    fileInfo.id = fileInfoId;
                    fileInfo.className = 'alert alert-info mt-2';
                    input.parentNode.appendChild(fileInfo);
                }
                
                fileInfo.innerHTML = `
                    <i class="fas fa-file me-2"></i>
                    <strong>${fileName}</strong> (${fileSize})
                    <button type="button" class="btn-close float-end" onclick="clearFileInput('${input.id}')"></button>
                `;
                
                // Check file size (16MB limit)
                if (file.size > 16 * 1024 * 1024) {
                    fileInfo.className = 'alert alert-danger mt-2';
                    fileInfo.innerHTML += '<br><small class="text-danger">File size exceeds 16MB limit</small>';
                    input.value = '';
                }
            }
        });
    });
}

// Clear file input
function clearFileInput(inputId) {
    var input = document.getElementById(inputId);
    if (input) {
        input.value = '';
        var fileInfo = document.getElementById(inputId + '_info');
        if (fileInfo) {
            fileInfo.remove();
        }
    }
}

// Search functionality
function setupSearch() {
    var searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function(event) {
            var searchTerm = event.target.value.toLowerCase();
            var tableRows = document.querySelectorAll('.table tbody tr');
            
            tableRows.forEach(function(row) {
                var text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// Filter functionality
function setupFilters() {
    var filterSelects = document.querySelectorAll('.filter-select');
    
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function(event) {
            var filterValue = event.target.value;
            var filterType = event.target.getAttribute('data-filter-type');
            var tableRows = document.querySelectorAll('.table tbody tr');
            
            tableRows.forEach(function(row) {
                var shouldShow = true;
                
                if (filterType === 'status') {
                    var statusBadge = row.querySelector('.badge');
                    if (statusBadge) {
                        var status = statusBadge.textContent.toLowerCase();
                        if (filterValue !== 'all' && !status.includes(filterValue.toLowerCase())) {
                            shouldShow = false;
                        }
                    }
                } else if (filterType === 'subject') {
                    var subjectCell = row.cells[1]; // Assuming subject is in column 2
                    if (subjectCell) {
                        var subject = subjectCell.textContent.toLowerCase();
                        if (filterValue !== 'all' && !subject.includes(filterValue.toLowerCase())) {
                            shouldShow = false;
                        }
                    }
                }
                
                row.style.display = shouldShow ? '' : 'none';
            });
        });
    });
}

// Confirmation dialogs
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success');
    }).catch(function(err) {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    var notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(function() {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Format date/time
function formatDateTime(dateString) {
    var date = new Date(dateString);
    return date.toLocaleString();
}

// Time ago function
function timeAgo(dateString) {
    var date = new Date(dateString);
    var seconds = Math.floor((new Date() - date) / 1000);
    
    var interval = seconds / 31536000;
    if (interval > 1) {
        return Math.floor(interval) + " years ago";
    }
    
    interval = seconds / 2592000;
    if (interval > 1) {
        return Math.floor(interval) + " months ago";
    }
    
    interval = seconds / 86400;
    if (interval > 1) {
        return Math.floor(interval) + " days ago";
    }
    
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + " hours ago";
    }
    
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + " minutes ago";
    }
    
    return Math.floor(seconds) + " seconds ago";
}

// Export functions for use in templates
window.confirmAction = confirmAction;
window.copyToClipboard = copyToClipboard;
window.showNotification = showNotification;
window.formatDateTime = formatDateTime;
window.timeAgo = timeAgo;
window.clearFileInput = clearFileInput;
