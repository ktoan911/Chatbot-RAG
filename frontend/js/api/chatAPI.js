/* ==========================================================================
   Chat API Integration
   Handles all communication with the backend RAG chatbot API
   ========================================================================== */

class ChatAPI {
    constructor() {
        // TODO: Thay đổi BASE_URL theo địa chỉ server backend của bạn
        this.BASE_URL = 'http://localhost:5000';
        this.timeout = 30000; // 30 seconds timeout
        this.retryAttempts = 3;
    }

    /**
     * Make HTTP request with error handling and retries
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Request options
     * @returns {Promise<Object>} Response data
     */
    async makeRequest(endpoint, options = {}) {
        const url = `${this.BASE_URL}${endpoint}`;
        const defaultOptions = {
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            ...options
        };

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const response = await fetch(url, {
                    ...defaultOptions,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data;

            } catch (error) {
                console.error(`Request attempt ${attempt} failed:`, error);

                // Don't retry on certain errors
                if (error.name === 'AbortError') {
                    throw new Error('Request timeout');
                }

                if (attempt === this.retryAttempts) {
                    throw error;
                }

                // Wait before retry (exponential backoff)
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
            }
        }
    }

    /**
     * Health check - verify API is accessible
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        try {
            // TODO: Gọi API health check endpoint "/"
            const response = await this.makeRequest('/');
            return {
                success: true,
                status: response.status,
                service: response.service,
                timestamp: response.timestamp
            };
        } catch (error) {
            console.error('Health check failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Send message to chatbot and get response
     * @param {string} message - User message
     * @returns {Promise<Object>} Bot response
     */
    async sendMessage(message) {
        try {
            if (!message || message.trim().length === 0) {
                throw new Error('Message cannot be empty');
            }

            // TODO: Gọi API endpoint "/get_message" với POST method
            // Payload: { input: message }
            const response = await this.makeRequest('/get_message', {
                method: 'POST',
                body: JSON.stringify({
                    input: message.trim()
                })
            });

            if (response.status === 'success') {
                return {
                    success: true,
                    message: response.response,
                    processingTime: response.time,
                    timestamp: Date.now() / 1000
                };
            } else {
                throw new Error(response.error || 'Unknown error occurred');
            }

        } catch (error) {
            console.error('Send message failed:', error);
            return {
                success: false,
                error: error.message,
                timestamp: Date.now() / 1000
            };
        }
    }

    /**
     * Get chat history from server
     * @returns {Promise<Object>} Chat history
     */
    async getChatHistory() {
        try {
            // TODO: Gọi API endpoint "/get_history" với GET method
            const response = await this.makeRequest('/get_history');

            if (response.status === 'success') {
                return {
                    success: true,
                    history: response.history || [],
                    count: response.count || 0
                };
            } else {
                throw new Error(response.error || 'Failed to get history');
            }

        } catch (error) {
            console.error('Get chat history failed:', error);
            return {
                success: false,
                error: error.message,
                history: []
            };
        }
    }

