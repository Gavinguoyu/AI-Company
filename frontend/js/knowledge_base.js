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
            const data = await res.json();
            if (data.project && data.project.project_name) {
                this.projectName = data.project.project_name;
            } else {
                // 从project_id中提取（去掉时间戳后缀）
                this.projectName = projectId.split('_').slice(0, -2).join('_') || projectId;
            }
        } catch (e) {
            // 如果API失败，尝试从project_id中提取
            this.projectName = projectId.split('_').slice(0, -2).join('_') || projectId;
        }
    }
    
    async loadFileList() {
        try {
            // 使用project_name作为目录名
            const projectName = this.projectName || this.currentProjectId;
            
            // 加载共享知识库文件
            const sharedRes = await fetch(`/api/project/${this.currentProjectId}/files?directory=shared_knowledge`);
            const sharedData = await sharedRes.json();
            
            if (sharedData.success) {
                this.renderFileList(this.sharedList, sharedData.items, 'shared_knowledge');
            }
            
            // 加载游戏产出文件
            const outputRes = await fetch(`/api/project/${this.currentProjectId}/files?directory=output`);
            const outputData = await outputRes.json();
            
            if (outputData.success) {
                this.renderFileList(this.outputList, outputData.items, 'output');
            }
        } catch (err) {
            console.error('加载文件列表失败:', err);
            alert('加载文件列表失败: ' + err.message);
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
