/**
 * SMARTCROP - MAIN JAVASCRIPT
 */

// Utility Functions
const CropApp = {
    // Initialize
    init: function() {
        console.log('Crop Recommendation App Initialized');
        this.setupEventListeners();
        this.initAnimations();
    },

    // Event Listeners
    setupEventListeners: function() {
        // Auto-dismiss alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });

        // Form validation
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });

        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    },

    // Animations
    initAnimations: function() {
        // Fade in elements on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.card, .crop-badge').forEach(el => {
            observer.observe(el);
        });
    },

    // API Call Helper
    makeAPICall: async function(endpoint, data = null, method = 'GET') {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(endpoint, options);
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Show loading
    showLoading: function(element) {
        element.innerHTML = '<div class="text-center"><div class="spinner-border text-success" role="status"><span class="visually-hidden">Loading...</span></div></div>';
    },

    // Format number
    formatNumber: function(num, decimals = 2) {
        return Number(num).toFixed(decimals);
    },

    // Format percentage
    formatPercentage: function(num, decimals = 2) {
        return this.formatNumber(num * 100, decimals) + '%';
    }
};

// Prediction Form Handler
const PredictionForm = {
    init: function() {
        const form = document.getElementById('predictionForm');
        if (form) {
            this.setupRangeInputs();
            this.setupSubmit(form);
        }
    },

    setupRangeInputs: function() {
        // Add range sliders (optional enhancement)
        const numInputs = document.querySelectorAll('input[type="number"]');
        numInputs.forEach(input => {
            input.addEventListener('input', function() {
                const value = parseFloat(this.value);
                const min = parseFloat(this.min);
                const max = parseFloat(this.max);

                if (value < min) this.value = min;
                if (value > max) this.value = max;
            });
        });
    },

    setupSubmit: function(form) {
        form.addEventListener('submit', function(e) {
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Prédiction en cours...';

            // Re-enable after form processes
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }, 3000);
        });
    }
};

// Dashboard Charts Handler
const DashboardCharts = {
    init: function() {
        // Charts are initialized in the dashboard.html template
        // This is a placeholder for additional chart functionality
    },

    updateChart: function(chartId, newData) {
        const chart = Chart.getChart(chartId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }
};

// Dashboard Chart Rendering
function renderDashboardCharts() {
    var cropData = window.smartCropData || {};
    var cropDistCanvas = document.getElementById('cropDistributionChart');
    if (cropDistCanvas && Object.keys(cropData).length > 0) {
        var ctx1 = cropDistCanvas.getContext('2d');
        new Chart(ctx1, {
            type: 'pie',
            data: {
                labels: Object.keys(cropData),
                datasets: [{
                    data: Object.values(cropData),
                    backgroundColor: [
                        '#198754', '#20c997', '#0dcaf0', '#0d6efd', '#6610f2',
                        '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    var topCropsCanvas = document.getElementById('topCropsChart');
    if (topCropsCanvas && Object.keys(cropData).length > 0) {
        var sortedCrops = Object.entries(cropData)
            .sort(function(a, b) { return b[1] - a[1]; })
            .slice(0, 5);
        var ctx2 = topCropsCanvas.getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: sortedCrops.map(function(x) { return x[0]; }),
                datasets: [{
                    label: 'Number of predictions',
                    data: sortedCrops.map(function(x) { return x[1]; }),
                    backgroundColor: '#198754'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    renderDashboardCharts();
});

// Auto-refresh for real-time updates (optional)
const AutoRefresh = {
    interval: null,

    start: function(callback, seconds = 30) {
        this.interval = setInterval(callback, seconds * 1000);
    },

    stop: function() {
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }
};

// Export to CSV (for history page)
const ExportData = {
    toCSV: function(data, filename = 'predictions.csv') {
        const csv = this.convertToCSV(data);
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', filename);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    },

    convertToCSV: function(data) {
        if (!data || !data.length) return '';
        
        const headers = Object.keys(data[0]);
        const csvRows = [headers.join(',')];
        
        data.forEach(row => {
            const values = headers.map(header => {
                const escaped = ('' + row[header]).replace(/"/g, '\\"');
                return `"${escaped}"`;
            });
            csvRows.push(values.join(','));
        });
        
        return csvRows.join('\n');
    }
};

// Notification System
const Notifications = {
    show: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    },

    success: function(message) {
        this.show(message, 'success');
    },

    error: function(message) {
        this.show(message, 'danger');
    },

    warning: function(message) {
        this.show(message, 'warning');
    },

    info: function(message) {
        this.show(message, 'info');
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    CropApp.init();
    PredictionForm.init();
    DashboardCharts.init();
    
    console.log('All modules initialized');
});

// Make utilities available globally
window.CropApp = CropApp;
window.Notifications = Notifications;
window.ExportData = ExportData;