    /**
     * Clear/delete chat history
     * @returns {Promise<Object>} Delete result
     */
    async clearChatHistory() {
        try {
            // TODO: Gọi API endpoint "/delete_history" với DELETE method
            const response = await this.makeRequest('/delete_history', {
                method: 'DELETE'
            });

            if (response.status === 'success') {
                return {
                    success: true,
                    message: response.message
                };
            } else {
                throw new Error(response.error || 'Failed to clear history');
            }

        } catch (error) {
            console.error('Clear chat history failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get current configuration
     * @returns {Promise<Object>} Configuration
     */
    async getConfig() {
        try {
            // TODO: Gọi API endpoint "/config" với GET method
            const response = await this.makeRequest('/config');

            if (response.status === 'success') {
                return {
                    success: true,
                    config: {
                        numHistory: response.num_history
                    }
                };
            } else {
                throw new Error(response.error || 'Failed to get config');
            }

        } catch (error) {
            console.error('Get config failed:', error);
            return {
                success: false,
                error: error.message,
                config: { numHistory: 10 } // Default value
            };
        }
    }

    /**
     * Update configuration
     * @param {Object} config - Configuration object
     * @returns {Promise<Object>} Update result
     */
    async updateConfig(config) {
        try {
            // TODO: Gọi API endpoint "/config" với POST method
            // Payload: { num_history: config.numHistory }
            const response = await this.makeRequest('/config', {
                method: 'POST',
                body: JSON.stringify({
                    num_history: config.numHistory
                })
            });

            if (response.status === 'success') {
                return {
                    success: true,
                    message: response.message,
                    config: {
                        numHistory: response.num_history
                    }
                };
            } else {
                throw new Error(response.error || 'Failed to update config');
            }

        } catch (error) {
            console.error('Update config failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Export chat history
     * @returns {Promise<Object>} Exported history
     */
    async exportHistory() {
        try {
            // TODO: Gọi API endpoint "/export_history" với GET method
            const response = await this.makeRequest('/export_history');

            if (response.status === 'success') {
                return {
                    success: true,
                    history: response.history,
                    exportedAt: response.exported_at,
                    count: response.count
                };
            } else {
                throw new Error(response.error || 'Failed to export history');
            }

        } catch (error) {
            console.error('Export history failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Check if API is reachable
     * @returns {Promise<boolean>} Connection status
     */
    async isConnected() {
        try {
            const health = await this.healthCheck();
            return health.success;
        } catch (error) {
            return false;
        }
    }

    /**
     * Get connection status with details
     * @returns {Promise<Object>} Detailed connection status
     */
    async getConnectionStatus() {
        try {
            const health = await this.healthCheck();
            
            if (health.success) {
                return {
                    connected: true,
                    status: 'connected',
                    message: 'Kết nối thành công',
                    service: health.service,
                    latency: Date.now() - (health.timestamp * 1000)
                };
            } else {
                return {
                    connected: false,
                    status: 'error',
                    message: 'Không thể kết nối',
                    error: health.error
                };
            }
        } catch (error) {
            return {
                connected: false,
                status: 'error',
                message: 'Lỗi kết nối',
                error: error.message
            };
        }
    }

    /**
     * Validate message before sending
     * @param {string} message - Message to validate
     * @returns {Object} Validation result
     */
    validateMessage(message) {
        if (!message || typeof message !== 'string') {
            return {
                valid: false,
                error: 'Tin nhắn không hợp lệ'
            };
        }

        const trimmed = message.trim();
        if (trimmed.length === 0) {
            return {
                valid: false,
                error: 'Tin nhắn không được để trống'
            };
        }

        if (trimmed.length > 1000) {
            return {
                valid: false,
                error: 'Tin nhắn quá dài (tối đa 1000 ký tự)'
            };
        }

        return {
            valid: true,
            message: trimmed
        };
    }

    /**
     * Set base URL for API
     * @param {string} url - New base URL
     */
    setBaseURL(url) {
        this.BASE_URL = url.replace(/\/$/, ''); // Remove trailing slash
    }

    /**
     * Set request timeout
     * @param {number} timeout - Timeout in milliseconds
     */
    setTimeout(timeout) {
        this.timeout = timeout;
    }

    /**
     * Set retry attempts
     * @param {number} attempts - Number of retry attempts
     */
    setRetryAttempts(attempts) {
        this.retryAttempts = attempts;
    }
}

// Create and export global instance
window.chatAPI = new ChatAPI();

// TODO: Khi triển khai production, hãy thay đổi các cấu hình sau:
// 1. BASE_URL: Địa chỉ server backend thực tế
// 2. Timeout: Điều chỉnh theo yêu cầu
// 3. Retry attempts: Số lần thử lại khi request thất bại
// 4. Error handling: Xử lý lỗi chi tiết hơn
// 5. Authentication: Thêm xác thực nếu cần
// 6. Rate limiting: Giới hạn số request
// 7. Caching: Cache response để tối ưu performance

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatAPI;
} 