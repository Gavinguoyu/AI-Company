/**
 * 老板决策面板
 * 负责显示决策请求和收集用户选择
 */
export class BossPanel {
    constructor(wsClient) {
        this.wsClient = wsClient;
        this.currentDecision = null;
        
        // 监听决策请求事件
        this.wsClient.on('boss_decision', (data) => this.showDecision(data));
        
        console.log('✅ BossPanel 初始化完成');
    }

    /**
     * 显示决策请求
     * @param {Object} data - 决策数据
     */
    showDecision(data) {
        console.log('🤔 收到决策请求:', data);
        
        this.currentDecision = data;
        
        // 创建并显示模态窗口
        const modal = this.createModal(data);
        document.body.appendChild(modal);
        
        // 添加淡入动画
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);
    }

    /**
     * 创建决策模态窗口
     * @param {Object} data - 决策数据
     */
    createModal(data) {
        const modal = document.createElement('div');
        modal.className = 'modal boss-decision-modal';
        
        // 提取数据
        const title = data.title || '需要您的决策';
        const question = data.question || '';
        const options = data.options || ['继续', '取消'];
        const decisionId = data.decision_id;
        
        modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>👔 ${title}</h2>
                </div>
                <div class="modal-body">
                    <p class="decision-question">${this.escapeHtml(question)}</p>
                    <div class="decision-options">
                        ${options.map((option, index) => `
                            <button class="decision-btn" data-option="${this.escapeHtml(option)}" data-index="${index}">
                                ${this.escapeHtml(option)}
                            </button>
                        `).join('')}
                    </div>
                </div>
                <div class="modal-footer">
                    <small>请选择一个选项以继续工作流</small>
                </div>
            </div>
        `;
        
        // 绑定按钮点击事件
        modal.querySelectorAll('.decision-btn').forEach(btn => {
            btn.onclick = () => {
                const choice = btn.dataset.option;
                this.submitDecision(decisionId, choice);
                this.closeModal(modal);
            };
        });
        
        // 点击遮罩层不关闭（强制用户做决策）
        modal.querySelector('.modal-overlay').onclick = (e) => {
            e.stopPropagation();
            // 轻微震动提示
            modal.querySelector('.modal-content').classList.add('shake');
            setTimeout(() => {
                modal.querySelector('.modal-content').classList.remove('shake');
            }, 500);
        };
        
        return modal;
    }

    /**
     * 提交决策结果
     * @param {string} decisionId - 决策ID
     * @param {string} choice - 用户选择
     */
    submitDecision(decisionId, choice) {
        console.log('📤 提交决策:', decisionId, '->', choice);
        
        // 通过 WebSocket 发送决策响应
        this.wsClient.send({
            type: 'boss_decision_response',
            decision_id: decisionId,
            choice: choice
        });
        
        // 清空当前决策
        this.currentDecision = null;
    }

    /**
     * 关闭模态窗口
     * @param {HTMLElement} modal - 模态窗口元素
     */
    closeModal(modal) {
        // 淡出动画
        modal.classList.remove('show');
        
        // 等待动画结束后移除元素
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    }

    /**
     * 转义 HTML 特殊字符
     * @param {string} text - 原始文本
     * @returns {string} 转义后的文本
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

export default BossPanel;
