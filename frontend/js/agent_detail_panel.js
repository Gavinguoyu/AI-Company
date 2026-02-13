/**
 * Agent 详情面板（右侧抽屉）
 * 点击办公室中的Agent后，滑出显示该Agent的所有消息和产出
 */

const AGENT_META = {
    pm:         { name: '项目经理',   emoji: '👨‍💼' },
    planner:    { name: '游戏策划',   emoji: '📋' },
    programmer: { name: '程序员',     emoji: '👨‍💻' },
    artist:     { name: '美术设计',   emoji: '🎨' },
    tester:     { name: '测试工程师', emoji: '🧪' }
};

export class AgentDetailPanel {
    constructor() {
        this.drawer   = document.getElementById('agent-drawer');
        this.elEmoji  = document.getElementById('drawer-emoji');
        this.elName   = document.getElementById('drawer-name');
        this.elStatus = document.getElementById('drawer-status');
        this.elContent = document.getElementById('drawer-content');
        this.closeBtn  = document.getElementById('drawer-close');

        this.currentAgentId = null;
        this.currentTab = 'messages';

        /** 按Agent分类存储消息  Map<agentId, Array<msg>> */
        this.messageStore = new Map();
        /** 按Agent分类存储产出  Map<agentId, Array<string>> */
        this.outputStore = new Map();

        // 初始化所有Agent的存储
        for (const id of Object.keys(AGENT_META)) {
            this.messageStore.set(id, []);
            this.outputStore.set(id, []);
        }

        this.bindEvents();
    }

