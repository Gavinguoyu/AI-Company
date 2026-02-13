/**
 * WebSocket客户端
 * 负责连接后端WebSocket服务，处理消息分发和自动重连
 */
export class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectInterval = 3000; // 3秒后重连
        this.listeners = {}; // 事件监听器
        this.isConnecting = false;
        this.shouldReconnect = true; // 是否应该重连
        this.clientId = this.generateClientId();
    }

    /**
     * 生成唯一的客户端ID
     */
    generateClientId() {
        return `web-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * 连接WebSocket服务器
     */
    connect() {
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
            console.log('⚠️ WebSocket已连接或正在连接中');
            return;
        }

        this.isConnecting = true;
        const wsUrl = `${this.url}/${this.clientId}`;
        console.log(`📡 正在连接WebSocket: ${wsUrl}`);

        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket连接成功');
                this.isConnecting = false;
                this.triggerEvent('connection', { status: 'connected' });
            };

            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('❌ 解析消息失败:', error, event.data);
                }
            };

            this.ws.onerror = (error) => {
                console.error('❌ WebSocket错误:', error);
                this.isConnecting = false;
                this.triggerEvent('connection', { status: 'error', error });
            };

            this.ws.onclose = (event) => {
                console.log('⚠️ WebSocket断开连接', event.code, event.reason);
                this.isConnecting = false;
                this.triggerEvent('connection', { status: 'disconnected' });
                
                // 自动重连
                if (this.shouldReconnect) {
                    console.log(`⏱️ ${this.reconnectInterval / 1000}秒后尝试重连...`);
                    setTimeout(() => this.connect(), this.reconnectInterval);
                }
            };
        } catch (error) {
            console.error('❌ 创建WebSocket连接失败:', error);
            this.isConnecting = false;
        }
    }

    /**
     * 处理收到的消息
     */
    handleMessage(message) {
        console.log('📨 收到消息:', message);
        
        const eventType = message.event;
        const data = message.data || message;

        // 分发给对应的监听器
        if (this.listeners[eventType]) {
            this.listeners[eventType].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`❌ 处理事件 ${eventType} 时出错:`, error);
                }
            });
        }

        // 通用监听器
        if (this.listeners['*']) {
            this.listeners['*'].forEach(callback => {
                try {
                    callback(message);
                } catch (error) {
                    console.error('❌ 处理通用事件时出错:', error);
                }
            });
        }
    }

    /**
     * 注册事件监听器
     * @param {string} eventType - 事件类型（如 'agent_message', 'agent_status' 等）
     * @param {Function} callback - 回调函数
     */
    on(eventType, callback) {
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
        }
        this.listeners[eventType].push(callback);
    }

    /**
     * 移除事件监听器
     */
    off(eventType, callback) {
        if (!this.listeners[eventType]) return;
        
        if (callback) {
            this.listeners[eventType] = this.listeners[eventType].filter(cb => cb !== callback);
        } else {
            delete this.listeners[eventType];
        }
    }

    /**
     * 触发事件
     */
    triggerEvent(eventType, data) {
        if (this.listeners[eventType]) {
            this.listeners[eventType].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`❌ 触发事件 ${eventType} 时出错:`, error);
                }
            });
        }
    }

    /**
     * 发送消息到服务器
     */
    send(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
            this.ws.send(messageStr);
            console.log('📤 发送消息:', message);
        } else {
            console.error('❌ WebSocket未连接，无法发送消息');
        }
    }

    /**
     * 订阅项目更新
     */
    subscribeProject(projectId) {
        this.send({
            action: 'subscribe_project',
            project_id: projectId
        });
    }

    /**
     * 取消订阅项目
     */
    unsubscribeProject(projectId) {
        this.send({
            action: 'unsubscribe_project',
            project_id: projectId
        });
    }

    /**
     * 关闭连接
     */
    close() {
        console.log('🔌 主动关闭WebSocket连接');
        this.shouldReconnect = false;
        if (this.ws) {
            this.ws.close();
        }
    }

    /**
     * 获取连接状态
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

export default WebSocketClient;
