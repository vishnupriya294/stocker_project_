// Stocker Platform JavaScript
class StockerApp {
    constructor() {
        this.updateInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.startLiveUpdates();
        this.initializeQuantityControls();
    }

    bindEvents() {
        // Navigation
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                navLinks.forEach(l => l.classList.remove('active'));
                e.target.classList.add('active');
            });
        });

        // Stock card clicks
        const stockCards = document.querySelectorAll('.stock-card');
        stockCards.forEach(card => {
            card.addEventListener('click', () => {
                const symbol = card.dataset.symbol;
                if (symbol) {
                    window.location.href = `/trade/${symbol}`;
                }
            });
        });

        // Form validations
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', this.validateForm);
        });

        // Trade form enhancements
        this.enhanceTradeForm();
    }

    startLiveUpdates() {
        if (document.querySelector('.stock-card') || document.querySelector('.portfolio-item')) {
            this.updateStockPrices();
            this.updateInterval = setInterval(() => {
                this.updateStockPrices();
            }, 5000); // Update every 5 seconds
        }
    }

    async updateStockPrices() {
        try {
            const response = await fetch('/api/stocks');
            const stocks = await response.json();
            
            this.updateStockCards(stocks);
            this.updatePortfolio(stocks);
            this.updateDashboardStats(stocks);
        } catch (error) {
            console.error('Failed to update stock prices:', error);
        }
    }

    updateStockCards(stocks) {
        Object.entries(stocks).forEach(([symbol, data]) => {
            const card = document.querySelector(`[data-symbol="${symbol}"]`);
            if (card) {
                const priceElement = card.querySelector('.stock-price');
                const changeElement = card.querySelector('.stock-change');
                
                if (priceElement) {
                    const oldPrice = parseFloat(priceElement.textContent.replace('$', ''));
                    const newPrice = data.price;
                    
                    priceElement.textContent = `$${newPrice.toFixed(2)}`;
                    
                    // Add flash effect for price changes
                    if (Math.abs(oldPrice - newPrice) > 0.01) {
                        this.flashElement(priceElement, newPrice > oldPrice ? 'success' : 'danger');
                    }
                }
                
                if (changeElement) {
                    const change = data.change;
                    changeElement.textContent = `${change >= 0 ? '+' : ''}$${change.toFixed(2)}`;
                    changeElement.className = `stock-change ${change >= 0 ? 'positive' : 'negative'}`;
                }
            }
        });
    }

    updatePortfolio(stocks) {
        const portfolioItems = document.querySelectorAll('.portfolio-item');
        portfolioItems.forEach(item => {
            const symbol = item.dataset.symbol;
            if (symbol && stocks[symbol]) {
                const currentPriceElement = item.querySelector('.portfolio-price');
                const changeElement = item.querySelector('.portfolio-change');
                
                if (currentPriceElement) {
                    const quantity = parseInt(item.dataset.quantity);
                    const avgPrice = parseFloat(item.dataset.avgPrice);
                    const currentPrice = stocks[symbol].price;
                    const totalValue = quantity * currentPrice;
                    const gainLoss = (currentPrice - avgPrice) * quantity;
                    
                    currentPriceElement.textContent = `$${totalValue.toFixed(2)}`;
                    
                    if (changeElement) {
                        changeElement.textContent = `${gainLoss >= 0 ? '+' : ''}$${gainLoss.toFixed(2)}`;
                        changeElement.className = `portfolio-change ${gainLoss >= 0 ? 'text-success' : 'text-danger'}`;
                    }
                }
            }
        });
    }

    updateDashboardStats(stocks) {
        // Update portfolio value if on dashboard
        if (window.location.pathname === '/dashboard') {
            this.updatePortfolioValue();
        }
    }

    async updatePortfolioValue() {
        const userId = document.body.dataset.userId;
        if (!userId) return;

        try {
            const response = await fetch(`/api/portfolio/${userId}`);
            const data = await response.json();
            
            const portfolioValueElement = document.querySelector('#portfolio-value');
            if (portfolioValueElement && data.portfolio_value !== undefined) {
                portfolioValueElement.textContent = `$${data.portfolio_value.toFixed(2)}`;
            }
        } catch (error) {
            console.error('Failed to update portfolio value:', error);
        }
    }

    flashElement(element, type) {
        element.classList.add(`flash-${type}`);
        setTimeout(() => {
            element.classList.remove(`flash-${type}`);
        }, 1000);
    }

    enhanceTradeForm() {
        const tradeForm = document.querySelector('.trade-form');
        if (!tradeForm) return;

        const quantityInput = tradeForm.querySelector('input[name="quantity"]');
        const priceElement = tradeForm.querySelector('.stock-price');
        const totalElement = tradeForm.querySelector('#total-cost');
        const actionSelect = tradeForm.querySelector('select[name="action"]');

        if (quantityInput && priceElement && totalElement) {
            const updateTotal = () => {
                const quantity = parseInt(quantityInput.value) || 0;
                const price = parseFloat(priceElement.textContent.replace('$', '')) || 0;
                const total = quantity * price;
                totalElement.textContent = `$${total.toFixed(2)}`;
            };

            quantityInput.addEventListener('input', updateTotal);
            updateTotal(); // Initial calculation
        }

        // Add confirmation for large trades
        tradeForm.addEventListener('submit', (e) => {
            const quantity = parseInt(quantityInput?.value) || 0;
            const price = parseFloat(priceElement?.textContent.replace('$', '')) || 0;
            const total = quantity * price;

            if (total > 10000) { // Large trade threshold
                if (!confirm(`This is a large trade worth $${total.toFixed(2)}. Are you sure you want to proceed?`)) {
                    e.preventDefault();
                }
            }
        });
    }

    initializeQuantityControls() {
        const quantityControls = document.querySelectorAll('.quantity-input');
        quantityControls.forEach(control => {
            const input = control.querySelector('input[name="quantity"]');
            const decreaseBtn = control.querySelector('.quantity-btn[data-action="decrease"]');
            const increaseBtn = control.querySelector('.quantity-btn[data-action="increase"]');

            if (decreaseBtn) {
                decreaseBtn.addEventListener('click', () => {
                    const currentValue = parseInt(input.value) || 0;
                    if (currentValue > 1) {
                        input.value = currentValue - 1;
                        input.dispatchEvent(new Event('input'));
                    }
                });
            }

            if (increaseBtn) {
                increaseBtn.addEventListener('click', () => {
                    const currentValue = parseInt(input.value) || 0;
                    input.value = currentValue + 1;
                    input.dispatchEvent(new Event('input'));
                });
            }
        });
    }

    validateForm(e) {
        const form = e.target;
        const inputs = form.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        });

        if (!isValid) {
            e.preventDefault();
            this.showNotification('Please fill in all required fields', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);

        // Add click to dismiss
        notification.addEventListener('click', () => {
            notification.remove();
        });
    }

    // Admin functions
    initializeAdminFeatures() {
        this.bindAdminActions();
    }

    bindAdminActions() {
        // User management actions
        const userActions = document.querySelectorAll('.user-action');
        userActions.forEach(action => {
            action.addEventListener('click', (e) => {
                const actionType = e.target.dataset.action;
                const userId = e.target.dataset.userId;
                
                if (actionType === 'delete') {
                    if (confirm('Are you sure you want to delete this user?')) {
                        this.deleteUser(userId);
                    }
                } else if (actionType === 'suspend') {
                    this.suspendUser(userId);
                }
            });
        });
    }

    async deleteUser(userId) {
        try {
            const response = await fetch(`/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.showNotification('User deleted successfully', 'success');
                location.reload();
            } else {
                throw new Error('Failed to delete user');
            }
        } catch (error) {
            this.showNotification('Failed to delete user', 'error');
        }
    }

    async suspendUser(userId) {
        try {
            const response = await fetch(`/admin/users/${userId}/suspend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                this.showNotification('User suspended successfully', 'success');
                location.reload();
            } else {
                throw new Error('Failed to suspend user');
            }
        } catch (error) {
            this.showNotification('Failed to suspend user', 'error');
        }
    }

    // Utility functions
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    formatPercentage(value) {
        return `${(value * 100).toFixed(2)}%`;
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Cleanup
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.stockerApp = new StockerApp();
    
    // Initialize admin features if on admin page
    if (document.body.classList.contains('admin-page')) {
        window.stockerApp.initializeAdminFeatures();
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Pause updates when page is hidden
        if (window.stockerApp && window.stockerApp.updateInterval) {
            clearInterval(window.stockerApp.updateInterval);
        }
    } else {
        // Resume updates when page is visible
        if (window.stockerApp) {
            window.stockerApp.startLiveUpdates();
        }
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.stockerApp) {
        window.stockerApp.destroy();
    }
});

// Add CSS for notifications and flash effects
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        color: white;
        font-weight: 500;
        z-index: 1000;
        cursor: pointer;
        animation: slideInRight 0.3s ease-out;
    }
    
    .notification-success {
        background: var(--success-color);
    }
    
    .notification-error {
        background: var(--danger-color);
    }
    
    .notification-info {
        background: var(--accent-color);
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .flash-success {
        animation: flashGreen 1s ease-out;
    }
    
    .flash-danger {
        animation: flashRed 1s ease-out;
    }
    
    @keyframes flashGreen {
        0%, 100% { background-color: transparent; }
        50% { background-color: rgba(34, 197, 94, 0.2); }
    }
    
    @keyframes flashRed {
        0%, 100% { background-color: transparent; }
        50% { background-color: rgba(239, 68, 68, 0.2); }
    }
    
    input.error {
        border-color: var(--danger-color);
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
`;
document.head.appendChild(style);