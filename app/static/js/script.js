let selectedItems = [];
let selectionOptions = [];

// Generate unique Patient ID if not present
document.addEventListener('DOMContentLoaded', function() {
    const patientIdField = document.getElementById('patient_id');
    if (!patientIdField.value) {
        patientIdField.value = 'PT' + Math.random().toString(36).substr(2, 6).toUpperCase();
    }
});

// Handle form submissions with loading states
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Processing...';
        }
    });
});