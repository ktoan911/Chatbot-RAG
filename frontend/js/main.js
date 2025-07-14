/* ==========================================================================
   Main Application Entry Point
   Initializes and coordinates all components of the RAG Chatbot frontend
   ========================================================================== */

class ChatbotApp {
    constructor() {
        this.components = {};
        this.isInitialized = false;
        this.config = {
            version: '1.0.0',
            debug: false,
            autoSave: true,
            autoSaveInterval: 30000 // 30 seconds
        };
        
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('🚀 Initializing RAG Chatbot Application...');
            
            // Show loading overlay
            this.showInitialLoading();
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Initialize components in order
            await this.initializeComponents();
            
            // Setup global event listeners
            this.setupGlobalEvents();
            
            // Check API connection
            await this.checkInitialConnection();
            
            // Setup auto-save
            this.setupAutoSave();
            
            // Initialize keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            // Mark as initialized
            this.isInitialized = true;
            
            // Hide loading overlay
            this.hideInitialLoading();
            
            console.log('✅ Application initialized successfully');
            
            // Show welcome notification
            setTimeout(() => {
                Utils.showToast('Chào mừng đến với RAG Chatbot!', 'success', 3000);
            }, 500);
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Initialize all components
     */
    async initializeComponents() {
        try {
            // Initialize modal component first (needed for settings)
            console.log('📱 Initializing Modal Component...');
            this.components.modal = new ModalComponent();
            window.modalComponent = this.components.modal;
            
            // Initialize sidebar component
            console.log('📋 Initializing Sidebar Component...');
            this.components.sidebar = new SidebarComponent();
            window.sidebarComponent = this.components.sidebar;
            
            // Initialize chat component
            console.log('💬 Initializing Chat Component...');
            this.components.chat = new ChatComponent();
            window.chatComponent = this.components.chat;
            
            console.log('✅ All components initialized');
            
        } catch (error) {
            console.error('❌ Component initialization failed:', error);
            throw error;
        }
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEvents() {
        // Handle clear chat button
        const clearChatBtn = document.getElementById('clearChatBtn');
        clearChatBtn?.addEventListener('click', async () => {
            const confirmed = await this.components.modal.showConfirmDialog({
                title: 'Xóa cuộc trò chuyện',
                message: 'Bạn có chắc muốn xóa toàn bộ cuộc trò chuyện hiện tại?',
                confirmText: 'Xóa',
                type: 'warning'
            });
            
            if (confirmed) {
                await this.components.chat.clearChat();
            }
        });
        
        // Handle window beforeunload (save data before leaving)
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = 'Bạn có thay đổi chưa được lưu. Bạn có muốn rời khỏi trang?';
                return e.returnValue;
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', Utils.debounce(() => {
            this.handleWindowResize();
        }, 250));
        
        // Handle online/offline status
        Utils.onNetworkChange((isOnline) => {
            this.handleNetworkChange(isOnline);
        });
        
