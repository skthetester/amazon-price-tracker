// Amazon Price Tracker - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh functionality
    const autoRefreshCheckbox = document.getElementById('auto-refresh');
    let refreshInterval;

    if (autoRefreshCheckbox) {
        autoRefreshCheckbox.addEventListener('change', function() {
            if (this.checked) {
                // Refresh every 5 minutes
                refreshInterval = setInterval(() => {
                    location.reload();
                }, 300000);
                console.log('Auto-refresh enabled');
            } else {
                clearInterval(refreshInterval);
                console.log('Auto-refresh disabled');
            }
        });
    }

    // Form validation
    const productForm = document.getElementById('add-product-form');
    if (productForm) {
        productForm.addEventListener('submit', function(e) {
            const url = document.getElementById('amazon_url').value;
            
            // Basic Amazon URL validation
            if (!url.includes('amazon.com') || (!url.includes('/dp/') && !url.includes('/gp/product/'))) {
                e.preventDefault();
                alert('Please enter a valid Amazon product URL');
                return false;
            }
        });
    }

    // Price update animation
    const priceElements = document.querySelectorAll('.price-updated');
    priceElements.forEach(element => {
        element.classList.add('price-updated');
        setTimeout(() => {
            element.classList.remove('price-updated');
        }, 2000);
    });

    // Copy ASIN functionality
    const copyButtons = document.querySelectorAll('.copy-asin');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const asin = this.dataset.asin;
            navigator.clipboard.writeText(asin).then(() => {
                // Show success feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 1500);
            });
        });
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.confirm-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const productName = this.dataset.productName || 'this product';
            if (!confirm(`Are you sure you want to delete "${productName}"?`)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Loading states for buttons
    const loadingButtons = document.querySelectorAll('.btn-loading');
    loadingButtons.forEach(button => {
        button.addEventListener('click', function() {
            const originalHTML = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            this.disabled = true;
            
            // Re-enable after 5 seconds (fallback)
            setTimeout(() => {
                this.innerHTML = originalHTML;
                this.disabled = false;
            }, 5000);
        });
    });
});

// Utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'America/New_York'  // EST/EDT
    }) + ' EST';
}

// Price change indicator
function getPriceChangeClass(oldPrice, newPrice) {
    if (newPrice > oldPrice) return 'text-danger';
    if (newPrice < oldPrice) return 'text-success';
    return 'text-muted';
}

// Chart themes
const chartTheme = {
    layout: {
        font: { family: 'Segoe UI, sans-serif' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        colorway: ['#0d6efd', '#198754', '#dc3545', '#ffc107']
    }
};
