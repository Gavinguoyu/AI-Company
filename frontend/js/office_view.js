/**
 * 办公室视图
 * 显示虚拟办公室中的5个Agent
 */
export class OfficeView {
    constructor(containerElement) {
        this.container = containerElement;
        this.agents = this.initAgents();
        this.render();
    }

    /**
     * 初始化Agent列表
     */
    initAgents() {
        return [
            {
                id: 'pm',
                name: '项目经理',
                avatar: '👔',
                status: 'idle',
                currentTask: ''
            },
            {
                id: 'planner',
                name: '游戏策划',
                avatar: '📋',
                status: 'idle',
                currentTask: ''
            },
            {
                id: 'programmer',
                name: '程序员',
                avatar: '💻',
                status: 'idle',
                currentTask: ''
            },
            {
                id: 'artist',
                name: '美术设计',
                avatar: '🎨',
                status: 'idle',
                currentTask: ''
            },
            {
                id: 'tester',
                name: '测试工程师',
                avatar: '🔍',
                status: 'idle',
                currentTask: ''
            }
        ];
    }

    /**
     * 更新Agent状态
     */
    updateAgentStatus(data) {
        const agentId = data.agent_id || data.agentId;
        const agent = this.agents.find(a => a.id === agentId);
        
        if (agent) {
            agent.status = data.status || 'idle';
            agent.currentTask = data.current_task || data.currentTask || '';
            this.render();
        }
    }

    /**
     * 显示Agent之间的通信（视觉效果）
     */
    showCommunication(fromId, toId) {
        // 简单版本：高亮发送者和接收者
        const fromAgent = this.agents.find(a => a.id === fromId);
        const toAgent = this.agents.find(a => a.id === toId);

        if (fromAgent) {
            fromAgent.status = 'thinking';
        }
        if (toAgent && toAgent.id !== 'all') {
            toAgent.status = 'thinking';
        }

        this.render();

        // 2秒后恢复
        setTimeout(() => {
            if (fromAgent) fromAgent.status = 'working';
            if (toAgent) toAgent.status = 'working';
            this.render();
        }, 2000);
    }

    /**
     * 渲染办公室视图
     */
    render() {
        this.container.innerHTML = this.agents
            .map(agent => this.renderAgent(agent))
            .join('');
    }

    /**
     * 渲染单个Agent卡片
     */
    renderAgent(agent) {
        const statusText = this.getStatusText(agent.status);
        const statusClass = agent.status;

        return `
            <div class="agent-card" data-agent-id="${agent.id}">
                <div class="agent-avatar">${agent.avatar}</div>
                <div class="agent-info">
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-role">${agent.id}</div>
                    ${agent.currentTask ? `<div class="agent-task">${agent.currentTask}</div>` : ''}
                </div>
                <span class="agent-status ${statusClass}">${statusText}</span>
            </div>
        `;
    }

    /**
     * 获取状态文本
     */
    getStatusText(status) {
        const statusTexts = {
            'idle': '空闲',
            'thinking': '思考中',
            'working': '工作中',
            'waiting': '等待中'
        };
        return statusTexts[status] || status;
    }

    /**
     * 重置所有Agent状态
     */
    reset() {
        this.agents.forEach(agent => {
            agent.status = 'idle';
            agent.currentTask = '';
        });
        this.render();
    }
}

export default OfficeView;
