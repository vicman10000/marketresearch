// =================================================================
// API Client - Centralized API communication
// Handles authentication, error handling, and retry logic
// =================================================================

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL || window.location.origin;
        this.apiPrefix = '/api';
        this.token = this.loadToken();
        this.refreshToken = this.loadRefreshToken();
        this.ws = null;
    }
    
    // ===== Token Management =====
    
    loadToken() {
        return localStorage.getItem('access_token');
    }
    
    loadRefreshToken() {
        return localStorage.getItem('refresh_token');
    }
    
    saveTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
        this.token = accessToken;
        this.refreshToken = refreshToken;
    }
    
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        this.token = null;
        this.refreshToken = null;
    }
    
    isAuthenticated() {
        return !!this.token;
    }
    
    // ===== HTTP Methods =====
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${this.apiPrefix}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Add auth token if available
        if (this.token && !options.skipAuth) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        const config = {
            ...options,
            headers
        };
        
        try {
            const response = await fetch(url, config);
            
            // Handle 401 Unauthorized - token might be expired
            if (response.status === 401 && this.token && !options.skipRetry) {
                // Try to refresh token and retry
                // For now, just clear tokens and redirect to login
                this.clearTokens();
                window.dispatchEvent(new CustomEvent('auth-required'));
                throw new Error('Authentication required');
            }
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Request failed' }));
                throw new Error(error.detail || `HTTP ${response.status}`);
            }
            
            // Check if response has content
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
            
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }
    
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }
    
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    async put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
    
    // ===== Authentication APIs =====
    
    async register(email, username, password, fullName = null) {
        const data = await this.post('/auth/register', {
            email,
            username,
            password,
            full_name: fullName
        }, { skipAuth: true });
        
        return data;
    }
    
    async login(email, password) {
        const data = await this.post('/auth/login', {
            email,
            password
        }, { skipAuth: true });
        
        this.saveTokens(data.access_token, data.refresh_token);
        return data;
    }
    
    async logout() {
        try {
            await this.post('/auth/logout');
        } finally {
            this.clearTokens();
            if (this.ws) {
                this.ws.close();
            }
        }
    }
    
    async getCurrentUser() {
        return await this.get('/auth/me');
    }
    
    async getPreferences() {
        return await this.get('/auth/preferences');
    }
    
    async updatePreferences(preferences) {
        return await this.put('/auth/preferences', preferences);
    }
    
    // ===== Market Data APIs =====
    
    async getStocks(sector = null, limit = 100, skip = 0) {
        let endpoint = `/stocks?limit=${limit}&skip=${skip}`;
        if (sector) {
            endpoint += `&sector=${encodeURIComponent(sector)}`;
        }
        return await this.get(endpoint);
    }
    
    async getStock(symbol) {
        return await this.get(`/stocks/${symbol}`);
    }
    
    async getSectors() {
        return await this.get('/stocks/sectors/list');
    }
    
    async refreshData(maxStocks = null) {
        const endpoint = maxStocks ? `/stocks/refresh?max_stocks=${maxStocks}` : '/stocks/refresh';
        return await this.post(endpoint);
    }
    
    // ===== Analytics APIs =====
    
    async getDashboardSummary() {
        return await this.get('/analytics/summary');
    }
    
    async getTopPerformers(count = 10, metric = 'ytd_return') {
        return await this.get(`/analytics/top-performers?count=${count}&metric=${metric}`);
    }
    
    async getSectorBreakdown() {
        return await this.get('/analytics/sector-breakdown');
    }
    
    async customQuery(query) {
        return await this.post('/analytics/custom-query', query);
    }
    
    async getVisualizations() {
        return await this.get('/analytics/visualizations/list');
    }
    
    // ===== WebSocket Connection =====
    
    connectWebSocket(endpoint, onMessage, onError = null) {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsURL = `${wsProtocol}//${window.location.host}${this.apiPrefix}${endpoint}`;
        
        // Add token to URL if authenticated
        const url = this.token ? `${wsURL}?token=${this.token}` : wsURL;
        
        this.ws = new WebSocket(url);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            // Send ping every 30 seconds
            this.pingInterval = setInterval(() => {
                if (this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({ action: 'ping' }));
                }
            }, 30000);
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('WebSocket message parse error:', error);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (onError) onError(error);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            if (this.pingInterval) {
                clearInterval(this.pingInterval);
            }
        };
        
        return this.ws;
    }
    
    sendWebSocketMessage(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }
    
    closeWebSocket() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
        }
    }
}

// Create global API client instance
const apiClient = new APIClient();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APIClient;
}

