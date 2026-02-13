/**
 * 文件浏览器
 * 显示项目文件结构（树形）
 */
export class FileBrowser {
    constructor(containerElement) {
        this.container = containerElement;
        this.files = [];
        this.expandedFolders = new Set();
    }

    /**
     * 更新文件列表
     */
    updateFiles(files) {
        if (!files || files.length === 0) {
            this.clear();
            return;
        }

        this.files = files;
        this.render();
    }

    /**
     * 添加或更新单个文件
     */
    updateFile(filePath) {
        if (!this.files.find(f => f.path === filePath)) {
            this.files.push({ path: filePath, type: 'file' });
            this.files.sort((a, b) => a.path.localeCompare(b.path));
        }
        this.render();
    }

    /**
     * 渲染文件树
     */
    render() {
        this.clearWelcome();

        if (this.files.length === 0) {
            this.container.innerHTML = '<div class="file-welcome">暂无项目文件</div>';
            return;
        }

        // 构建文件树结构
        const tree = this.buildTree(this.files);
        
        // 渲染树
        this.container.innerHTML = this.renderTree(tree);

        // 添加事件监听
        this.attachEventListeners();
    }

    /**
     * 构建树形结构
     */
    buildTree(files) {
        const tree = {};

        files.forEach(file => {
            const parts = file.path.split('/').filter(p => p);
            let current = tree;

            parts.forEach((part, index) => {
                if (!current[part]) {
                    current[part] = {
                        name: part,
                        path: parts.slice(0, index + 1).join('/'),
                        type: index === parts.length - 1 ? 'file' : 'folder',
                        children: {}
                    };
                }
                current = current[part].children;
            });
        });

        return tree;
    }

    /**
     * 渲染树
     */
    renderTree(tree, level = 0) {
        const items = Object.values(tree);
        if (items.length === 0) return '';

        // 排序：文件夹在前，文件在后
        items.sort((a, b) => {
            if (a.type !== b.type) {
                return a.type === 'folder' ? -1 : 1;
            }
            return a.name.localeCompare(b.name);
        });

        let html = '<ul class="file-tree">';
        
        items.forEach(item => {
            const indent = level * 20;
            const icon = item.type === 'folder' ? '📁' : '📄';
            const isExpanded = this.expandedFolders.has(item.path);
            const expandIcon = item.type === 'folder' 
                ? (isExpanded ? '▼' : '▶') 
                : '';
            
            html += `
                <li>
                    <div class="file-item ${item.type === 'folder' ? 'folder-item' : ''}" 
                         style="padding-left: ${indent}px"
                         data-path="${item.path}"
                         data-type="${item.type}">
                        ${expandIcon ? `<span class="expand-icon">${expandIcon}</span>` : '<span class="expand-icon" style="width: 16px; display: inline-block;"></span>'}
                        <span class="file-icon">${icon}</span>
                        <span class="file-name">${item.name}</span>
                    </div>
            `;

            // 如果是展开的文件夹，递归渲染子项
            if (item.type === 'folder' && isExpanded && Object.keys(item.children).length > 0) {
                html += this.renderTree(item.children, level + 1);
            }

            html += '</li>';
        });

        html += '</ul>';
        return html;
    }

    /**
     * 附加事件监听器
     */
    attachEventListeners() {
        this.container.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const path = item.dataset.path;
                const type = item.dataset.type;

                if (type === 'folder') {
                    // 切换文件夹展开/折叠
                    if (this.expandedFolders.has(path)) {
                        this.expandedFolders.delete(path);
                    } else {
                        this.expandedFolders.add(path);
                    }
                    this.render();
                } else {
                    // 文件点击事件（暂不实现查看内容）
                    console.log('点击文件:', path);
                    // TODO: P7阶段可以实现文件内容查看
                }
            });
        });
    }

    /**
     * 清空欢迎消息
     */
    clearWelcome() {
        const welcome = this.container.querySelector('.file-welcome');
        if (welcome) {
            welcome.remove();
        }
    }

    /**
     * 清空文件列表
     */
    clear() {
        this.files = [];
        this.expandedFolders.clear();
        this.container.innerHTML = '<div class="file-welcome">暂无项目文件</div>';
    }

    /**
     * 从项目目录加载文件（模拟）
     */
    loadProjectFiles(projectName) {
        // 这是模拟数据，实际应该从API获取
        const mockFiles = [
            { path: `projects/${projectName}/shared_knowledge/game_design_doc.md`, type: 'file' },
            { path: `projects/${projectName}/shared_knowledge/tech_design_doc.md`, type: 'file' },
            { path: `projects/${projectName}/shared_knowledge/api_registry.yaml`, type: 'file' },
            { path: `projects/${projectName}/shared_knowledge/config_tables.yaml`, type: 'file' },
            { path: `projects/${projectName}/output/js/game.js`, type: 'file' },
            { path: `projects/${projectName}/output/css/style.css`, type: 'file' }
        ];

        this.updateFiles(mockFiles);
    }
}

export default FileBrowser;
