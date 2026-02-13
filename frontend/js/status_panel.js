/**
 * 项目状态面板
 * 显示当前项目信息和Agent工作状态
 */
export class StatusPanel {
    constructor(containerElement) {
        this.container = containerElement;
        this.projectName = document.getElementById('project-name');
        this.projectPhase = document.getElementById('project-phase');
        this.projectProgress = document.getElementById('project-progress');
        this.progressText = document.getElementById('progress-text');
        this.agentStatusList = document.getElementById('agent-status-list');
        
        this.agentStates = {};
        this.currentProject = null;
    }

    /**
     * 更新项目信息
     */
    updateProject(projectData) {
        this.currentProject = projectData;
        
        if (this.projectName) {
            this.projectName.textContent = projectData.name || '无';
        }
        
        if (this.projectPhase) {
            const phaseName = this.getPhaseName(projectData.phase);
            this.projectPhase.textContent = phaseName;
        }
        
        if (projectData.progress !== undefined) {
            this.updateProgress(projectData.progress);
        }
    }

    /**
     * 更新进度条
     */
    updateProgress(progress) {
        const progressValue = Math.min(100, Math.max(0, progress));
        
        if (this.projectProgress) {
            this.projectProgress.style.width = `${progressValue}%`;
        }
        
        if (this.progressText) {
            this.progressText.textContent = `${progressValue}%`;
        }
    }

    /**
     * 更新单个Agent状态
     */
    updateAgentStatus(data) {
        const agentId = data.agent_id || data.agentId;
        const status = data.status || 'idle';
        const currentTask = data.current_task || data.currentTask || '';

        this.agentStates[agentId] = {
            status,
            currentTask
        };

        this.renderAgentList();
    }

    /**
     * 渲染Agent状态列表
     */
    renderAgentList() {
        if (!this.agentStatusList) return;

        // 定义Agent顺序
        const agentOrder = ['pm', 'planner', 'programmer', 'artist', 'tester'];
        
        // 确保所有Agent都有初始状态
        agentOrder.forEach(id => {
            if (!this.agentStates[id]) {
                this.agentStates[id] = { status: 'idle', currentTask: '' };
            }
        });

        // 渲染
        this.agentStatusList.innerHTML = agentOrder
            .map(id => this.renderAgentItem(id, this.agentStates[id]))
            .join('');
    }

    /**
     * 渲染单个Agent状态项
     */
    renderAgentItem(agentId, state) {
        const name = this.getAgentName(agentId);
        const statusText = this.getStatusText(state.status);
        const statusClass = `agent-status ${state.status}`;

        return `
            <div class="agent-status-item">
                <span class="agent-status-name">${name}</span>
                <span class="${statusClass}">${statusText}</span>
            </div>
        `;
    }

    /**
     * 获取阶段名称
     */
    getPhaseName(phase) {
        const phaseNames = {
            'initiation': '立项',
            'planning': '策划',
            'tech_design': '技术设计',
            'parallel_dev': '并行开发',
            'integration': '整合',
            'testing': '测试',
            'delivery': '交付',
            'completed': '已完成'
        };
        return phaseNames[phase] || phase || '-';
    }

    /**
     * 获取Agent名称
     */
    getAgentName(agentId) {
        const agentNames = {
            'pm': '项目经理',
            'planner': '游戏策划',
            'programmer': '程序员',
            'artist': '美术设计',
            'tester': '测试工程师'
        };
        return agentNames[agentId] || agentId;
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
     * 清空状态
     */
    clear() {
        this.currentProject = null;
        this.agentStates = {};
        
        if (this.projectName) this.projectName.textContent = '无';
        if (this.projectPhase) this.projectPhase.textContent = '-';
        if (this.progressText) this.progressText.textContent = '0%';
        if (this.projectProgress) this.projectProgress.style.width = '0%';
        if (this.agentStatusList) this.agentStatusList.innerHTML = '';
    }
}

export default StatusPanel;
