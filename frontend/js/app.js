/**
 * 主应用入口 – 深色极客风全屏版
 * 整合办公室场景、Agent详情面板、老板对话框、系统日志
 */
import WebSocketClient from './websocket.js';
import OfficeScene     from './office_scene.js';
import AgentDetailPanel from './agent_detail_panel.js';
import KnowledgeBase   from './knowledge_base.js';

/* ═══════════════════════════════════════════
   常量
   ═══════════════════════════════════════════ */

const TEMPLATES = {
    snake:  '制作一个经典的贪吃蛇游戏。玩家控制一条蛇在地图上移动，通过吃食物增长身体，同时避免撞到自己或墙壁。',
    flappy: '制作一个Flappy Bird风格的游戏。玩家点击屏幕让小鸟飞起来，需要在管道之间穿梭。',
    2048:   '制作一个2048数字合并游戏。玩家通过滑动方向键合并相同数字的方块。',
    tetris: '制作一个俄罗斯方块游戏。不同形状的方块从顶部下落，玩家需要旋转和移动方块。',
    custom: ''
};

const PHASE_NAMES = {
    initiation: '立项', planning: '策划', tech_design: '技术设计',
    parallel_dev: '并行开发', integration: '整合', testing: '测试',
    delivery: '交付', completed: '已完成'
};

/* ═══════════════════════════════════════════
   主应用
   ═══════════════════════════════════════════ */

class App {
    constructor() {
        this.ws = null;
        this.officeScene = null;
        this.agentPanel = null;
        this.knowledgeBase = null;
        this.currentProjectId = null;
        this.logCount = 0;

        this.init();
    }

    init() {
        console.log('▶ App init');

        // 办公室场景
        this.officeScene = new OfficeScene(document.getElementById('office-canvas'));
        this.officeScene.onAgentClick = (id) => this.onAgentClicked(id);

        // Agent详情面板
        this.agentPanel = new AgentDetailPanel();
        
        // 知识库
        this.knowledgeBase = new KnowledgeBase();

        // WebSocket
        this.initWebSocket();

        // UI事件
        this.initUI();

        // 老板对话框
        this.initBossChat();

        // 加载项目
        this.loadProjects();

        console.log('✅ App ready');
    }

    /* ═══════════ WebSocket ═══════════ */

    initWebSocket() {
        const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = location.host || 'localhost:8000';
        this.ws = new WebSocketClient(`${protocol}//${host}/ws`);

        this.ws.on('connection', d => this.updateWsBadge(d.status));

        // Agent 消息
        this.ws.on('agent_message', data => {
            // 1) 归类到Agent面板
            this.agentPanel.addMessage(data);

            // 2) 办公室场景动画
            this.officeScene?.showMessage(data.from, data.to, data.content);

            // 3) 底部日志只显示简短摘要
            const summary = data.content?.length > 60
                ? data.content.substring(0, 60) + '…'
                : data.content;
            this.addLog('agent', `${this.agentLabel(data.from)} → ${this.agentLabel(data.to)}: ${summary}`);
        });

        // Agent 状态
        this.ws.on('agent_status', data => {
            const id = data.agent_id || data.agentId;
            const status = data.status || 'idle';
            this.officeScene?.updateAgentStatus(id, status, data.current_task || '');
            this.agentPanel.updateStatus(id, status);
            this.addLog('agent', `${this.agentLabel(id)} → ${status.toUpperCase()}`);
        });

        // 阶段变化
        this.ws.on('phase_change', data => {
            this.updateProjectInfo(data.project_id, data.new_phase, data.progress);
            this.addLog('phase', `阶段切换 → ${PHASE_NAMES[data.new_phase] || data.new_phase}`);
            
            // 如果进入交付阶段或完成，显示试玩按钮并更新游戏展示区
            if (data.new_phase === 'delivery' || data.new_phase === 'completed' || data.progress >= 90) {
                this.showPlayButton();
                // P8-2: 添加游戏到办公室展示区
                const gameUrl = `/projects/${data.project_id || this.currentProjectId}/output/index.html`;
                this.officeScene?.addGameToShowcase(
                    data.project_id || this.currentProjectId || '新游戏',
                    gameUrl,
                    new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
                );
            }
        });

        // 老板决策
        this.ws.on('boss_decision', data => {
            this.showBossDecision(data);
            this.addLog('boss', `需要老板决策: ${data.question}`);
        });

        // 文件更新
        this.ws.on('file_update', data => {
            this.addLog('system', `文件更新: ${data.file_path}`);
        });
        
        // Agent产出文件
        this.ws.on('file_output', data => {
            // 添加到Agent详情面板
            this.agentPanel.addOutput(data.agent_id, {
                file_path: data.file_path,
                file_type: data.file_type,
                summary: data.summary,
                timestamp: data.timestamp
            });
            
            this.addLog('agent', `${this.agentLabel(data.agent_id)} 产出: ${data.summary || data.file_path}`);
        });

        // 任务完成
        this.ws.on('task_complete', data => {
            this.addLog('phase', `✓ 任务完成: ${data.task_name}`);
        });

        // 错误
        this.ws.on('error_alert', data => {
            this.addLog('error', `错误: ${data.error_message}`);
        });

        this.ws.connect();
    }

