// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.charts = {};
        this.currentFilters = {};
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        this.updateCurrentTime();
        this.setupEventListeners();
        this.loadDashboardData();
        this.startAutoRefresh();
    }
    
    updateCurrentTime() {
        const now = new Date();
        const timeString = now.toLocaleString();
        document.getElementById('current-time').textContent = timeString;
        
        // Update every minute
        setTimeout(() => this.updateCurrentTime(), 60000);
    }
    
    setupEventListeners() {
        // Filter form submission
        document.getElementById('filter-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });
        
        // Auto-refresh toggle (future enhancement)
        // Real-time updates can be added here
    }
    
    applyFilters() {
        const formData = new FormData(document.getElementById('filter-form'));
        this.currentFilters = Object.fromEntries(formData.entries());
        
        // Remove empty values
        Object.keys(this.currentFilters).forEach(key => {
            if (!this.currentFilters[key]) {
                delete this.currentFilters[key];
            }
        });
        
        this.loadDashboardData();
    }
    
    async loadDashboardData() {
        this.showLoading();
        
        try {
            await Promise.all([
                this.loadMetrics(),
                this.loadAnalytics(),
                this.loadSentimentAnalysis(),
                this.loadRecentChats(),
                this.loadSupportQueue()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        } finally {
            this.hideLoading();
        }
    }
    
    async loadMetrics() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`/api/metrics?${params}`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateMetricsCards(data);
            } else {
                throw new Error(data.detail || 'Failed to load metrics');
            }
        } catch (error) {
            console.error('Error loading metrics:', error);
            this.showMetricsError();
        }
    }
    
    updateMetricsCards(metrics) {
        document.getElementById('total-chats').textContent = metrics.total_chats.toLocaleString();
        document.getElementById('resolution-rate').textContent = `${metrics.resolution_rate.toFixed(1)}%`;
        document.getElementById('avg-response-time').textContent = `${metrics.avg_response_time.toFixed(1)}s`;
        document.getElementById('feedback-rate').textContent = `${metrics.feedback_rate.toFixed(1)}%`;
        
        // Add animation
        document.getElementById('metrics-cards').classList.add('fade-in');
    }
    
    showMetricsError() {
        document.getElementById('total-chats').textContent = 'Error';
        document.getElementById('resolution-rate').textContent = 'Error';
        document.getElementById('avg-response-time').textContent = 'Error';
        document.getElementById('feedback-rate').textContent = 'Error';
    }
    
    async loadAnalytics() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`/api/analytics?${params}`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateCharts(data);
            } else {
                throw new Error(data.detail || 'Failed to load analytics');
            }
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }
    
    updateCharts(analytics) {
        this.updateCategoriesChart(analytics.categories);
        this.updateDailyChatsChart(analytics.daily_chats);
        this.updateLanguageChart(analytics.languages);
    }
    
    updateCategoriesChart(categories) {
        const ctx = document.getElementById('categories-chart').getContext('2d');
        
        if (this.charts.categories) {
            this.charts.categories.destroy();
        }
        
        this.charts.categories = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(categories),
                datasets: [{
                    data: Object.values(categories),
                    backgroundColor: [
                        '#007bff',
                        '#28a745',
                        '#ffc107',
                        '#dc3545',
                        '#6f42c1'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    updateDailyChatsChart(dailyChats) {
        const ctx = document.getElementById('daily-chats-chart').getContext('2d');
        
        if (this.charts.dailyChats) {
            this.charts.dailyChats.destroy();
        }
        
        const sortedDates = Object.keys(dailyChats).sort();
        const values = sortedDates.map(date => dailyChats[date]);
        
        this.charts.dailyChats = new Chart(ctx, {
            type: 'line',
            data: {
                labels: sortedDates,
                datasets: [{
                    label: 'Daily Chats',
                    data: values,
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    updateLanguageChart(languages) {
        const ctx = document.getElementById('language-chart').getContext('2d');
        
        if (this.charts.language) {
            this.charts.language.destroy();
        }
        
        this.charts.language = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(languages).map(lang => lang === 'en' ? 'English' : lang === 'ar' ? 'Arabic' : lang),
                datasets: [{
                    data: Object.values(languages),
                    backgroundColor: ['#17a2b8', '#fd7e14']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    async loadSentimentAnalysis() {
        try {
            const params = new URLSearchParams(this.currentFilters);
            const response = await fetch(`/api/sentiment?${params}`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateSentimentChart(data);
            } else {
                throw new Error(data.detail || 'Failed to load sentiment analysis');
            }
        } catch (error) {
            console.error('Error loading sentiment analysis:', error);
        }
    }
    
    updateSentimentChart(sentimentData) {
        const ctx = document.getElementById('sentiment-chart').getContext('2d');
        
        if (this.charts.sentiment) {
            this.charts.sentiment.destroy();
        }
        
        this.charts.sentiment = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Positive', 'Neutral', 'Negative'],
                datasets: [{
                    label: 'Sentiment Distribution',
                    data: [
                        sentimentData.sentiment_counts.positive || 0,
                        sentimentData.sentiment_counts.neutral || 0,
                        sentimentData.sentiment_counts.negative || 0
                    ],
                    backgroundColor: ['#28a745', '#6c757d', '#dc3545']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    async loadRecentChats() {
        try {
            const params = new URLSearchParams({
                limit: 10,
                ...(this.currentFilters.user_id && { user_id: this.currentFilters.user_id })
            });
            
            const response = await fetch(`/api/recent-chats?${params}`);
            const data = await response.json();
            
            if (response.ok) {
                this.updateRecentChatsTable(data.recent_chats);
            } else {
                throw new Error(data.detail || 'Failed to load recent chats');
            }
        } catch (error) {
            console.error('Error loading recent chats:', error);
            this.showRecentChatsError();
        }
    }
    
    updateRecentChatsTable(chats) {
        const tbody = document.getElementById('recent-chats-table');
        
        if (chats.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No recent chats found</td></tr>';
            return;
        }
        
        tbody.innerHTML = chats.map(chat => `
            <tr>
                <td>${new Date(chat.timestamp).toLocaleString()}</td>
                <td>${chat.user_id || 'Anonymous'}</td>
                <td title="${chat.message}">${this.truncateText(chat.message, 50)}</td>
                <td><span class="badge bg-primary">${chat.category}</span></td>
                <td>
                    <span class="badge ${chat.resolved ? 'bg-success' : 'bg-warning'}">
                        ${chat.resolved ? 'Resolved' : 'Unresolved'}
                    </span>
                </td>
                <td>
                    ${this.getFeedbackIcon(chat.feedback_type)}
                </td>
            </tr>
        `).join('');
    }
    
    showRecentChatsError() {
        const tbody = document.getElementById('recent-chats-table');
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading recent chats</td></tr>';
    }
    
    async loadSupportQueue() {
        try {
            const response = await fetch('/api/support-queue?limit=20');
            const data = await response.json();
            
            if (response.ok) {
                this.updateSupportQueue(data.queue_items);
            } else {
                throw new Error(data.detail || 'Failed to load support queue');
            }
        } catch (error) {
            console.error('Error loading support queue:', error);
            this.showSupportQueueError();
        }
    }
    
    updateSupportQueue(queueItems) {
        const container = document.getElementById('support-queue');
        
        if (queueItems.length === 0) {
            container.innerHTML = '<div class="empty-state"><i class="fas fa-check-circle"></i><p>No items in support queue</p></div>';
            return;
        }
        
        container.innerHTML = queueItems.map(item => `
            <div class="support-queue-item">
                <div class="timestamp">${new Date(item.timestamp).toLocaleString()}</div>
                <div class="message">${this.truncateText(item.message, 60)}</div>
                <div class="d-flex justify-content-between align-items-center mt-2">
                    <span class="badge bg-secondary">${item.category}</span>
                    <span class="confidence">Confidence: ${(item.confidence * 100).toFixed(0)}%</span>
                </div>
                ${item.feedback_comment ? `<div class="mt-1 text-muted small">Comment: ${item.feedback_comment}</div>` : ''}
            </div>
        `).join('');
    }
    
    showSupportQueueError() {
        const container = document.getElementById('support-queue');
        container.innerHTML = '<div class="text-center text-danger">Error loading support queue</div>';
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    getFeedbackIcon(feedbackType) {
        switch (feedbackType) {
            case 'like':
                return '<i class="fas fa-thumbs-up text-success"></i>';
            case 'dislike':
                return '<i class="fas fa-thumbs-down text-danger"></i>';
            default:
                return '<i class="fas fa-minus text-muted"></i>';
        }
    }
    
    showLoading() {
        const modal = new bootstrap.Modal(document.getElementById('loading-modal'));
        modal.show();
    }
    
    hideLoading() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('loading-modal'));
        if (modal) {
            modal.hide();
        }
    }
    
    showError(message) {
        // Simple error display - can be enhanced with a proper modal
        console.error(message);
        alert(`Error: ${message}`);
    }
    
    startAutoRefresh() {
        // Refresh data every 5 minutes
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 300000);
    }
    
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});

// Handle page visibility changes to pause/resume refresh
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, could pause refresh
    } else {
        // Page is visible, resume refresh
    }
});
