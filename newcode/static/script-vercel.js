// Price Extractor Machine - Serverless Version
class PriceExtractor {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.extractionInProgress = false;
        this.results = [];
    }

    initializeElements() {
        this.urlInput = document.getElementById('urlInput');
        this.urlCount = document.getElementById('urlCount');
        this.extractBtn = document.getElementById('extractBtn');
        this.progressSection = document.getElementById('progressSection');
        this.progressText = document.getElementById('progressText');
        this.progressFill = document.getElementById('progressFill');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContainer = document.getElementById('resultsContainer');
        this.successCount = document.getElementById('successCount');
        this.failedCount = document.getElementById('failedCount');
        this.exportBtn = document.getElementById('exportBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.loadingOverlay = document.getElementById('loadingOverlay');
    }

    bindEvents() {
        this.urlInput.addEventListener('input', () => this.updateUrlCount());
        this.extractBtn.addEventListener('click', () => this.startExtraction());
        this.exportBtn.addEventListener('click', () => this.exportResults());
        this.clearBtn.addEventListener('click', () => this.clearResults());

        // Update URL count on page load
        this.updateUrlCount();
    }

    updateUrlCount() {
        const urls = this.getUrls();
        this.urlCount.textContent = urls.length;

        // Enable/disable extract button
        this.extractBtn.disabled = urls.length === 0 || this.extractionInProgress;

        // Show warning for too many URLs
        if (urls.length > 10) {
            this.showNotification('Maximum 10 URLs allowed per request', 'warning');
        }
    }

    getUrls() {
        const text = this.urlInput.value.trim();
        if (!text) return [];

        return text.split('\n')
            .map(url => url.trim())
            .filter(url => url && this.isValidUrl(url));
    }

    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    async startExtraction() {
        const urls = this.getUrls();

        if (urls.length === 0) {
            this.showNotification('Please enter at least one valid URL', 'error');
            return;
        }

        // Limit URLs for serverless constraints
        if (urls.length > 10) {
            this.showNotification('Maximum 10 URLs allowed per request', 'error');
            return;
        }

        this.extractionInProgress = true;
        this.updateUrlCount();
        this.showLoadingOverlay('Processing extraction...');
        this.showProgressSection();
        this.hideResultsSection();

        // Simulate progress
        this.simulateProgress(urls.length);

        try {
            // Direct extraction call for serverless
            const response = await fetch('/api/extract', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urls })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.results = data.results || [];

            this.extractionInProgress = false;
            this.updateUrlCount();
            this.hideLoadingOverlay();
            this.hideProgressSection();
            this.showResults();
            this.showNotification(`Extraction completed! ${data.successful} successful, ${data.failed} failed`, 'success');

        } catch (error) {
            console.error('Error during extraction:', error);
            this.extractionInProgress = false;
            this.updateUrlCount();
            this.hideLoadingOverlay();
            this.hideProgressSection();
            this.showNotification(`Failed to extract prices: ${error.message}`, 'error');
        }
    }

    simulateProgress(totalUrls) {
        let current = 0;
        const interval = setInterval(() => {
            if (current < totalUrls && this.extractionInProgress) {
                current++;
                const percentage = (current / totalUrls) * 100;
                this.progressFill.style.width = `${percentage}%`;
                this.progressText.textContent = `Processing ${current} of ${totalUrls} URLs...`;
            } else {
                clearInterval(interval);
            }
        }, 1000);
    }

    showResults() {
        this.resultsSection.style.display = 'block';
        this.updateResultsSummary();
        this.renderResults();
    }

    updateResultsSummary() {
        const successful = this.results.filter(r => r.status === 'success').length;
        const failed = this.results.filter(r => r.status === 'error').length;

        this.successCount.textContent = `${successful} successful`;
        this.failedCount.textContent = `${failed} failed`;
    }

    renderResults() {
        this.resultsContainer.innerHTML = '';

        this.results.forEach((result, index) => {
            const resultElement = this.createResultElement(result, index);
            this.resultsContainer.appendChild(resultElement);
        });
    }

    createResultElement(result, index) {
        const div = document.createElement('div');
        div.className = `result-item ${result.status === 'success' ? 'success' : result.status === 'error' ? 'error' : 'no-price'}`;

        const statusIcon = result.status === 'success' ? 'fa-check-circle' :
            result.status === 'error' ? 'fa-times-circle' : 'fa-exclamation-triangle';

        const priceDisplay = result.price ? result.price :
            result.status === 'error' ? 'Error' : 'No price found';

        div.innerHTML = `
            <div class="result-header">
                <div class="result-url">${this.truncateUrl(result.url)}</div>
                <div class="result-price ${result.status}">${priceDisplay}</div>
            </div>
            <div class="result-status ${result.status}">
                <i class="fas ${statusIcon}"></i>
                ${result.status === 'success' ? 'Price extracted' :
                result.status === 'error' ? 'Extraction failed' : 'No price found'}
            </div>
            ${result.error ? `<div class="result-error">Error: ${result.error}</div>` : ''}
        `;

        return div;
    }

    truncateUrl(url, maxLength = 60) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength) + '...';
    }

    exportResults() {
        if (this.results.length === 0) {
            this.showNotification('No results to export', 'error');
            return;
        }

        const csvContent = this.generateCSV();
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);

        link.setAttribute('href', url);
        link.setAttribute('download', `price_extraction_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        this.showNotification('Results exported successfully!', 'success');
    }

    generateCSV() {
        const headers = ['URL', 'Price', 'Status', 'Error'];
        const rows = this.results.map(result => [
            `"${result.url}"`,
            `"${result.price || ''}"`,
            `"${result.status}"`,
            `"${result.error || ''}"`
        ]);

        return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    }

    clearResults() {
        this.results = [];
        this.hideResultsSection();
        this.hideProgressSection();
        this.urlInput.value = '';
        this.updateUrlCount();
        this.showNotification('Results cleared', 'success');
    }

    showProgressSection() {
        this.progressSection.style.display = 'block';
        this.progressFill.style.width = '0%';
    }

    hideProgressSection() {
        this.progressSection.style.display = 'none';
    }

    hideResultsSection() {
        this.resultsSection.style.display = 'none';
    }

    showLoadingOverlay(message) {
        this.loadingOverlay.querySelector('p').textContent = message;
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoadingOverlay() {
        this.loadingOverlay.style.display = 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${type === 'success' ? 'fa-check' : type === 'error' ? 'fa-times' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info'}"></i>
                <span>${message}</span>
            </div>
        `;

        // Add styles for notification
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6'
        };

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            color: white;
            font-weight: 500;
            z-index: 1001;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            background: ${colors[type] || colors.info};
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 400px;
        `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PriceExtractor();
});