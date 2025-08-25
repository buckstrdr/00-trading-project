/**
 * TSX Strategy Backtester - Frontend Logic
 * Handles form submission, API communication, and results display
 */

class BacktesterUI {
    constructor() {
        this.form = document.getElementById('backtest-form');
        this.runButton = document.getElementById('run-btn');
        this.btnText = document.getElementById('btn-text');
        this.btnSpinner = document.getElementById('btn-spinner');
        this.loadingSection = document.getElementById('loading');
        this.errorSection = document.getElementById('error');
        this.resultsSection = document.getElementById('results');
        this.progressFill = document.getElementById('progress-fill');
        this.progressPercent = document.getElementById('progress-percent');
        this.progressEta = document.getElementById('progress-eta');
        
        this.progressPollInterval = null;
        this.currentBacktestId = null;
        
        this.init();
    }
    
    init() {
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        console.log('[BacktesterUI] Initialized successfully');
    }
    
    async handleSubmit(event) {
        event.preventDefault();
        
        try {
            // Reset UI state
            this.resetUI();
            this.showLoading();
            
            // Get form data
            const formData = new FormData(this.form);
            const params = Object.fromEntries(formData.entries());
            
            console.log('[BacktesterUI] Starting backtest with params:', params);
            
            // Validate form
            this.validateForm(params);
            
            // Send request
            const response = await this.executeBacktest(params);
            
            // Handle response - threaded approach returns immediate success
            if (response.success) {
                console.log('[BacktesterUI] Backtest started successfully');
                // Start polling for results
                this.pollForResults(params);
            } else {
                throw new Error(response.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('[BacktesterUI] Backtest failed:', error);
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }
    
    validateForm(params) {
        // Validate required fields
        const requiredFields = ['symbol', 'strategy', 'start_date', 'end_date'];
        for (const field of requiredFields) {
            if (!params[field] || params[field].trim() === '') {
                throw new Error(`${field.replace('_', ' ')} is required`);
            }
        }
        
        // Validate date range
        const startDate = new Date(params.start_date);
        const endDate = new Date(params.end_date);
        
        if (endDate <= startDate) {
            throw new Error('End date must be after start date');
        }
        
        // Validate date range is not too large (prevent excessive requests)
        const daysDiff = (endDate - startDate) / (1000 * 60 * 60 * 24);
        if (daysDiff > 365) {
            throw new Error('Date range cannot exceed 1 year');
        }
    }
    
    async executeBacktest(params) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout
        
        try {
            const response = await fetch('/run-backtest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(params),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
            
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - backtest took too long (5 minute limit)');
            }
            
            if (error instanceof TypeError && error.message.includes('fetch')) {
                throw new Error('Network error - please check if the server is running');
            }
            
            throw error;
        }
    }
    
    showResults(data, params) {
        // Hide other sections
        this.errorSection.style.display = 'none';
        
        // Show results section
        this.resultsSection.style.display = 'block';
        
        // Populate summary metrics
        this.populateSummaryMetrics(data);
        
        // Show raw results
        this.populateRawResults(data, params);
        
        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    populateSummaryMetrics(data) {
        const summaryDiv = document.getElementById('results-summary');
        const performanceSummary = data.performance_summary || {};
        
        // Extract key metrics
        const metrics = [
            {
                label: 'Initial Capital',
                value: this.formatCurrency(performanceSummary.initial_capital || 0),
                class: ''
            },
            {
                label: 'Final Value',
                value: this.formatCurrency(performanceSummary.final_portfolio_value || 0),
                class: ''
            },
            {
                label: 'Total Return',
                value: this.formatPercentage(performanceSummary.total_return || 0),
                class: (performanceSummary.total_return || 0) >= 0 ? 'positive' : 'negative'
            },
            {
                label: 'Max Drawdown',
                value: this.formatPercentage(performanceSummary.max_drawdown || 0),
                class: 'negative'
            },
            {
                label: 'Total Trades',
                value: (performanceSummary.total_trades || 0).toString(),
                class: ''
            },
            {
                label: 'Performance Rating',
                value: performanceSummary.performance_rating || 'Unknown',
                class: ''
            }
        ];
        
        // Generate HTML for metrics
        summaryDiv.innerHTML = metrics.map(metric => `
            <div class="metric-card">
                <div class="metric-label">${metric.label}</div>
                <div class="metric-value ${metric.class}">${metric.value}</div>
            </div>
        `).join('');
    }
    
    populateRawResults(data, params) {
        const rawDiv = document.getElementById('results-raw');
        
        // Create a summary object for display
        const displayData = {
            backtest_parameters: params,
            execution_metadata: data.execution_metadata || {},
            performance_summary: data.performance_summary || {},
            tsx_strategy_analysis: data.tsx_strategy_analysis || {},
            trade_execution_analysis: data.trade_execution_analysis || {},
            bridge_integration_status: data.bridge_integration_status || {},
            risk_analysis: data.risk_analysis || {},
            recommendations: data.recommendations || []
        };
        
        rawDiv.textContent = JSON.stringify(displayData, null, 2);
    }
    
    showError(message) {
        // Hide other sections
        this.resultsSection.style.display = 'none';
        
        // Show error section
        this.errorSection.style.display = 'block';
        
        // Set error message
        const errorContent = document.getElementById('error-content');
        errorContent.textContent = message;
        
        // Scroll to error
        this.errorSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    showLoading() {
        this.loadingSection.style.display = 'block';
        this.runButton.disabled = true;
        this.btnText.textContent = 'Running...';
        this.btnSpinner.style.display = 'inline-block';
        this.resetProgress();
        this.startProgressPolling();
    }
    
    hideLoading() {
        this.loadingSection.style.display = 'none';
        this.runButton.disabled = false;
        this.btnText.textContent = 'Run Backtest';
        this.btnSpinner.style.display = 'none';
        this.stopProgressPolling();
    }
    
    resetUI() {
        this.errorSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
    }
    
    // Utility methods
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }
    
    formatPercentage(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value / 100);
    }
    
    // Progress bar methods
    resetProgress() {
        this.updateProgress(0, 'Starting...');
    }
    
    updateProgress(percent, eta = null) {
        if (this.progressFill) {
            this.progressFill.style.width = `${percent}%`;
        }
        if (this.progressPercent) {
            this.progressPercent.textContent = `${Math.round(percent)}%`;
        }
        if (this.progressEta && eta) {
            this.progressEta.textContent = eta;
        }
    }
    
    startProgressPolling() {
        // Clear any existing polling
        this.stopProgressPolling();
        
        // Start polling for progress updates every 2 seconds
        this.progressPollInterval = setInterval(() => {
            this.pollProgress();
        }, 2000);
        
        // Initial poll
        setTimeout(() => this.pollProgress(), 500);
    }
    
    stopProgressPolling() {
        if (this.progressPollInterval) {
            clearInterval(this.progressPollInterval);
            this.progressPollInterval = null;
        }
    }
    
    async pollProgress() {
        try {
            const response = await fetch('/progress', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.progress !== undefined) {
                    this.updateProgress(data.progress, data.eta || 'Calculating...');
                    
                    // If backtest is complete, get results
                    if (data.progress >= 100 && !data.running) {
                        this.stopProgressPolling();
                        await this.fetchResults();
                    }
                }
            }
        } catch (error) {
            console.warn('[BacktesterUI] Progress poll failed:', error.message);
        }
    }
    
    async pollForResults(params) {
        // This method polls for results when using threaded approach
        let attempts = 0;
        const maxAttempts = 180; // 6 minutes maximum wait (2s intervals)
        
        const checkResults = async () => {
            try {
                attempts++;
                const progressResponse = await fetch('/progress');
                if (progressResponse.ok) {
                    const progressData = await progressResponse.json();
                    
                    // Update progress if available
                    if (progressData.progress !== undefined) {
                        this.updateProgress(progressData.progress, progressData.eta || 'Processing...');
                    }
                    
                    // Check if complete
                    if (progressData.progress >= 100 && !progressData.running) {
                        await this.fetchResults();
                        return;
                    }
                }
                
                // Continue polling if not complete and not exceeded max attempts
                if (attempts < maxAttempts) {
                    setTimeout(checkResults, 2000); // Check every 2 seconds
                } else {
                    throw new Error('Backtest timeout - exceeded maximum wait time');
                }
                
            } catch (error) {
                console.error('[BacktesterUI] Results polling failed:', error);
                this.showError(error.message);
                this.hideLoading();
            }
        };
        
        // Start polling
        setTimeout(checkResults, 1000); // Start after 1 second
    }
    
    async fetchResults() {
        try {
            const response = await fetch('/results');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.data) {
                    this.showResults(data.data, {});
                    console.log('[BacktesterUI] Backtest completed successfully');
                } else {
                    throw new Error(data.error || 'No results available');
                }
            } else {
                throw new Error('Failed to fetch results');
            }
        } catch (error) {
            console.error('[BacktesterUI] Failed to fetch results:', error);
            this.showError(error.message);
        } finally {
            this.hideLoading();
        }
    }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('[BacktesterUI] DOM loaded, initializing...');
    
    // Check if all required elements exist
    const requiredElements = [
        'backtest-form',
        'run-btn', 
        'btn-text',
        'btn-spinner',
        'loading',
        'error',
        'results'
    ];
    
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    
    if (missingElements.length > 0) {
        console.error('[BacktesterUI] Missing required elements:', missingElements);
        alert('UI initialization failed: Missing required elements');
        return;
    }
    
    // Initialize the backtester UI
    try {
        window.backtesterUI = new BacktesterUI();
        console.log('[BacktesterUI] Ready for backtesting');
    } catch (error) {
        console.error('[BacktesterUI] Initialization failed:', error);
        alert('UI initialization failed: ' + error.message);
    }
});

// Add some basic keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl+Enter to submit form
    if (event.ctrlKey && event.key === 'Enter') {
        const form = document.getElementById('backtest-form');
        if (form && !document.getElementById('run-btn').disabled) {
            form.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to stop/reset
    if (event.key === 'Escape') {
        if (window.backtesterUI) {
            window.backtesterUI.resetUI();
            window.backtesterUI.hideLoading();
        }
    }
});

// Export for testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BacktesterUI;
}