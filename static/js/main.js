// Jewelry Inventory Management System - Custom JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add loading state to forms on submit
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            }
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm || 'Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Image preview for file inputs
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function (input) {
        input.addEventListener('change', function () {
            const preview = document.querySelector('#image-preview');
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[type="number"][name="quantity"]');
    quantityInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // Search form auto-submit on select change
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        const selectInputs = searchForm.querySelectorAll('select');
        selectInputs.forEach(function (select) {
            select.addEventListener('change', function () {
                searchForm.submit();
            });
        });
    }

    // Print report button
    const printBtn = document.querySelector('#print-report');
    if (printBtn) {
        printBtn.addEventListener('click', function () {
            window.print();
        });
    }
});