    updateWsBadge(status) {
        const el = document.getElementById('ws-status');
        if (!el) return;
        if (status === 'connected') {
            el.textContent = '● ONLINE';
            el.className = 'ws-badge online';
        } else {
            el.textContent = '● OFFLINE';
            el.className = 'ws-badge offline';
        }
    }

    /* ═══════════ Agent 点击 ═══════════ */

    onAgentClicked(agentId) {
        this.agentPanel.open(agentId);
    }

    /* ═══════════ 底部日志 ═══════════ */

    addLog(tag, text) {
        const container = document.getElementById('log-messages');
        if (!container) return;

        // 清空欢迎文字
        const welcome = container.querySelector('.log-welcome');
        if (welcome) welcome.remove();

        const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.innerHTML = `<span class="log-time">${now}</span><span class="log-tag ${tag}">[${tag}]</span><span class="log-body">${this.esc(text)}</span>`;
        container.appendChild(entry);
        container.scrollTop = container.scrollHeight;

        this.logCount++;
        const countEl = document.getElementById('log-count');
        if (countEl) countEl.textContent = this.logCount;
    }

    /* ═══════════ 老板对话框 ═══════════ */

    initBossChat() {
        const toggle = document.getElementById('boss-chat-toggle');
        const chat = document.getElementById('boss-chat');
        toggle?.addEventListener('click', () => {
            chat.classList.toggle('collapsed');
            // 清除未读
            const badge = document.getElementById('boss-unread');
            if (badge) { badge.style.display = 'none'; badge.textContent = '0'; }
        });
    }