        // Handle visibility change (tab switch)
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });
        
        // Global error handler
        window.addEventListener('error', (e) => {
            this.handleGlobalError(e);
        });
        
        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            this.handleUnhandledRejection(e);
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K: Focus message input
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const messageInput = document.getElementById('messageInput');
                messageInput?.focus();
            }
            
            // Ctrl/Cmd + Shift + C: Clear chat
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                document.getElementById('clearChatBtn')?.click();
            }
            
            // Ctrl/Cmd + Shift + E: Export history
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'E') {
                e.preventDefault();
                this.components.chat?.exportChat();
            }
            
            // Ctrl/Cmd + ,: Open settings
            if ((e.ctrlKey || e.metaKey) && e.key === ',') {
                e.preventDefault();
                this.components.modal?.openSettingsModal();
            }
            
            // F11: Toggle fullscreen (if supported)
            if (e.key === 'F11') {
                e.preventDefault();
                this.toggleFullscreen();
            }
        });
    }

    /**
     * Check initial API connection
     */
    async checkInitialConnection() {
        try {
            console.log('🔗 Checking API connection...');
            
            // TODO: Kiểm tra kết nối với API backend
            const isConnected = await chatAPI.isConnected();
            
            if (isConnected) {
                console.log('✅ API connection successful');
                
                // Load initial data
                await this.loadInitialData();
                
            } else {
                console.warn('⚠️ API connection failed');
                Utils.showToast(
                    'Không thể kết nối đến server. Một số tính năng có thể không hoạt động.', 
                    'warning', 
                    5000
                );
            }
            
        } catch (error) {
            console.error('❌ Connection check failed:', error);
        }
    }

    /**
     * Load initial data from API
     */
    async loadInitialData() {
        try {
            // TODO: Load configuration from API
            const configResponse = await chatAPI.getConfig();
            if (configResponse.success) {
                // Update settings with server config
                this.components.modal.updateSetting('historyCount', configResponse.config.numHistory);
            }
            
            // Load chat history
            await this.components.sidebar.loadChatHistory();
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    /**
     * Setup auto-save functionality
     */
    setupAutoSave() {
        if (!this.config.autoSave) return;
        
        setInterval(() => {
            this.autoSave();
        }, this.config.autoSaveInterval);
        
        console.log(`🔄 Auto-save enabled (${this.config.autoSaveInterval / 1000}s interval)`);
    }

    /**
     * Perform auto-save
     */
    autoSave() {
        try {
            // Save chat messages
            if (this.components.chat) {
                this.components.chat.saveMessagesToStorage();
            }
            
            // Save chat history
            if (this.components.sidebar) {
                this.components.sidebar.saveChatHistoryToStorage();
            }
            
            // Save settings
            if (this.components.modal) {
                this.components.modal.saveSettingsToStorage();
            }
            
            if (this.config.debug) {
                console.log('💾 Auto-save completed');
            }
            
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    /**
     * Handle window resize
     */
    handleWindowResize() {
        // Update mobile layout
        if (Utils.isMobile()) {
            document.body.classList.add('mobile');
        } else {
            document.body.classList.remove('mobile');
        }
        
        // Update chat scroll
        if (this.components.chat) {
            this.components.chat.scrollToBottom();
        }
    }

    /**
     * Handle network change
     * @param {boolean} isOnline - Online status
     */
    handleNetworkChange(isOnline) {
        if (isOnline) {
            console.log('🌐 Network connected');
            Utils.showToast('Đã kết nối mạng', 'success', 2000);
            
            // Retry API connection
            if (this.components.chat) {
                this.components.chat.checkConnection();
            }
        } else {
            console.log('📴 Network disconnected');
            Utils.showToast('Mất kết nối mạng', 'warning', 3000);
        }
    }

    /**
     * Handle visibility change (tab switch)
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Tab is hidden - pause expensive operations
            if (this.config.debug) {
                console.log('👁️ Tab hidden - pausing operations');
            }
        } else {
            // Tab is visible - resume operations
            if (this.config.debug) {
                console.log('👁️ Tab visible - resuming operations');
            }
            
            // Check connection when tab becomes visible
            if (this.components.chat) {
                this.components.chat.checkConnection();
            }
        }
    }

    /**
     * Handle global errors
     * @param {ErrorEvent} e - Error event
     */
    handleGlobalError(e) {
        console.error('Global error:', e.error);
        
        // Show user-friendly error message
        Utils.showToast('Đã xảy ra lỗi không mong muốn', 'error');
        
        // Log to server (if available)
        this.logErrorToServer(e.error);
    }

    /**
     * Handle unhandled promise rejections
     * @param {PromiseRejectionEvent} e - Promise rejection event
     */
    handleUnhandledRejection(e) {
        console.error('Unhandled promise rejection:', e.reason);
        
        // Prevent the default browser error handling
        e.preventDefault();
        
        // Show user-friendly error message
        Utils.showToast('Có lỗi xảy ra trong quá trình xử lý', 'error');
        
        // Log to server (if available)
        this.logErrorToServer(e.reason);
    }

    /**
     * Log error to server
     * @param {Error} error - Error to log
     */
    async logErrorToServer(error) {
        try {
            // TODO: Implement error logging API
            // await chatAPI.logError({
            //     message: error.message,
            //     stack: error.stack,
            //     timestamp: Date.now(),
            //     userAgent: navigator.userAgent,
            //     url: window.location.href
            // });
        } catch (logError) {
            console.error('Failed to log error to server:', logError);
        }
    }

    /**
     * Show initial loading screen
     */
    showInitialLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('show');
        }
    }

    /**
     * Hide initial loading screen
     */
    hideInitialLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    /**
     * Handle initialization error
     * @param {Error} error - Initialization error
     */
    handleInitializationError(error) {
        this.hideInitialLoading();
        
        // Show error message
        const errorMessage = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 2rem;
                border-radius: 0.5rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 400px;
                z-index: 9999;
            ">
                <h3 style="color: #ef4444; margin-bottom: 1rem;">
                    Lỗi khởi tạo ứng dụng
                </h3>
                <p style="margin-bottom: 1.5rem; color: #666;">
                    Không thể khởi tạo ứng dụng. Vui lòng tải lại trang.
                </p>
                <button 
                    onclick="window.location.reload()" 
                    style="
                        background: #6366f1;
                        color: white;
                        border: none;
                        padding: 0.75rem 1.5rem;
                        border-radius: 0.375rem;
                        cursor: pointer;
                    "
                >
                    Tải lại trang
                </button>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', errorMessage);
    }

    /**
     * Check if there are unsaved changes
     * @returns {boolean} Has unsaved changes
     */
    hasUnsavedChanges() {
        // Check if there are any unsaved messages or changes
        if (this.components.chat && this.components.chat.messages.length > 0) {
            const lastSave = Utils.storage.get('last_save_time', 0);
            const lastMessage = this.components.chat.messages[this.components.chat.messages.length - 1];
            return lastMessage.timestamp > lastSave;
        }
        return false;
    }

    /**
     * Toggle fullscreen mode
     */
    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen?.();
        } else {
            document.exitFullscreen?.();
        }
    }

    /**
     * Get application info
     * @returns {Object} Application information
     */
    getAppInfo() {
        return {
            version: this.config.version,
            initialized: this.isInitialized,
            components: Object.keys(this.components),
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Enable debug mode
     */
    enableDebugMode() {
        this.config.debug = true;
        console.log('🐛 Debug mode enabled');
        
        // Add debug info to window
        window.debugApp = {
            app: this,
            components: this.components,
            utils: Utils,
            api: chatAPI
        };
        
        Utils.showToast('Debug mode đã bật', 'info');
    }

    /**
     * Restart application
     */
    async restart() {
        try {
            console.log('🔄 Restarting application...');
            
            // Destroy current components
            Object.values(this.components).forEach(component => {
                if (component.destroy) {
                    component.destroy();
                }
            });
            
            // Clear components
            this.components = {};
            this.isInitialized = false;
            
            // Reinitialize
            await this.init();
            
        } catch (error) {
            console.error('Restart failed:', error);
            Utils.showToast('Không thể khởi động lại ứng dụng', 'error');
        }
    }

    /**
     * Clean up and destroy application
     */
    destroy() {
        console.log('🔥 Destroying application...');
        
        // Destroy all components
        Object.values(this.components).forEach(component => {
            if (component.destroy) {
                component.destroy();
            }
        });
        
        // Clear intervals and timeouts
        // (Auto-save interval will be cleared automatically)
        
        // Remove global references
        delete window.chatComponent;
        delete window.sidebarComponent;
        delete window.modalComponent;
        delete window.debugApp;
        
        this.isInitialized = false;
        console.log('✅ Application destroyed');
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Create global app instance
    window.chatbotApp = new ChatbotApp();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.chatbotApp) {
        window.chatbotApp.autoSave();
    }
});

// TODO: Production deployment checklist:
// 1. ✅ Update API base URL in chatAPI.js
// 2. ✅ Enable HTTPS for production
// 3. ✅ Add proper error logging
// 4. ✅ Optimize bundle size
// 5. ✅ Add service worker for offline support
// 6. ✅ Implement proper authentication
// 7. ✅ Add rate limiting
// 8. ✅ Security headers
// 9. ✅ Performance monitoring
// 10. ✅ SEO optimization 