    bindEvents() {
        // 关闭按钮
        this.closeBtn?.addEventListener('click', () => this.close());

        // Tab切换
        this.drawer?.querySelectorAll('.drawer-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.drawer.querySelectorAll('.drawer-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                this.currentTab = tab.dataset.tab;
                this.renderContent();
            });
        });
    }

    /* ───── 外部接口 ───── */

    /** 打开某个Agent的详情 */
    open(agentId) {
        const meta = AGENT_META[agentId];
        if (!meta) return;

        this.currentAgentId = agentId;
        this.elEmoji.textContent = meta.emoji;
        this.elName.textContent = meta.name;

        this.renderContent();
        this.drawer.classList.add('open');
    }

    close() {
        this.drawer.classList.remove('open');
        this.currentAgentId = null;
    }

    /** 更新Agent状态显示 */
    updateStatus(agentId, status) {
        if (agentId !== this.currentAgentId) return;
        const texts = { idle: 'IDLE', working: 'WORKING', communicating: 'COMMUNICATING', error: 'ERROR', thinking: 'THINKING' };
        const colors = { idle: '#8b949e', working: '#58a6ff', communicating: '#3fb950', error: '#f85149', thinking: '#d29922' };
        this.elStatus.textContent = texts[status] || status;
        this.elStatus.style.color = colors[status] || '#8b949e';
    }

    /** 收录消息（按Agent归类） */
    addMessage(data) {
        const msg = {
            from: data.from || '?',
            to: data.to || 'all',
            content: data.content || '',
            time: this.fmtTime(data.timestamp)
        };

        // 归入发送者
        const fromMsgs = this.messageStore.get(msg.from);
        if (fromMsgs) fromMsgs.push(msg);

        // 也归入接收者（如果不是广播）
        if (msg.to !== 'all' && msg.to !== 'boss') {
            const toMsgs = this.messageStore.get(msg.to);
            if (toMsgs && msg.from !== msg.to) toMsgs.push(msg);
        }

        // 如果当前打开的Agent的消息有更新，刷新面板
        if (this.currentAgentId && this.currentTab === 'messages' &&
            (msg.from === this.currentAgentId || msg.to === this.currentAgentId)) {
            this.renderContent();
        }
    }

    /** 添加Agent产出 */
    addOutput(agentId, fileData) {
        const store = this.outputStore.get(agentId);
        if (store) {
            // fileData可以是字符串（旧格式）或对象（新格式）
            if (typeof fileData === 'string') {
                store.push({ type: 'text', content: fileData });
            } else {
                store.push(fileData);
            }
        }
        if (agentId === this.currentAgentId && this.currentTab === 'output') {
            this.renderContent();
        }
    }

    /* ───── 渲染 ───── */

    renderContent() {
        if (!this.currentAgentId) return;

        switch (this.currentTab) {
            case 'messages': this.renderMessages(); break;
            case 'output':   this.renderOutput();   break;
            case 'files':    this.renderFiles();     break;
        }
    }

    renderMessages() {
        const msgs = this.messageStore.get(this.currentAgentId) || [];
        if (msgs.length === 0) {
            this.elContent.innerHTML = '<div class="drawer-empty">暂无消息记录</div>';
            return;
        }

        this.elContent.innerHTML = msgs.map(m => `
            <div class="drawer-msg">
                <div class="drawer-msg-header">
                    <span class="drawer-msg-from">${this.agentName(m.from)} → ${this.agentName(m.to)}</span>
                    <span class="drawer-msg-time">${m.time}</span>
                </div>
                <div class="drawer-msg-body">${this.esc(m.content)}</div>
            </div>
        `).join('');

        this.elContent.scrollTop = this.elContent.scrollHeight;
    }

    renderOutput() {
        const out = this.outputStore.get(this.currentAgentId) || [];
        if (out.length === 0) {
            this.elContent.innerHTML = '<div class="drawer-empty">暂无产出内容</div>';
            return;
        }
        
        this.elContent.innerHTML = out.map((item, idx) => {
            // 兼容旧格式（纯文本）和新格式（文件对象）
            if (typeof item === 'string' || item.type === 'text') {
                const text = typeof item === 'string' ? item : item.content;
                return `
                    <div class="drawer-msg" style="border-left-color: var(--green);">
                        <div class="drawer-msg-body">${this.esc(text)}</div>
                    </div>
                `;
            }
            
            // 新格式：文件对象
            const fileIcon = this.getFileIcon(item.file_type);
            const fileName = item.file_path?.split('/').pop() || '未命名文件';
            
            return `
                <div class="drawer-file-item" data-idx="${idx}">
                    <div class="drawer-file-icon">${fileIcon}</div>
                    <div class="drawer-file-info">
                        <div class="drawer-file-name">${this.esc(fileName)}</div>
                        <div class="drawer-file-summary">${this.esc(item.summary || item.file_path || '')}</div>
                        <div class="drawer-file-meta">
                            <span class="drawer-file-type">${item.file_type || 'file'}</span>
                            <span class="drawer-file-time">${this.fmtTime(item.timestamp)}</span>
                        </div>
                    </div>
                    <button class="drawer-file-view-btn" data-path="${this.esc(item.file_path)}">查看</button>
                </div>
            `;
        }).join('');
        
        // 绑定查看按钮事件
        this.elContent.querySelectorAll('.drawer-file-view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const filePath = btn.dataset.path;
                this.viewFile(filePath);
            });
        });
    }
    
    getFileIcon(fileType) {
        const icons = {
            document: '📄',
            code: '💻',
            config: '⚙️',
            asset: '🎨',
            text: '📝'
        };
        return icons[fileType] || '📁';
    }
    
    async viewFile(filePath) {
        if (!filePath || !window.app?.currentProjectId) return;
        
        try {
            const res = await fetch(`/api/project/${window.app.currentProjectId}/file?path=${encodeURIComponent(filePath)}`);
            const data = await res.json();
            
            if (data.success) {
                this.showFileModal(filePath, data.content);
            } else {
                alert('读取文件失败');
            }
        } catch (err) {
            console.error('读取文件失败:', err);
            alert('读取文件失败: ' + err.message);
        }
    }
    
    showFileModal(filePath, content) {
        // 创建简单的文件查看模态框
        const modal = document.createElement('div');
        modal.className = 'file-view-modal';
        modal.innerHTML = `
            <div class="file-view-overlay"></div>
            <div class="file-view-box">
                <div class="file-view-header">
                    <h3>${this.esc(filePath)}</h3>
                    <button class="file-view-close">✕</button>
                </div>
                <div class="file-view-content">
                    <pre><code>${this.esc(content)}</code></pre>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 关闭按钮
        const closeBtn = modal.querySelector('.file-view-close');
        const overlay = modal.querySelector('.file-view-overlay');
        
        const close = () => {
            modal.remove();
        };
        
        closeBtn.addEventListener('click', close);
        overlay.addEventListener('click', close);
        
        // ESC键关闭
        const handleEsc = (e) => {
            if (e.key === 'Escape') {
                close();
                document.removeEventListener('keydown', handleEsc);
            }
        };
        document.addEventListener('keydown', handleEsc);
    }

    renderFiles() {
        this.elContent.innerHTML = '<div class="drawer-empty">文件列表（开发中）</div>';
    }

    /* ───── 工具 ───── */

    agentName(id) {
        const names = { pm: '项目经理', planner: '策划', programmer: '程序员', artist: '美术', tester: '测试', boss: '老板', all: '全体', system: '系统' };
        return names[id] || id;
    }

    fmtTime(ts) {
        try { return new Date(ts || Date.now()).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }); }
        catch { return '--:--:--'; }
    }

    esc(text) {
        const d = document.createElement('div');
        d.textContent = text;
        return d.innerHTML;
    }
}

export default AgentDetailPanel;