    showBossDecision(data) {
        // 1. 显示顶栏决策指示灯
        this.showDecisionIndicator();
        
        // 2. 弹出模态决策窗口（优先级高）
        this.showDecisionModal(data);
        
        // 3. 同时更新老板对话框（备用）
        const chat = document.getElementById('boss-chat');
        const msgContainer = document.getElementById('boss-messages');
        const actionsContainer = document.getElementById('boss-actions');
        if (!chat || !msgContainer || !actionsContainer) return;

        // 展开对话框
        chat.classList.remove('collapsed');

        // 清空欢迎消息
        const welcome = msgContainer.querySelector('.boss-welcome');
        if (welcome) welcome.remove();

        // 显示来自Agent的决策请求
        const msg = document.createElement('div');
        msg.className = 'boss-msg from-agent';
        msg.innerHTML = `
            <div class="boss-msg-sender">${this.agentLabel(data.agent_id || 'pm')}</div>
            <div>${this.esc(data.question || '需要您的决策')}</div>
        `;
        msgContainer.appendChild(msg);
        msgContainer.scrollTop = msgContainer.scrollHeight;

        // 显示决策按钮
        const options = data.options || ['继续', '取消'];
        actionsContainer.style.display = 'flex';
        actionsContainer.innerHTML = options.map((opt, i) =>
            `<button class="boss-decision-btn" data-option="${this.esc(opt)}" data-id="${data.decision_id || ''}">${this.esc(opt)}</button>`
        ).join('');

        actionsContainer.querySelectorAll('.boss-decision-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const choice = btn.dataset.option;
                const decisionId = btn.dataset.id;

                // 发送决策
                this.submitDecision(decisionId, choice);

                // 显示老板的回复
                const reply = document.createElement('div');
                reply.className = 'boss-msg from-boss';
                reply.innerHTML = `<div class="boss-msg-sender">👔 老板</div><div>我选择: ${this.esc(choice)}</div>`;
                msgContainer.appendChild(reply);
                msgContainer.scrollTop = msgContainer.scrollHeight;

                // 隐藏按钮
                actionsContainer.style.display = 'none';
            });
        });

        // 未读提示
        if (chat.classList.contains('collapsed')) {
            const badge = document.getElementById('boss-unread');
            if (badge) {
                badge.style.display = 'inline';
                badge.textContent = parseInt(badge.textContent || '0') + 1;
            }
        }
    }
    
    /* ═══════════ 决策指示灯 ═══════════ */
    
    showDecisionIndicator() {
        const indicator = document.getElementById('decision-indicator');
        const divider = document.getElementById('decision-divider');
        if (indicator) {
            indicator.style.display = 'inline-block';
            indicator.onclick = () => {
                // 点击指示灯可以重新打开决策窗口
                const modal = document.getElementById('decision-modal');
                if (modal) modal.style.display = 'flex';
            };
        }
        if (divider) divider.style.display = 'inline';
    }
    
    hideDecisionIndicator() {
        const indicator = document.getElementById('decision-indicator');
        const divider = document.getElementById('decision-divider');
        if (indicator) indicator.style.display = 'none';
        if (divider) divider.style.display = 'none';
    }
    
    /* ═══════════ 决策模态弹窗 ═══════════ */
    
    showDecisionModal(data) {
        const modal = document.getElementById('decision-modal');
        const titleEl = document.getElementById('decision-title');
        const questionEl = document.getElementById('decision-question');
        const optionsEl = document.getElementById('decision-options');
        const overlay = modal?.querySelector('.modal-overlay');
        const box = modal?.querySelector('.decision-box');
        
        if (!modal || !titleEl || !questionEl || !optionsEl) return;
        
        // 设置标题和问题
        const title = data.question?.split(':')[0] || '老板决策';
        const question = data.question || '需要您的决策';
        titleEl.textContent = title;
        questionEl.textContent = question;
        
        // 生成决策选项按钮
        const options = data.options || ['继续', '取消'];
        optionsEl.innerHTML = options.map(opt => 
            `<button class="decision-option-btn" data-option="${this.esc(opt)}" data-id="${data.decision_id || ''}">${this.esc(opt)}</button>`
        ).join('');
        
        // 绑定按钮事件
        optionsEl.querySelectorAll('.decision-option-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const choice = btn.dataset.option;
                const decisionId = btn.dataset.id;
                
                // 提交决策
                this.submitDecision(decisionId, choice);
                
                // 关闭模态窗口
                modal.style.display = 'none';
                
                // 隐藏指示灯
                this.hideDecisionIndicator();
            });
        });
        
        // 点击遮罩层震动提示（禁止关闭）
        overlay?.addEventListener('click', () => {
            box?.classList.add('shake');
            setTimeout(() => box?.classList.remove('shake'), 500);
        });
        
        // 显示模态窗口
        modal.style.display = 'flex';
    }
    
    /* ═══════════ 提交决策 ═══════════ */
    
    submitDecision(decisionId, choice) {
        // 发送决策到后端
        this.ws.send({ 
            type: 'boss_decision_response', 
            decision_id: decisionId, 
            choice: choice 
        });
        
        this.addLog('boss', `老板决策 → ${choice}`);
    }

    /* ═══════════ 项目信息 ═══════════ */

    updateProjectInfo(projectId, phase, progress) {
        if (projectId) this.currentProjectId = projectId;
        const nameEl = document.getElementById('project-name-display');
        const phaseEl = document.getElementById('project-phase-display');
        const barEl = document.getElementById('progress-bar-mini');
        const pctEl = document.getElementById('progress-pct');

        if (nameEl && projectId) nameEl.textContent = projectId;
        if (phaseEl && phase) phaseEl.textContent = (PHASE_NAMES[phase] || phase).toUpperCase();
        if (barEl && progress !== undefined) barEl.style.width = Math.min(100, progress) + '%';
        if (pctEl && progress !== undefined) pctEl.textContent = Math.min(100, progress) + '%';
    }

    /* ═══════════ UI 事件 ═══════════ */

    initUI() {
        const createBtn = document.getElementById('create-project-btn');
        const kbBtn     = document.getElementById('knowledge-base-btn');
        const modal     = document.getElementById('create-project-modal');
        const closeBtn  = document.getElementById('close-modal');
        const cancelBtn = document.getElementById('cancel-btn');
        const form      = document.getElementById('create-project-form');

        const openModal  = () => { if (modal) modal.style.display = 'flex'; };
        const closeModal = () => { if (modal) modal.style.display = 'none'; form?.reset(); };

        createBtn?.addEventListener('click', openModal);
        kbBtn?.addEventListener('click', () => this.knowledgeBase.open(this.currentProjectId));
        
        // 试玩游戏按钮
        const playBtn = document.getElementById('play-game-btn');
        playBtn?.addEventListener('click', () => this.playGame());
        closeBtn?.addEventListener('click', closeModal);
        cancelBtn?.addEventListener('click', closeModal);
        modal?.querySelector('.modal-overlay')?.addEventListener('click', closeModal);

        // 模板
        const descEl = document.getElementById('input-project-desc');
        document.querySelectorAll('.tpl-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tpl-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const t = btn.dataset.template;
                if (TEMPLATES[t] && descEl) descEl.value = TEMPLATES[t];
            });
        });

        // 提交
        form?.addEventListener('submit', async e => {
            e.preventDefault();
            const fd = new FormData(form);
            const name = fd.get('name');
            const desc = fd.get('description');
            if (!name || !desc) return;

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = '创建中…'; }

            try {
                const res = await fetch('/api/project/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ project_name: name, game_idea: desc })
                });
                const data = await res.json();
                if (data.success && data.project_id) {
                    closeModal();
                    this.selectProject(data.project_id);
                    this.addLog('system', `项目创建成功: ${data.project_id}`);
                } else {
                    throw new Error(data.message || '创建失败');
                }
            } catch (err) {
                this.addLog('error', `创建项目失败: ${err.message}`);
                alert('创建失败: ' + err.message);
            } finally {
                if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = '▶ START'; }
            }
        });
    }

    /* ═══════════ 项目管理 ═══════════ */

    async loadProjects() {
        try {
            const res = await fetch('/api/projects');
            const data = await res.json();
            if (data.projects?.length > 0) {
                this.selectProject(data.projects[0].id);
            }
        } catch (e) {
            console.warn('加载项目列表失败', e);
        }
    }

    async selectProject(projectId) {
        this.currentProjectId = projectId;
        if (this.ws?.isConnected()) this.ws.subscribeProject(projectId);

        try {
            const res = await fetch(`/api/project/${projectId}/status`);
            const data = await res.json();
            if (data.project) {
                this.updateProjectInfo(
                    data.project.name || projectId,
                    data.project.phase || 'unknown',
                    data.project.progress || 0
                );
            }
        } catch (e) {
            console.warn('加载项目详情失败', e);
        }
    }

    /* ═══════════ 工具 ═══════════ */

    agentLabel(id) {
        return { pm: 'PM', planner: '策划', programmer: '程序', artist: '美术', tester: '测试', boss: '老板', all: '全体', system: 'SYS' }[id] || id;
    }

    esc(text) {
        const d = document.createElement('div');
        d.textContent = text || '';
        return d.innerHTML;
    }
    
    /* ═══════════ 试玩游戏 ═══════════ */
    
    showPlayButton() {
        const playBtn = document.getElementById('play-game-btn');
        if (playBtn) playBtn.style.display = 'inline-block';
    }
    
    playGame() {
        if (!this.currentProjectId) {
            alert('请先选择项目');
            return;
        }
        
        // 在新窗口打开游戏
        const gameUrl = `/projects/${this.currentProjectId}/output/index.html`;
        const gameWindow = window.open(gameUrl, 'game_window', 'width=800,height=600');
        
        if (!gameWindow) {
            alert('无法打开游戏窗口，请检查浏览器弹窗设置');
            return;
        }
        
        // 显示反馈提示
        setTimeout(() => {
            if (confirm('试玩完成后，是否要提交反馈？')) {
                this.showFeedbackForm();
            }
        }, 5000);  // 5秒后提示
    }
    
    showFeedbackForm() {
        const feedback = prompt('请描述您发现的问题或建议：');
        if (!feedback || !feedback.trim()) return;
        
        this.submitFeedback(feedback);
    }
    
    async submitFeedback(feedback) {
        try {
            const res = await fetch(`/api/project/${this.currentProjectId}/feedback`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    feedback: feedback,
                    severity: 'normal'
                })
            });
            
            const data = await res.json();
            
            if (data.success) {
                this.addLog('boss', `反馈已提交: ${feedback.substring(0, 50)}...`);
                alert('反馈已提交，AI团队将进行修复');
            } else {
                alert('提交失败: ' + (data.message || '未知错误'));
            }
        } catch (err) {
            console.error('提交反馈失败:', err);
            alert('提交失败: ' + err.message);
        }
    }
}

/* ═══════════ 启动 ═══════════ */

document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

export default App;
