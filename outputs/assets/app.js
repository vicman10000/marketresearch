// =================================================================
// Market Research Dashboard - Professional Financial Theme
// Navigation, Theme Toggle, and Dynamic Content Loading
// =================================================================

class Dashboard {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.themeToggle = document.getElementById('themeToggle');
        this.navItems = document.querySelectorAll('.nav-item');
        this.contentFrame = document.getElementById('contentFrame');
        this.pageTitle = document.getElementById('pageTitle');
        this.pageSubtitle = document.getElementById('pageSubtitle');
        this.lastUpdated = document.getElementById('lastUpdated');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.downloadReport = document.getElementById('downloadReport');
        
        this.views = {
            dashboard: document.getElementById('dashboardView'),
            dynamic: document.getElementById('dynamicView'),
            report: document.getElementById('reportView')
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadThemePreference();
        this.updateLastUpdated();
        this.loadMetadata();
        
        // Auto-update time every minute
        setInterval(() => this.updateLastUpdated(), 60000);
    }
    
    setupEventListeners() {
        // Sidebar toggle
        this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Navigation items
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleNavigation(e));
        });
        
        // Refresh button
        this.refreshBtn.addEventListener('click', () => this.refreshContent());
        
        // Download report
        if (this.downloadReport) {
            this.downloadReport.addEventListener('click', () => this.downloadReportFile());
        }
        
        // Handle responsive sidebar on mobile
        if (window.innerWidth <= 768) {
            document.addEventListener('click', (e) => {
                if (!this.sidebar.contains(e.target) && this.sidebar.classList.contains('mobile-open')) {
                    this.sidebar.classList.remove('mobile-open');
                }
            });
        }
    }
    
    toggleSidebar() {
        this.sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', this.sidebar.classList.contains('collapsed'));
        
        // On mobile, use mobile-open class
        if (window.innerWidth <= 768) {
            this.sidebar.classList.toggle('mobile-open');
        }
    }
    
    toggleTheme() {
        const body = document.body;
        const isDark = body.classList.contains('dark-theme');
        
        if (isDark) {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
            this.themeToggle.innerHTML = '<i class="fas fa-moon"></i><span>Dark Mode</span>';
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            this.themeToggle.innerHTML = '<i class="fas fa-sun"></i><span>Light Mode</span>';
            localStorage.setItem('theme', 'dark');
        }
    }
    
    loadThemePreference() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        const body = document.body;
        
        if (savedTheme === 'dark') {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
            this.themeToggle.innerHTML = '<i class="fas fa-sun"></i><span>Light Mode</span>';
        }
        
        // Load sidebar state
        const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (sidebarCollapsed) {
            this.sidebar.classList.add('collapsed');
        }
    }
    
    handleNavigation(e) {
        e.preventDefault();
        const navItem = e.currentTarget;
        const view = navItem.getAttribute('data-view');
        
        // Update active state
        this.navItems.forEach(item => item.classList.remove('active'));
        navItem.classList.add('active');
        
        // Close mobile sidebar
        if (window.innerWidth <= 768) {
            this.sidebar.classList.remove('mobile-open');
        }
        
        // Navigate to view
        this.navigateToView(view);
    }
    
    navigateToView(view) {
        // Hide all views
        Object.values(this.views).forEach(v => v.classList.remove('active'));
        
        if (view === 'dashboard') {
            // Show main dashboard
            this.views.dashboard.classList.add('active');
            this.updateHeader('Market Overview Dashboard', 'Real-time market analytics and insights');
        } else if (view === 'report') {
            // Show report view
            this.views.report.classList.add('active');
            this.updateHeader('Market Research Report', 'Comprehensive market analysis and insights');
            this.loadReport();
        } else {
            // Load visualization in iframe
            this.views.dynamic.classList.add('active');
            this.contentFrame.src = view;
            
            // Update header based on view
            const title = this.getTitleForView(view);
            const subtitle = this.getSubtitleForView(view);
            this.updateHeader(title, subtitle);
        }
    }
    
    getTitleForView(view) {
        const titles = {
            'static/bubble_chart.html': 'Return vs Volatility Analysis',
            'static/sector_performance.html': 'Sector Performance Overview',
            'static/market_cap_distribution.html': 'Market Capitalization Distribution',
            'static/top_performers.html': 'Top Performing Stocks',
            'animated/animated_bubble_chart.html': 'Animated Bubble Chart',
            'animated/animated_sector_race.html': 'Sector Performance Race',
            'animated/animated_swarm_plot.html': 'Animated Swarm Distribution',
            'animated/animated_3d_visualization.html': '3D Market Visualization'
        };
        return titles[view] || 'Market Analysis';
    }
    
    getSubtitleForView(view) {
        if (view.includes('animated/')) {
            return 'Interactive time-series visualization';
        } else if (view.includes('static/')) {
            return 'Statistical analysis and insights';
        }
        return 'Data visualization';
    }
    
    updateHeader(title, subtitle) {
        this.pageTitle.textContent = title;
        this.pageSubtitle.textContent = subtitle;
    }
    
    updateLastUpdated() {
        const now = new Date();
        const options = {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        this.lastUpdated.textContent = now.toLocaleDateString('en-US', options);
    }
    
    async loadMetadata() {
        try {
            const response = await fetch('metadata.json');
            if (response.ok) {
                const metadata = await response.json();
                this.updateDashboardStats(metadata);
                this.updateDataSource(metadata);
            }
        } catch (error) {
            console.log('Metadata not available:', error);
        }
    }
    
    updateDataSource(metadata) {
        const dataSourceEl = document.getElementById('dataSourceType');
        const marketSourceEl = document.getElementById('marketSource');
        
        // Determine if using sample data based on environment or metadata
        const usingSampleData = window.location.search.includes('sample') || 
                               (metadata && metadata.data_source === 'sample');
        
        if (dataSourceEl) {
            if (usingSampleData) {
                dataSourceEl.innerHTML = '<i class="fas fa-flask"></i> Sample Data';
                dataSourceEl.style.color = 'var(--warning)';
            } else {
                dataSourceEl.innerHTML = '<i class="fas fa-database"></i> Live Data';
                dataSourceEl.style.color = 'var(--success)';
            }
        }
        
        if (marketSourceEl) {
            // Update market source based on metadata or default to S&P 500
            const marketName = metadata?.market || 'S&P 500';
            marketSourceEl.textContent = marketName;
            
            // Add stock count if available
            if (metadata?.summary?.total_stocks) {
                marketSourceEl.textContent = `${marketName} (${metadata.summary.total_stocks} stocks)`;
            }
        }
    }
    
    updateDashboardStats(metadata) {
        // Update stat cards with real data from metadata
        if (metadata.summary) {
            const marketCapEl = document.getElementById('totalMarketCap');
            const avgReturnEl = document.getElementById('avgReturn');
            const avgVolatilityEl = document.getElementById('avgVolatility');
            const stockCountEl = document.getElementById('stockCount');
            
            if (marketCapEl && metadata.summary.total_market_cap) {
                marketCapEl.textContent = this.formatMarketCap(metadata.summary.total_market_cap);
            }
            
            if (avgReturnEl && metadata.summary.avg_ytd_return) {
                avgReturnEl.textContent = metadata.summary.avg_ytd_return.toFixed(2) + '%';
            }
            
            if (avgVolatilityEl && metadata.summary.avg_volatility) {
                avgVolatilityEl.textContent = metadata.summary.avg_volatility.toFixed(2) + '%';
            }
            
            if (stockCountEl && metadata.summary.total_stocks) {
                stockCountEl.textContent = metadata.summary.total_stocks;
            }
        }
    }
    
    formatMarketCap(value) {
        if (value >= 1e12) {
            return '$' + (value / 1e12).toFixed(2) + 'T';
        } else if (value >= 1e9) {
            return '$' + (value / 1e9).toFixed(2) + 'B';
        } else if (value >= 1e6) {
            return '$' + (value / 1e6).toFixed(2) + 'M';
        }
        return '$' + value.toFixed(0);
    }
    
    async loadReport() {
        const reportContent = document.getElementById('reportContent');
        reportContent.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading report...</div>';
        
        try {
            const response = await fetch('market_report.txt');
            if (response.ok) {
                const text = await response.text();
                reportContent.textContent = text;
            } else {
                reportContent.innerHTML = '<div class="loading"><i class="fas fa-exclamation-triangle"></i> Report not available</div>';
            }
        } catch (error) {
            reportContent.innerHTML = '<div class="loading"><i class="fas fa-exclamation-triangle"></i> Error loading report</div>';
        }
    }
    
    refreshContent() {
        // Animate refresh icon
        const icon = this.refreshBtn.querySelector('i');
        icon.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            icon.style.transform = 'rotate(0deg)';
        }, 600);
        
        // Reload current view
        const activeView = document.querySelector('.view-content.active');
        
        if (activeView === this.views.dynamic && this.contentFrame.src) {
            this.contentFrame.src = this.contentFrame.src;
        } else if (activeView === this.views.dashboard) {
            const dashboardFrame = this.views.dashboard.querySelector('.visualization-frame');
            if (dashboardFrame) {
                dashboardFrame.src = dashboardFrame.src;
            }
        } else if (activeView === this.views.report) {
            this.loadReport();
        }
        
        // Reload metadata
        this.loadMetadata();
        this.updateLastUpdated();
    }
    
    async downloadReportFile() {
        try {
            const response = await fetch('market_report.txt');
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `market_report_${new Date().toISOString().split('T')[0]}.txt`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            console.error('Error downloading report:', error);
            alert('Unable to download report. Please try again.');
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});

// Handle window resize for responsive behavior
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth > 768) {
            sidebar.classList.remove('mobile-open');
        }
    }, 250);
});

