/**
 * CARA Platform Dashboard Module
 * 
 * Handles dashboard-specific functionality including jurisdiction updates,
 * chart rendering, and dashboard interactions.
 */

import { StorageUtils, DomUtils } from './utils.js';

/**
 * Dashboard Controller Class
 */
class DashboardController {
    constructor() {
        this.currentJurisdictionId = null;
        this.currentJurisdictionName = null;
        this.charts = {};
        this.init();
    }

    /**
     * Initialize dashboard functionality
     */
    init() {
        // Get jurisdiction data from template variables if available
        this.loadJurisdictionFromTemplate();
        
        // Update storage and navbar
        this.updateJurisdictionData();
        
        // Initialize chart rendering
        this.initializeCharts();
        
        // Set up event listeners
        this.setupEventListeners();
    }

    /**
     * Load jurisdiction data from template variables
     */
    loadJurisdictionFromTemplate() {
        // These will be set by the template
        if (typeof window.templateData !== 'undefined') {
            this.currentJurisdictionId = window.templateData.jurisdictionId;
            this.currentJurisdictionName = window.templateData.jurisdictionName;
        }
    }

    /**
     * Update localStorage and navbar display with current jurisdiction
     */
    updateJurisdictionData() {
        if (this.currentJurisdictionId && this.currentJurisdictionName) {
            // Update localStorage to reflect current jurisdiction
            StorageUtils.setSelectedJurisdiction(this.currentJurisdictionId, this.currentJurisdictionName);
            
            // Update navbar display immediately
            DomUtils.updateElementContent('jurisdiction-display', 
                this.currentJurisdictionName);
        }
    }

    /**
     * Initialize all charts on the dashboard
     */
    initializeCharts() {
        // Risk distribution chart
        this.initializeRiskDistributionChart();
        
        // Temporal components chart
        this.initializeTemporalChart();
        
        // Individual domain charts
        this.initializeDomainCharts();
    }

    /**
     * Initialize risk distribution pie chart
     */
    initializeRiskDistributionChart() {
        const ctx = DomUtils.getElementById('riskDistributionChart');
        if (!ctx || typeof Chart === 'undefined') return;

        // Chart data will be provided by template or API
        if (typeof window.chartData !== 'undefined' && window.chartData.riskDistribution) {
            this.charts.riskDistribution = new Chart(ctx, {
                type: 'doughnut',
                data: window.chartData.riskDistribution,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: 'Risk Distribution by Domain'
                        }
                    }
                }
            });
        }
    }

    /**
     * Initialize temporal components chart
     */
    initializeTemporalChart() {
        const ctx = DomUtils.getElementById('temporalChart');
        if (!ctx || typeof Chart === 'undefined') return;

        if (typeof window.chartData !== 'undefined' && window.chartData.temporal) {
            this.charts.temporal = new Chart(ctx, {
                type: 'bar',
                data: window.chartData.temporal,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1.0,
                            ticks: {
                                callback: function(value) {
                                    return (value * 100).toFixed(0) + '%';
                                }
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Temporal Risk Components (BSTA Framework)'
                        }
                    }
                }
            });
        }
    }

    /**
     * Initialize individual domain charts
     */
    initializeDomainCharts() {
        const domains = ['naturalHazards', 'infectiousDisease', 'activeShooter', 'climateAdjusted'];
        
        domains.forEach(domain => {
            const ctx = DomUtils.getElementById(`${domain}Chart`);
            if (ctx && typeof window.chartData !== 'undefined' && window.chartData[domain]) {
                this.charts[domain] = new Chart(ctx, {
                    type: 'radar',
                    data: window.chartData[domain],
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            r: {
                                beginAtZero: true,
                                max: 1.0,
                                ticks: {
                                    callback: function(value) {
                                        return (value * 100).toFixed(0) + '%';
                                    }
                                }
                            }
                        }
                    }
                });
            }
        });
    }

    /**
     * Set up event listeners for dashboard interactions
     */
    setupEventListeners() {
        // Chart interaction handlers
        Object.keys(this.charts).forEach(chartName => {
            const chart = this.charts[chartName];
            if (chart && chart.canvas) {
                DomUtils.addEventListenerSafe(chart.canvas, 'click', (evt) => {
                    this.handleChartClick(chartName, evt);
                });
            }
        });

        // Print button handlers
        const printButtons = document.querySelectorAll('[href*="/print-summary/"]');
        printButtons.forEach(button => {
            DomUtils.addEventListenerSafe(button, 'click', (e) => {
                // Track print action for analytics
                this.trackAction('print_summary');
            });
        });

        // Action plan button handlers
        const actionButtons = document.querySelectorAll('[href*="/action-plan/"]');
        actionButtons.forEach(button => {
            DomUtils.addEventListenerSafe(button, 'click', (e) => {
                // Track action plan generation
                this.trackAction('generate_action_plan');
            });
        });
    }

    /**
     * Handle chart click interactions
     * @param {string} chartName - Name of the clicked chart
     * @param {Event} evt - Click event
     */
    handleChartClick(chartName, evt) {
        const chart = this.charts[chartName];
        if (!chart) return;

        const points = Chart.getElementsAtEventForMode(chart, evt, 'nearest', { intersect: true }, true);
        
        if (points.length) {
            const firstPoint = points[0];
            const label = chart.data.labels[firstPoint.index];
            const value = chart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
            
            // Show detailed information about the clicked segment
            this.showChartDetail(chartName, label, value);
        }
    }

    /**
     * Show detailed information for chart segment
     * @param {string} chartName - Chart identifier
     * @param {string} label - Data label
     * @param {number} value - Data value
     */
    showChartDetail(chartName, label, value) {
        // Could show a modal or tooltip with more details
        console.log(`Chart: ${chartName}, Label: ${label}, Value: ${value}`);
        
        // Example: could trigger a detail modal
        // this.showDetailModal(chartName, label, value);
    }

    /**
     * Track user actions for analytics
     * @param {string} action - Action identifier
     */
    trackAction(action) {
        // Simple action tracking - could be enhanced with analytics service
        console.log(`Dashboard action: ${action}`, {
            jurisdiction: this.currentJurisdictionName,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Update dashboard with new data
     * @param {Object} newData - Updated risk data
     */
    updateDashboard(newData) {
        // Update charts with new data
        Object.keys(this.charts).forEach(chartName => {
            if (newData[chartName] && this.charts[chartName]) {
                this.charts[chartName].data = newData[chartName];
                this.charts[chartName].update();
            }
        });
    }

    /**
     * Cleanup dashboard resources
     */
    destroy() {
        // Destroy all Chart.js instances
        Object.values(this.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        
        this.charts = {};
    }
}

// Initialize dashboard when DOM is ready
let dashboardController;

document.addEventListener('DOMContentLoaded', () => {
    dashboardController = new DashboardController();
    
    // Make controller available globally for debugging
    window.dashboardController = dashboardController;
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboardController) {
        dashboardController.destroy();
    }
});

export default DashboardController;