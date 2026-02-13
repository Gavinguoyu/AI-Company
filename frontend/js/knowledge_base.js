/**
 * 知识库浏览器
 * 展示项目的共享知识库和游戏产出文件
 */

export class KnowledgeBase {
    constructor() {
        this.modal = document.getElementById('knowledge-base-modal');
        this.closeBtn = document.getElementById('close-kb-modal');
        this.sharedList = document.getElementById('kb-shared-list');
        this.outputList = document.getElementById('kb-output-list');
        this.emptyView = this.modal?.querySelector('.kb-empty');
        this.fileView = this.modal?.querySelector('.kb-file-view');
        this.fileTitle = document.getElementById('kb-file-title');
        this.fileMeta = document.getElementById('kb-file-meta');
        this.fileCode = document.getElementById('kb-file-code');
        
        this.currentProjectId = null;
        this.currentFile = null;
        this.projectName = null;  // 添加projectName属性
        
        this.bindEvents();
    }
    
    bindEvents() {
        // 关闭按钮
        this.closeBtn?.addEventListener('click', () => this.close());
        
        // 点击遮罩层关闭
        this.modal?.querySelector('.modal-overlay')?.addEventListener('click', () => this.close());
    }
    
    close() {
        this.modal.style.display = 'none';
        this.currentProjectId = null;
        this.currentFile = null;
    }
    
    async open(projectId) {
        if (!projectId) {
            alert('请先选择或创建项目');
            return;
        }
        
        this.currentProjectId = projectId;
        this.modal.style.display = 'flex';
        
        // 获取project_name - 尝试从API获取或从project_id中提取
        await this.fetchProjectName(projectId);
        
        // 加载文件列表
        await this.loadFileList();
    }
    
    async fetchProjectName(projectId) {
        try {
            const res = await fetch(`/api/project/${projectId}/status`);
            if (res.ok) {
                const data = await res.json();
                // API直接返回扁平字段: { project_name, project_id, ... }
                if (data.project_name) {
                    this.projectName = data.project_name;
                    return;
                }
            }
            // fallback: 从project_id中提取（去掉时间戳后缀 _YYYYMMDD_HHMMSS）
            this.projectName = this._extractProjectName(projectId);
        } catch (e) {
            this.projectName = this._extractProjectName(projectId);
        }
    }
    
    _extractProjectName(projectId) {
        // "p10_counter_test_20260213_183223" -> "p10_counter_test"
        // "11_20260213_200851" -> "11"
        const parts = projectId.split('_');
        if (parts.length >= 3) {
            const last = parts[parts.length - 1];
            const secondLast = parts[parts.length - 2];
            if (/^\d{6}$/.test(last) && /^\d{8}$/.test(secondLast)) {
                return parts.slice(0, -2).join('_') || projectId;
            }
        }
        return projectId;
    }
    
    async loadFileList() {
        const pid = this.currentProjectId;
        
        // 加载共享知识库文件
        try {
            const sharedRes = await fetch(`/api/project/${pid}/files?directory=shared_knowledge`);
            const sharedData = await sharedRes.json();
            if (sharedData.success && sharedData.items) {
                this.renderFileList(this.sharedList, sharedData.items, 'shared_knowledge');
            } else {
                this.renderFileList(this.sharedList, [], 'shared_knowledge');
            }
        } catch (err) {
            console.warn('加载知识库文件失败:', err);
            this.renderFileList(this.sharedList, [], 'shared_knowledge');
        }
        
        // 加载游戏产出文件
        try {
            const outputRes = await fetch(`/api/project/${pid}/files?directory=output`);
            const outputData = await outputRes.json();
            if (outputData.success && outputData.items) {
                this.renderFileList(this.outputList, outputData.items, 'output');
            } else {
                this.renderFileList(this.outputList, [], 'output');
            }
        } catch (err) {
            console.warn('加载产出文件失败:', err);
            this.renderFileList(this.outputList, [], 'output');
        }
    }
    
    renderFileList(container, items, basePath) {
        if (!container) return;
        
        // 只显示文件，不显示目录
        const files = items.filter(item => item.type === 'file');
        
        if (files.length === 0) {
            container.innerHTML = '<div class="kb-file-item" style="cursor:default;">暂无文件</div>';
            return;
        }
        
        container.innerHTML = files.map(file => {
            const icon = this.getFileIcon(file.name);
            return `
                <div class="kb-file-item" data-path="${this.esc(file.path)}">
                    <span>${icon}</span>
                    <span>${this.esc(file.name)}</span>
                </div>
            `;
        }).join('');
        
        // 绑定点击事件
        container.querySelectorAll('.kb-file-item').forEach(item => {
            const path = item.dataset.path;
            if (path) {
                item.addEventListener('click', () => this.viewFile(path));
            }
        });
    }
    
    getFileIcon(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        const icons = {
            md: '📄',
            yaml: '⚙️',
            yml: '⚙️',
            js: '💻',
            html: '🌐',
            css: '🎨',
            json: '📋',
            txt: '📝'
        };
        return icons[ext] || '📁';
    }
    
    async viewFile(filePath) {
        try {
            const res = await fetch(`/api/project/${this.currentProjectId}/file?path=${encodeURIComponent(filePath)}`);
            const data = await res.json();
            
            if (data.success) {
                this.currentFile = filePath;
                this.showFileContent(filePath, data.content, data.modified_time);
                
                // 更新选中状态
                this.modal.querySelectorAll('.kb-file-item').forEach(item => {
                    if (item.dataset.path === filePath) {
                        item.classList.add('active');
                    } else {
                        item.classList.remove('active');
                    }
                });
            } else {
                alert('读取文件失败');
            }
        } catch (err) {
            console.error('读取文件失败:', err);
            alert('读取文件失败: ' + err.message);
        }
    }
    
    showFileContent(filePath, content, modifiedTime) {
        // 隐藏空状态，显示文件视图
        if (this.emptyView) this.emptyView.style.display = 'none';
        if (this.fileView) this.fileView.style.display = 'flex';
        
        // 设置文件信息
        if (this.fileTitle) {
            const fileName = filePath.split('/').pop();
            this.fileTitle.textContent = fileName;
        }
        
        if (this.fileMeta) {
            const size = new Blob([content]).size;
            const sizeStr = size < 1024 ? `${size}B` : `${(size / 1024).toFixed(1)}KB`;
            const timeStr = new Date(modifiedTime).toLocaleString('zh-CN');
            this.fileMeta.textContent = `${sizeStr} · 修改于 ${timeStr}`;
        }
        
        // 设置文件内容
        if (this.fileCode) {
            this.fileCode.textContent = content;
        }
    }
    
    esc(text) {
        const d = document.createElement('div');
        d.textContent = text || '';
        return d.innerHTML;
    }
}

export default KnowledgeBase;
