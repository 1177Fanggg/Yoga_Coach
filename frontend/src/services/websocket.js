// WebSocket 服務 - 處理即時回饋推送
class WebSocketService {
    constructor() {
        this.ws = null;
        this.sessionId = null;
        this.listeners = [];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    /**
     * 連接 WebSocket
     * @param {string} sessionId - Session ID
     */
    connect(sessionId) {
        this.sessionId = sessionId;
        const wsUrl = 'ws://localhost:8000/ws';

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('[WebSocket] 已連接');
                this.reconnectAttempts = 0;

                // 發送 session_id
                this.ws.send(JSON.stringify({ session_id: sessionId }));
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('[WebSocket] 收到訊息:', data);
                    this.notifyListeners(data);
                } catch (error) {
                    console.error('[WebSocket] 解析訊息失敗:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('[WebSocket] 錯誤:', error);
            };

            this.ws.onclose = () => {
                console.log('[WebSocket] 連接關閉');
                this.handleReconnect();
            };
        } catch (error) {
            console.error('[WebSocket] 連接失敗:', error);
        }
    }

    /**
     * 處理重新連接
     */
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts && this.sessionId) {
            this.reconnectAttempts++;
            console.log(`[WebSocket] 嘗試重新連接 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

            setTimeout(() => {
                this.connect(this.sessionId);
            }, 2000 * this.reconnectAttempts); // 指數退避
        }
    }

    /**
     * 新增監聽器
     * @param {Function} callback - 回調函數
     */
    addListener(callback) {
        if (typeof callback === 'function') {
            this.listeners.push(callback);
        }
    }

    /**
     * 移除監聽器
     * @param {Function} callback - 回調函數
     */
    removeListener(callback) {
        this.listeners = this.listeners.filter((listener) => listener !== callback);
    }

    /**
     * 通知所有監聽器
     * @param {Object} data - 資料
     */
    notifyListeners(data) {
        this.listeners.forEach((listener) => {
            try {
                listener(data);
            } catch (error) {
                console.error('[WebSocket] 監聽器錯誤:', error);
            }
        });
    }

    /**
     * 發送訊息
     * @param {Object} message - 訊息物件
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('[WebSocket] 連接未開啟，無法發送訊息');
        }
    }

    /**
     * 斷開連接
     */
    disconnect() {
        if (this.ws) {
            this.sessionId = null;
            this.reconnectAttempts = this.maxReconnectAttempts; // 防止自動重連
            this.ws.close();
            this.ws = null;
            console.log('[WebSocket] 已斷開連接');
        }
    }

    /**
     * 檢查連接狀態
     * @returns {boolean} 是否已連接
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// 建立單例
const websocketService = new WebSocketService();

export default websocketService;
