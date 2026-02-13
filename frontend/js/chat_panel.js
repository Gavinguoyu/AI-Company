/**
 * 实时对话面板
 * 显示Agent之间的实时消息交流
 */
export class ChatPanel {
    constructor(containerElement) {
        this.container = containerElement;
        this.messages = [];
        this.maxMessages = 100; // 最多保留100条消息
    }

    /**
     * 添加消息
     */
    addMessage(data) {
        const message = {
            from: data.from || '未知',
            to: data.to || '所有人',
            content: data.content || '',
            timestamp: data.timestamp || new Date().toISOString(),
            type: data.type || 'message'
        };

        this.messages.push(message);

        // 限制消息数量
        if (this.messages.length > this.maxMessages) {
            this.messages.shift();
        }

        this.render();
        this.scrollToBottom();
    }

    /**
     * 清空欢迎消息
     */
    clearWelcome() {
        const welcome = this.container.querySelector('.chat-welcome');
        if (welcome) {
            welcome.remove();
        }
    }

    /**
     * 渲染消息列表
     */
    render() {
        // 清空欢迎消息
        this.clearWelcome();

        // 如果没有消息，显示欢迎消息
        if (this.messages.length === 0) {
            this.container.innerHTML = '<div class="chat-welcome">等待Agent消息...</div>';
            return;
        }

        // 渲染所有消息
        this.container.innerHTML = this.messages.map(msg => this.renderMessage(msg)).join('');
    }

    /**
     * 渲染单条消息
     */
    renderMessage(message) {
        const time = this.formatTime(message.timestamp);
        const fromName = this.getAgentName(message.from);
        const toName = this.getAgentName(message.to);

        return `
            <div class="chat-message">
                <div class="message-header">
                    <div>
                        <span class="message-from">${fromName}</span>
                        <span class="message-to">→ ${toName}</span>
                    </div>
                    <span class="message-time">${time}</span>
                </div>
                <div class="message-content">${this.escapeHtml(message.content)}</div>
            </div>
        `;
    }

    /**
     * 格式化时间
     */
    formatTime(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (error) {
            return '时间未知';
        }
    }

    /**
     * 获取Agent显示名称
     */
    getAgentName(agentId) {
        const agentNames = {
            'pm': '项目经理',
            'planner': '游戏策划',
            'programmer': '程序员',
            'artist': '美术设计',
            'tester': '测试工程师',
            'boss': '老板',
            'all': '所有人'
        };
        return agentNames[agentId] || agentId;
    }

    /**
     * 转义HTML特殊字符
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 滚动到底部
     */
    scrollToBottom() {
        this.container.scrollTop = this.container.scrollHeight;
    }

    /**
     * 清空所有消息
     */
    clear() {
        this.messages = [];
        this.render();
    }
}

export default ChatPanel;
