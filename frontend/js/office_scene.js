/**
 * 办公室场景 – Canvas 2D 全屏自适应 + 无限画布
 * P8-2 增强版：像素风Agent、办公室装饰、动画系统、游戏展示区、交互增强
 * 深色极客风 · 点击Agent可触发外部回调
 * Camera系统：中键拖拽平移 / 滚轮缩放 / 空格+左键拖拽
 */

import { spriteRenderer, DECORATIONS, PAL } from './pixel_sprites.js';

export class OfficeScene {
    constructor(container) {
        this.container = container;
        this.canvas = null;
        this.ctx = null;

        this.agents = new Map();
        this.flyingMessages = [];
        this.particles = [];
        this.selectedAgentId = null;
        this.hoveredAgentId = null;

        // 逻辑坐标尺寸（世界坐标原点区域）
        this.W = 1200;
        this.H = 700;

        // 视口缩放/偏移（设备像素适配）
        this.scale = 1;
        this.offsetX = 0;
        this.offsetY = 0;

        // ═══ Camera 系统 ═══
        this.camX = 0;
        this.camY = 0;
        this.zoom = 1;
        this.zoomMin = 0.3;
        this.zoomMax = 3.0;

        // ═══ 拖拽状态 ═══
        this.isDragging = false;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.camStartX = 0;
        this.camStartY = 0;
        this.spaceHeld = false;

        this.animationId = null;
        this.ready = false;
        this.frameCount = 0;

        /** @type {function(string):void|null} 外部点击回调 */
        this.onAgentClick = null;

        // ═══ P8-2: 悬停提示面板 ═══
        this.tooltipData = null;

        // ═══ P8-2: 装饰物缓存 ═══
        this.decoCache = new Map();

        // ═══ P8-2: 游戏展示区 ═══
        this.gameShowcase = {
            games: [],
            x: 950, y: 10,
            w: 230, h: 160,
            hovered: false
        };

        // ═══ P8-2: 状态动画 ═══
        this.statusAnimations = new Map();

        this.init();
    }

    /* ═══════════ 初始化 ═══════════ */

    init() {
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.container.innerHTML = '';
        this.container.appendChild(this.canvas);

        this.createAgents();
        this.preRenderDecorations();
        this.resize();

        window.addEventListener('resize', () => this.resize());
        this.canvas.addEventListener('mousemove', e => this.onMouseMove(e));
        this.canvas.addEventListener('click', e => this.onClick(e));

        // Camera 事件
        this.canvas.addEventListener('wheel', e => this.onWheel(e), { passive: false });
        this.canvas.addEventListener('mousedown', e => this.onMouseDown(e));
        this.canvas.addEventListener('mouseup', e => this.onMouseUp(e));
        this.canvas.addEventListener('mouseleave', e => this.onMouseLeave(e));
        window.addEventListener('keydown', e => this.onKeyDown(e));
        window.addEventListener('keyup', e => this.onKeyUp(e));

        this.canvas.addEventListener('contextmenu', e => e.preventDefault());

        this.ready = true;
        this.render();
        console.log('✅ 办公室场景初始化完成（P8-2 像素风增强版）');
    }

    resize() {
        const rect = this.container.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = rect.height + 'px';

        const sx = rect.width / this.W;
        const sy = rect.height / this.H;
        this.scale = Math.min(sx, sy) * dpr;
        this.offsetX = (this.canvas.width - this.W * this.scale) / 2;
        this.offsetY = (this.canvas.height - this.H * this.scale) / 2;
    }

    /* ═══════════ Agent 定义 ═══════════ */

    createAgents() {
        const defs = [
            { id: 'pm',         x: 240,  y: 220, name: '项目经理',   emoji: '👨‍💼', accent: '#58a6ff' },
            { id: 'planner',    x: 960,  y: 220, name: '游戏策划',   emoji: '📋',   accent: '#d29922' },
            { id: 'programmer', x: 240,  y: 480, name: '程序员',     emoji: '👨‍💻', accent: '#3fb950' },
            { id: 'artist',     x: 960,  y: 480, name: '美术设计',   emoji: '🎨',   accent: '#f778ba' },
            { id: 'tester',     x: 600,  y: 580, name: '测试工程师', emoji: '🧪',   accent: '#bc8cff' }
        ];
        for (const d of defs) {
            this.agents.set(d.id, {
                ...d,
                status: 'idle', task: '',
                bubble: null, bubbleTimer: 0,
                phase: Math.random() * Math.PI * 2,
                hitRadius: 50,
                // P8-2: 动画相关
                animFrame: 0,
                animTimer: 0,
                celebrateTimer: 0,
                thinkTimer: 0,
                walkTarget: null,
                walkProgress: 0,
                messageCount: 0,
            });
        }
    }

    /** P8-2: 预渲染装饰物精灵 */
    preRenderDecorations() {
        for (const [key, data] of Object.entries(DECORATIONS)) {
            this.decoCache.set(key, spriteRenderer.renderSprite(`deco_${key}`, data, 2));
        }
    }

    /* ═══════════ 坐标转换（含 Camera） ═══════════ */

    screenToLogic(sx, sy) {
        const dpr = window.devicePixelRatio || 1;
        let lx = (sx * dpr - this.offsetX) / this.scale;
        let ly = (sy * dpr - this.offsetY) / this.scale;
        lx = (lx - this.W / 2) / this.zoom + this.W / 2 - this.camX;
        ly = (ly - this.H / 2) / this.zoom + this.H / 2 - this.camY;
        return { x: lx, y: ly };
    }

    /* ═══════════ Camera 事件 ═══════════ */

    onWheel(e) {
        e.preventDefault();
        const rect = this.canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const before = this.screenToLogic(mx, my);

        const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
        this.zoom = Math.max(this.zoomMin, Math.min(this.zoomMax, this.zoom * factor));

        const after = this.screenToLogic(mx, my);
        this.camX += (after.x - before.x);
        this.camY += (after.y - before.y);
    }

    onMouseDown(e) {
        if (e.button === 1 || (e.button === 0 && this.spaceHeld)) {
            e.preventDefault();
            this.isDragging = true;
            this.dragStartX = e.clientX;
            this.dragStartY = e.clientY;
            this.camStartX = this.camX;
            this.camStartY = this.camY;
            this.canvas.style.cursor = 'grabbing';
        }
    }

    onMouseUp(_e) {
        if (this.isDragging) {
            this.isDragging = false;
            this.canvas.style.cursor = this.spaceHeld ? 'grab' : 'default';
        }
    }

    onMouseLeave(_e) {
        if (this.isDragging) {
            this.isDragging = false;
            this.canvas.style.cursor = 'default';
        }
        this.hoveredAgentId = null;
        this.tooltipData = null;
    }

    onKeyDown(e) {
        if (e.code === 'Space') {
            e.preventDefault();
            this.spaceHeld = true;
            if (!this.isDragging) this.canvas.style.cursor = 'grab';
        }
        if (e.code === 'Home') {
            this.camX = 0;
            this.camY = 0;
            this.zoom = 1;
        }
    }

    onKeyUp(e) {
        if (e.code === 'Space') {
            this.spaceHeld = false;
            if (!this.isDragging) this.canvas.style.cursor = 'default';
        }
    }

    /* ═══════════ 鼠标移动 ═══════════ */

    onMouseMove(e) {
        if (this.isDragging) {
            const dpr = window.devicePixelRatio || 1;
            const dx = (e.clientX - this.dragStartX) * dpr / (this.scale * this.zoom);
            const dy = (e.clientY - this.dragStartY) * dpr / (this.scale * this.zoom);
            this.camX = this.camStartX + dx;
            this.camY = this.camStartY + dy;
            return;
        }

        const rect = this.canvas.getBoundingClientRect();
        const p = this.screenToLogic(e.clientX - rect.left, e.clientY - rect.top);
        let found = null;
        this.agents.forEach(a => {
            if (Math.hypot(p.x - a.x, p.y - a.y) < a.hitRadius) found = a.id;
        });
        this.hoveredAgentId = found;

        // P8-2: 更新悬停提示
        if (found) {
            const a = this.agents.get(found);
            this.tooltipData = {
                screenX: e.clientX - rect.left,
                screenY: e.clientY - rect.top,
                agent: a
            };
        } else {
            this.tooltipData = null;
        }

        // 检查游戏展示区悬停
        const gs = this.gameShowcase;
        gs.hovered = p.x >= gs.x && p.x <= gs.x + gs.w && p.y >= gs.y && p.y <= gs.y + gs.h;

        if (!this.spaceHeld) {
            this.canvas.style.cursor = found ? 'pointer' : (gs.hovered && gs.games.length > 0 ? 'pointer' : 'default');
        }
    }

    onClick(e) {
        if (this.spaceHeld) return;
        if (e.button !== 0) return;

        const rect = this.canvas.getBoundingClientRect();
        const p = this.screenToLogic(e.clientX - rect.left, e.clientY - rect.top);

        // 检查游戏展示区点击
        const gs = this.gameShowcase;
        if (gs.games.length > 0 && p.x >= gs.x && p.x <= gs.x + gs.w && p.y >= gs.y && p.y <= gs.y + gs.h) {
            const latest = gs.games[gs.games.length - 1];
            if (latest.url) window.open(latest.url, '_blank');
            return;
        }

        let clicked = null;
        this.agents.forEach(a => {
            if (Math.hypot(p.x - a.x, p.y - a.y) < a.hitRadius) clicked = a.id;
        });

        if (clicked) {
            this.selectedAgentId = clicked;
            if (this.onAgentClick) this.onAgentClick(clicked);
        } else {
            this.selectedAgentId = null;
        }
    }

    /* ═══════════ 外部接口 ═══════════ */

    updateAgentStatus(agentId, status, task = '') {
        const a = this.agents.get(agentId);
        if (!a) return;
        const old = a.status;
        a.status = status;
        a.task = task;
        if (old !== status) {
            this.spawnParticles(a.x, a.y - 40, this.statusColor(status));
            // P8-2: 状态变化动画
            if (status === 'idle' && old === 'working') {
                a.celebrateTimer = 60; // 庆祝动画
            }
            if (status === 'thinking') {
                a.thinkTimer = 120;
            }
        }
    }

    showMessage(fromId, toId, content) {
        const from = this.agents.get(fromId);
        if (!from) return;
        from.messageCount++;

        let to = this.agents.get(toId);
        if (!to || toId === 'all' || toId === 'boss') {
            const ids = [...this.agents.keys()].filter(id => id !== fromId);
            to = this.agents.get(ids[Math.floor(Math.random() * ids.length)]);
        }
        if (!to) { this.showBubble(from, content); return; }

        const cx = (from.x + to.x) / 2;
        const cy = Math.min(from.y, to.y) - 80;
        this.flyingMessages.push({
            fromX: from.x, fromY: from.y,
            toX: to.x, toY: to.y,
            ctrlX: cx, ctrlY: cy,
            progress: 0, content, targetAgent: to
        });

        from.status = 'communicating';
        setTimeout(() => { if (from.status === 'communicating') from.status = 'working'; }, 2000);
    }

    showBubble(agent, text) {
        agent.bubble = text.length > 26 ? text.substring(0, 26) + '…' : text;
        agent.bubbleTimer = 180;
    }

    selectAgent(id) {
        this.selectedAgentId = id;
    }

    reset() {
        this.agents.forEach(a => { a.status = 'idle'; a.task = ''; a.messageCount = 0; });
    }

    resetCamera() {
        this.camX = 0;
        this.camY = 0;
        this.zoom = 1;
    }

    /** P8-2: 添加游戏到展示区 */
    addGameToShowcase(name, url, time) {
        this.gameShowcase.games.push({ name, url, time: time || new Date().toLocaleTimeString() });
        // 只保留最近5个
        if (this.gameShowcase.games.length > 5) this.gameShowcase.games.shift();
    }

    /* ═══════════ 渲染循环 ═══════════ */

    render = () => {
        if (!this.ready) return;
        this.animationId = requestAnimationFrame(this.render);
        this.frameCount++;
        const c = this.ctx;
        const CW = this.canvas.width, CH = this.canvas.height;
        c.clearRect(0, 0, CW, CH);

        // 背景
        c.fillStyle = '#0d1117';
        c.fillRect(0, 0, CW, CH);

        c.save();
        c.translate(this.offsetX, this.offsetY);
        c.scale(this.scale, this.scale);

        c.translate(this.W / 2, this.H / 2);
        c.scale(this.zoom, this.zoom);
        c.translate(-this.W / 2 + this.camX, -this.H / 2 + this.camY);

        // 绘制世界内容
        this.drawFloor(c);
        this.drawWalls(c);
        this.drawConnections(c);
        this.drawDecorations(c);
        this.drawDesks(c);
        this.drawAgentSprites(c);
        this.drawAgentAnimations(c);
        this.updateFlying(c);
        this.drawBubbles(c);
        this.updateParticles(c);
        this.drawGameShowcase(c);

        c.restore();

        // UI 层 (Camera变换之外)
        this.drawMiniMap(c, CW, CH);
        this.drawZoomControls(c, CW, CH);
        this.drawTooltip(c, CW, CH);

        if (Math.abs(this.zoom - 1) > 0.01) {
            this.drawZoomIndicator(c, CW, CH);
        }
    };

    /* ═══════════ P8-2: 地板纹理 ═══════════ */

    drawFloor(c) {
        const extend = 600;
        const x0 = -extend, y0 = -extend;
        const x1 = this.W + extend, y1 = this.H + extend;

        // 像素风地板纹理
        const tileSize = 40;
        for (let x = Math.floor(x0 / tileSize) * tileSize; x <= x1; x += tileSize) {
            for (let y = Math.floor(y0 / tileSize) * tileSize; y <= y1; y += tileSize) {
                const checker = ((x / tileSize + y / tileSize) % 2 === 0);
                c.fillStyle = checker ? 'rgba(20,27,35,1)' : 'rgba(16,22,30,1)';
                c.fillRect(x, y, tileSize, tileSize);
            }
        }

        // 格线
        c.strokeStyle = 'rgba(48,54,61,.25)';
        c.lineWidth = 0.5;
        for (let x = Math.floor(x0 / tileSize) * tileSize; x <= x1; x += tileSize) {
            c.beginPath(); c.moveTo(x, y0); c.lineTo(x, y1); c.stroke();
        }
        for (let y = Math.floor(y0 / tileSize) * tileSize; y <= y1; y += tileSize) {
            c.beginPath(); c.moveTo(x0, y); c.lineTo(x1, y); c.stroke();
        }

        // 标题
        c.fillStyle = 'rgba(255,255,255,.04)';
        c.font = 'bold 18px "Cascadia Code", monospace';
        c.textAlign = 'center';
        c.fillText('AI  GAMEDEV  STUDIO', this.W / 2, 40);

        // 像素风格边框点缀
        c.fillStyle = 'rgba(0,255,157,.06)';
        for (let i = 0; i < this.W; i += 8) {
            c.fillRect(i, 0, 4, 2);
            c.fillRect(i, this.H - 2, 4, 2);
        }
        for (let i = 0; i < this.H; i += 8) {
            c.fillRect(0, i, 2, 4);
            c.fillRect(this.W - 2, i, 2, 4);
        }
    }

    /* ═══════════ P8-2: 墙壁分区 ═══════════ */

    drawWalls(c) {
        // 顶部墙壁 - 深色带纹理
        c.fillStyle = '#121820';
        c.fillRect(0, 0, this.W, 60);

        // 墙壁底部像素边框
        c.fillStyle = 'rgba(0,255,157,.15)';
        for (let x = 0; x < this.W; x += 6) {
            c.fillRect(x, 58, 4, 2);
        }

        // 墙上挂画/标语
        c.fillStyle = '#1c2333';
        this.rr(c, 480, 10, 240, 40, 4, true);
        c.strokeStyle = 'rgba(0,255,157,.2)';
        c.lineWidth = 1;
        this.rr(c, 480, 10, 240, 40, 4, false, true);

        c.fillStyle = 'rgba(0,255,157,.4)';
        c.font = 'bold 11px "Cascadia Code", monospace';
        c.textAlign = 'center';
        c.fillText('{ MAKE GAMES WITH AI }', 600, 35);

        // 左侧分区标签
        c.fillStyle = 'rgba(88,166,255,.08)';
        c.fillRect(20, 140, 4, 200);
        c.save();
        c.translate(30, 240);
        c.rotate(-Math.PI / 2);
        c.fillStyle = 'rgba(88,166,255,.25)';
        c.font = '9px "Cascadia Code", monospace';
        c.textAlign = 'center';
        c.fillText('MANAGEMENT', 0, 0);
        c.restore();

        // 右侧分区标签
        c.fillStyle = 'rgba(247,120,186,.08)';
        c.fillRect(this.W - 24, 140, 4, 200);
        c.save();
        c.translate(this.W - 14, 240);
        c.rotate(Math.PI / 2);
        c.fillStyle = 'rgba(247,120,186,.25)';
        c.font = '9px "Cascadia Code", monospace';
        c.textAlign = 'center';
        c.fillText('CREATIVE', 0, 0);
        c.restore();

        // 底部分区标签
        c.fillStyle = 'rgba(188,140,255,.08)';
        c.fillRect(400, this.H - 24, 400, 4);
        c.fillStyle = 'rgba(188,140,255,.25)';
        c.font = '9px "Cascadia Code", monospace';
        c.textAlign = 'center';
        c.fillText('QUALITY ASSURANCE', 600, this.H - 10);
    }

    /* ═══════════ 绘制：Agent之间连线 ═══════════ */

    drawConnections(c) {
        const ids = [...this.agents.keys()];
        c.strokeStyle = 'rgba(48,54,61,.2)';
        c.lineWidth = 1;
        c.setLineDash([4, 6]);
        for (let i = 0; i < ids.length; i++) {
            for (let j = i + 1; j < ids.length; j++) {
                const a = this.agents.get(ids[i]);
                const b = this.agents.get(ids[j]);
                c.beginPath(); c.moveTo(a.x, a.y); c.lineTo(b.x, b.y); c.stroke();
            }
        }
        c.setLineDash([]);
    }

    /* ═══════════ P8-2: 装饰物绘制 ═══════════ */

    drawDecorations(c) {
        // 植物们
        const plants = [
            { x: 60, y: 130 },
            { x: 1130, y: 130 },
            { x: 60, y: 620 },
            { x: 1130, y: 620 },
            { x: 580, y: 100 },
        ];
        const plantSprite = this.decoCache.get('plant');
        if (plantSprite) {
            plants.forEach(p => {
                // 轻微摇摆动画
                c.save();
                const sway = Math.sin(this.frameCount * 0.02 + p.x) * 1.5;
                c.translate(p.x, p.y);
                c.rotate(sway * Math.PI / 180);
                c.drawImage(plantSprite, -plantSprite.width / 2, -plantSprite.height / 2);
                c.restore();
            });
        }

        // 书架 (左上角)
        const bookshelf = this.decoCache.get('bookshelf');
        if (bookshelf) {
            c.drawImage(bookshelf, 100, 70);
        }

        // 咖啡机 (中间偏上)
        const coffee = this.decoCache.get('coffee');
        if (coffee) {
            c.drawImage(coffee, 555, 80);
            // 蒸汽动画
            if (this.frameCount % 30 < 15) {
                c.fillStyle = 'rgba(255,255,255,.15)';
                const steamY = 75 - (this.frameCount % 15) * 0.5;
                c.fillRect(562, steamY, 2, 3);
                c.fillRect(568, steamY - 3, 2, 3);
                c.fillRect(565, steamY - 6, 2, 3);
            }
        }

        // 任务板 (中间墙上)
        const taskboard = this.decoCache.get('taskboard');
        if (taskboard) {
            c.drawImage(taskboard, 370, 65);
        }

        // 中间区域休息区地毯
        c.fillStyle = 'rgba(0,255,157,.03)';
        this.rr(c, 500, 340, 200, 120, 8, true);
        c.strokeStyle = 'rgba(0,255,157,.08)';
        c.lineWidth = 1;
        c.setLineDash([3, 3]);
        this.rr(c, 504, 344, 192, 112, 6, false, true);
        c.setLineDash([]);

        // 中间桌子 (会议桌)
        c.fillStyle = '#1a1f2e';
        this.rr(c, 530, 360, 140, 80, 8, true);
        c.fillStyle = '#1e2536';
        this.rr(c, 534, 364, 132, 72, 6, true);
        // 桌上文件
        c.fillStyle = 'rgba(255,255,255,.06)';
        c.fillRect(550, 375, 20, 28);
        c.fillRect(580, 380, 20, 28);
        c.fillStyle = 'rgba(0,255,157,.1)';
        c.fillRect(610, 375, 30, 15);
    }

    /* ═══════════ 绘制：桌子（增强版） ═══════════ */

    drawDesks(c) {
        this.agents.forEach(a => {
            // 桌子阴影
            c.fillStyle = 'rgba(0,0,0,.3)';
            this.rr(c, a.x - 52, a.y + 20, 104, 48, 6, true);

            // 桌面
            c.fillStyle = '#1c2333';
            this.rr(c, a.x - 54, a.y + 16, 108, 48, 6, true);

            // 桌面高光
            c.fillStyle = 'rgba(255,255,255,.03)';
            this.rr(c, a.x - 48, a.y + 18, 96, 10, 4, true);

            // 桌腿 (像素风)
            c.fillStyle = '#151a27';
            c.fillRect(a.x - 48, a.y + 56, 4, 12);
            c.fillRect(a.x + 44, a.y + 56, 4, 12);

            // 电脑显示器（像素风）
            const monitor = this.decoCache.get('monitor');
            if (monitor) {
                c.drawImage(monitor, a.x - 10, a.y + 20);
            } else {
                // 后备：简单矩形显示器
                c.fillStyle = '#0d1117';
                c.fillRect(a.x - 14, a.y + 26, 28, 20);
                c.fillStyle = a.status === 'working' || a.status === 'communicating'
                    ? a.accent + '66' : 'rgba(48,54,61,.5)';
                c.fillRect(a.x - 12, a.y + 28, 24, 16);
            }

            // 显示器屏幕发光效果
            if (a.status === 'working' || a.status === 'communicating') {
                c.fillStyle = a.accent + '0a';
                c.beginPath();
                c.arc(a.x, a.y + 35, 25, 0, Math.PI * 2);
                c.fill();
            }

            // 桌上小物件
            // 杯子
            c.fillStyle = '#334155';
            c.fillRect(a.x + 25, a.y + 28, 8, 10);
            c.fillStyle = '#475569';
            c.fillRect(a.x + 25, a.y + 26, 8, 3);
            // 小物件 - 基于agent不同
            if (a.id === 'pm') {
                // 名牌
                c.fillStyle = '#58a6ff22';
                c.fillRect(a.x - 40, a.y + 30, 20, 8);
            } else if (a.id === 'programmer') {
                // 键盘
                c.fillStyle = '#334155';
                c.fillRect(a.x - 20, a.y + 42, 24, 6);
                c.fillStyle = '#475569';
                for (let i = 0; i < 5; i++) c.fillRect(a.x - 18 + i * 5, a.y + 43, 3, 1);
            } else if (a.id === 'artist') {
                // 数位板
                c.fillStyle = '#2c1810';
                c.fillRect(a.x - 38, a.y + 32, 18, 14);
                c.fillStyle = '#3d2317';
                c.fillRect(a.x - 36, a.y + 34, 14, 10);
            }
        });
    }

    /* ═══════════ 绘制：Agent精灵（像素风） ═══════════ */

    drawAgentSprites(c) {
        this.agents.forEach(a => {
            const bob = Math.sin(a.phase) * 2;
            a.phase += 0.025;

            // 动画帧切换
            a.animTimer++;
            if (a.animTimer > 30) {
                a.animTimer = 0;
                a.animFrame = a.animFrame === 0 ? 1 : 0;
            }

            const isSelected = a.id === this.selectedAgentId;
            const isHovered  = a.id === this.hoveredAgentId;

            // 选中/悬停效果
            if (isSelected || isHovered) {
                c.save();
                c.strokeStyle = isSelected ? a.accent : a.accent + '88';
                c.lineWidth = isSelected ? 2.5 : 1.5;
                c.setLineDash(isSelected ? [] : [4, 4]);
                c.beginPath();
                c.arc(a.x, a.y - 5 + bob, 55, 0, Math.PI * 2);
                c.stroke();
                c.setLineDash([]);

                // 地面发光
                const glow = c.createRadialGradient(a.x, a.y + 60, 0, a.x, a.y + 60, 60);
                glow.addColorStop(0, a.accent + '18');
                glow.addColorStop(1, 'transparent');
                c.fillStyle = glow;
                c.fillRect(a.x - 60, a.y + 10, 120, 60);
                c.restore();
            }

            // P8-2: 绘制像素风角色
            const frames = spriteRenderer.getAgentFrames(a.id);
            if (frames) {
                const isWorking = a.status === 'working' || a.status === 'communicating';
                const frame = (isWorking && a.animFrame === 1) ? frames.work : frames.idle;
                const spriteW = frame.width;
                const spriteH = frame.height;

                c.save();
                // 关闭抗锯齿以保持像素风
                c.imageSmoothingEnabled = false;
                // 绘制像素角色，放大显示
                const drawScale = 2.6;
                const drawW = spriteW * drawScale;
                const drawH = spriteH * drawScale;
                c.drawImage(frame,
                    a.x - drawW / 2,
                    a.y - drawH / 2 - 12 + bob,
                    drawW, drawH
                );
                c.imageSmoothingEnabled = true;
                c.restore();
            } else {
                // 后备：使用Emoji
                c.font = '42px Arial';
                c.textAlign = 'center';
                c.textBaseline = 'middle';
                c.fillText(a.emoji, a.x, a.y - 10 + bob);
            }

            // 名称标签
            c.fillStyle = isSelected ? a.accent + '33' : 'rgba(0,0,0,.55)';
            this.rr(c, a.x - 46, a.y + 56, 92, 24, 4, true);

            c.fillStyle = isSelected ? '#fff' : 'rgba(255,255,255,.85)';
            c.font = 'bold 12px "Microsoft YaHei", sans-serif';
            c.textAlign = 'center'; c.textBaseline = 'middle';
            c.fillText(a.name, a.x, a.y + 68);

            // 状态指示灯（像素风方块）
            const sc = this.statusColor(a.status);
            // 外圈方块
            c.fillStyle = sc + '33';
            c.fillRect(a.x - 10, a.y - 52 + bob, 20, 20);
            // 内圈方块
            c.fillStyle = sc;
            c.fillRect(a.x - 6, a.y - 48 + bob, 12, 12);
            // 像素边框
            c.strokeStyle = sc + '66';
            c.lineWidth = 1;
            c.strokeRect(a.x - 10, a.y - 52 + bob, 20, 20);

            // 状态文字
            c.fillStyle = sc;
            c.font = '10px "Cascadia Code", monospace';
            c.fillText(this.statusText(a.status).toUpperCase(), a.x, a.y + 86);

            // 消息计数徽标
            if (a.messageCount > 0) {
                c.fillStyle = a.accent;
                c.beginPath();
                c.arc(a.x + 30, a.y - 45 + bob, 8, 0, Math.PI * 2);
                c.fill();
                c.fillStyle = '#fff';
                c.font = 'bold 8px "Cascadia Code", monospace';
                c.fillText(a.messageCount > 99 ? '99+' : String(a.messageCount), a.x + 30, a.y - 44 + bob);
            }
        });
    }

    /* ═══════════ P8-2: Agent动画效果 ═══════════ */

    drawAgentAnimations(c) {
        this.agents.forEach(a => {
            // 庆祝动画 - 头顶星星
            if (a.celebrateTimer > 0) {
                a.celebrateTimer--;
                const t = a.celebrateTimer / 60;
                const count = 5;
                for (let i = 0; i < count; i++) {
                    const angle = (Math.PI * 2 * i / count) + this.frameCount * 0.05;
                    const r = 30 + (1 - t) * 20;
                    const sx = a.x + Math.cos(angle) * r;
                    const sy = a.y - 50 + Math.sin(angle) * r * 0.5 - (1 - t) * 30;
                    c.save();
                    c.globalAlpha = t;
                    c.fillStyle = '#facc15';
                    this.drawStar(c, sx, sy, 4, 2, 5);
                    c.restore();
                }
            }

            // 思考动画 - 头顶问号/灯泡
            if (a.thinkTimer > 0 || a.status === 'thinking') {
                if (a.thinkTimer > 0) a.thinkTimer--;
                const bob = Math.sin(this.frameCount * 0.08) * 3;
                const alpha = a.thinkTimer > 0 ? Math.min(1, a.thinkTimer / 20) : 0.8;

                c.save();
                c.globalAlpha = alpha;

                // 思考气泡
                c.fillStyle = '#1c2333';
                c.strokeStyle = '#d29922';
                c.lineWidth = 1.5;
                const bx = a.x + 35, by = a.y - 65 + bob;
                this.rr(c, bx - 14, by - 14, 28, 28, 6, true);
                this.rr(c, bx - 14, by - 14, 28, 28, 6, false, true);

                // 问号
                c.fillStyle = '#d29922';
                c.font = 'bold 18px "Cascadia Code", monospace';
                c.textAlign = 'center'; c.textBaseline = 'middle';
                c.fillText('?', bx, by);

                // 小气泡
                c.fillStyle = '#1c2333';
                c.strokeStyle = '#d29922';
                c.beginPath(); c.arc(a.x + 22, a.y - 50, 4, 0, Math.PI * 2); c.fill(); c.stroke();
                c.beginPath(); c.arc(a.x + 27, a.y - 55, 3, 0, Math.PI * 2); c.fill(); c.stroke();

                c.restore();
            }

            // 工作动画 - 打字效果（在显示器上）
            if (a.status === 'working') {
                // 代码行在屏幕上滚动
                const lineY = a.y + 30;
                const lineCount = 3;
                for (let i = 0; i < lineCount; i++) {
                    const flicker = (this.frameCount + i * 7) % 20 < 14;
                    if (flicker) {
                        c.fillStyle = a.accent + '44';
                        const w = 4 + Math.sin(this.frameCount * 0.1 + i) * 3;
                        c.fillRect(a.x - 8 + i * 5, lineY + i * 3, w, 1);
                    }
                }
            }
        });
    }

    /* ═══════════ P8-2: 游戏展示区 ═══════════ */

    drawGameShowcase(c) {
        const gs = this.gameShowcase;

        // 背景
        c.fillStyle = '#111622';
        this.rr(c, gs.x, gs.y, gs.w, gs.h, 8, true);

        // 边框
        c.strokeStyle = gs.hovered ? 'rgba(0,255,157,.5)' : 'rgba(48,54,61,.6)';
        c.lineWidth = gs.hovered ? 2 : 1;
        this.rr(c, gs.x, gs.y, gs.w, gs.h, 8, false, true);

        // 标题栏
        c.fillStyle = '#1a2030';
        this.rr(c, gs.x, gs.y, gs.w, 28, 8, true);
        c.fillRect(gs.x, gs.y + 20, gs.w, 8);

        // 像素风图标
        c.fillStyle = '#00ff9d';
        c.font = '11px "Cascadia Code", monospace';
        c.textAlign = 'left';
        c.fillText('🎮 GAME SHOWCASE', gs.x + 10, gs.y + 18);

        // 游戏展示屏幕图标
        const gameScreen = this.decoCache.get('gameScreen');
        if (gameScreen) {
            c.save();
            c.imageSmoothingEnabled = false;
            c.drawImage(gameScreen, gs.x + 10, gs.y + 36, gameScreen.width * 1.5, gameScreen.height * 1.5);
            c.imageSmoothingEnabled = true;
            c.restore();
        }

        if (gs.games.length === 0) {
            // 空状态
            c.fillStyle = 'rgba(255,255,255,.15)';
            c.font = '11px "Cascadia Code", monospace';
            c.textAlign = 'center';
            c.fillText('等待游戏生成…', gs.x + gs.w / 2, gs.y + 95);

            // 像素风加载动画
            const dots = Math.floor(this.frameCount / 20) % 4;
            c.fillStyle = 'rgba(0,255,157,.3)';
            for (let i = 0; i < dots; i++) {
                c.fillRect(gs.x + gs.w / 2 - 12 + i * 8, gs.y + 110, 4, 4);
            }
        } else {
            // 显示最新游戏
            const latest = gs.games[gs.games.length - 1];
            c.fillStyle = '#c9d1d9';
            c.font = 'bold 11px "Microsoft YaHei", sans-serif';
            c.textAlign = 'left';
            c.fillText(latest.name || '未命名游戏', gs.x + 60, gs.y + 50);

            c.fillStyle = '#8b949e';
            c.font = '10px "Cascadia Code", monospace';
            c.fillText(latest.time, gs.x + 60, gs.y + 65);

            // 点击提示
            c.fillStyle = gs.hovered ? '#00ff9d' : 'rgba(0,255,157,.5)';
            c.font = '10px "Cascadia Code", monospace';
            c.fillText('▶ PLAY', gs.x + 60, gs.y + 85);

            // 游戏数量
            if (gs.games.length > 1) {
                c.fillStyle = 'rgba(255,255,255,.25)';
                c.font = '9px "Cascadia Code", monospace';
                c.textAlign = 'right';
                c.fillText(`${gs.games.length} games`, gs.x + gs.w - 10, gs.y + gs.h - 10);
            }
        }
    }

    /* ═══════════ 飞行消息 ═══════════ */

    updateFlying(c) {
        for (let i = this.flyingMessages.length - 1; i >= 0; i--) {
            const m = this.flyingMessages[i];
            m.progress += 0.016;
            const t = this.ease(Math.min(m.progress, 1));

            const x = (1 - t) ** 2 * m.fromX + 2 * (1 - t) * t * m.ctrlX + t ** 2 * m.toX;
            const y = (1 - t) ** 2 * m.fromY + 2 * (1 - t) * t * m.ctrlY + t ** 2 * m.toY;

            // 拖尾粒子 - 像素风方块
            for (let j = 1; j <= 5; j++) {
                const tt = this.ease(Math.max(m.progress - j * 0.008, 0));
                const tx = (1 - tt) ** 2 * m.fromX + 2 * (1 - tt) * tt * m.ctrlX + tt ** 2 * m.toX;
                const ty = (1 - tt) ** 2 * m.fromY + 2 * (1 - tt) * tt * m.ctrlY + tt ** 2 * m.toY;
                c.fillStyle = `rgba(0,255,157,${.3 - j * .05})`;
                const s = 8 - j * 1.2;
                c.fillRect(tx - s / 2, ty - s / 2, s, s);
            }

            // 信封主体 - 像素风方块
            c.fillStyle = '#00ff9d';
            c.fillRect(x - 6, y - 6, 12, 12);
            c.fillStyle = '#0d1117';
            c.fillRect(x - 4, y - 4, 8, 8);
            c.fillStyle = '#00ff9d';
            c.fillRect(x - 3, y - 2, 6, 4);

            // 发光效果
            c.save();
            c.globalAlpha = 0.3;
            c.fillStyle = '#00ff9d';
            c.fillRect(x - 10, y - 10, 20, 20);
            c.globalAlpha = 1;
            c.restore();

            if (m.progress >= 1) {
                this.flyingMessages.splice(i, 1);
                this.showBubble(m.targetAgent, m.content);
                m.targetAgent.status = 'communicating';
                this.spawnParticles(m.toX, m.toY - 40, '#3fb950');
                setTimeout(() => {
                    if (m.targetAgent.status === 'communicating') m.targetAgent.status = 'working';
                }, 1500);
            }
        }
    }

    /* ═══════════ 气泡 ═══════════ */

    drawBubbles(c) {
        this.agents.forEach(a => {
            if (!a.bubble || a.bubbleTimer <= 0) { a.bubble = null; return; }
            a.bubbleTimer--;
            const alpha = a.bubbleTimer < 30 ? a.bubbleTimer / 30 : 1;
            const bx = a.x, by = a.y - 80;

            c.save();
            c.globalAlpha = alpha;
            c.font = '11px "Microsoft YaHei", sans-serif';
            const tw = Math.min(c.measureText(a.bubble).width, 180);
            const bw = tw + 18, bh = 30;

            // 像素风气泡
            c.fillStyle = '#1c2333';
            this.rr(c, bx - bw / 2, by - bh / 2, bw, bh, 4, true);
            c.strokeStyle = a.accent;
            c.lineWidth = 1.5;
            this.rr(c, bx - bw / 2, by - bh / 2, bw, bh, 4, false, true);

            // 气泡箭头
            c.fillStyle = '#1c2333';
            c.beginPath();
            c.moveTo(bx - 4, by + bh / 2);
            c.lineTo(bx + 4, by + bh / 2);
            c.lineTo(bx, by + bh / 2 + 6);
            c.closePath(); c.fill();
            c.strokeStyle = a.accent;
            c.lineWidth = 1;
            c.beginPath();
            c.moveTo(bx - 4, by + bh / 2);
            c.lineTo(bx, by + bh / 2 + 6);
            c.lineTo(bx + 4, by + bh / 2);
            c.stroke();

            c.fillStyle = '#c9d1d9';
            c.textAlign = 'center'; c.textBaseline = 'middle';
            c.fillText(a.bubble, bx, by, 180);
            c.restore();
        });
    }

    /* ═══════════ MiniMap 小地图 ═══════════ */

    drawMiniMap(c, CW, CH) {
        const mmW = 160;
        const mmH = mmW * (this.H / this.W);
        const mmX = CW - mmW - 16;
        const mmY = CH - mmH - 16;
        const mmScale = mmW / this.W;

        c.save();

        c.fillStyle = 'rgba(13,17,23,.85)';
        c.strokeStyle = 'rgba(48,54,61,.8)';
        c.lineWidth = 1;
        c.beginPath();
        c.rect(mmX - 2, mmY - 2, mmW + 4, mmH + 4);
        c.fill();
        c.stroke();

        c.beginPath();
        c.rect(mmX, mmY, mmW, mmH);
        c.clip();

        // Agent小点（像素风方块）
        this.agents.forEach(a => {
            const ax = mmX + a.x * mmScale;
            const ay = mmY + a.y * mmScale;
            c.fillStyle = this.statusColor(a.status);
            c.fillRect(ax - 3, ay - 3, 6, 6);
        });

        // 当前视口框
        const viewW = CW / (this.scale * this.zoom);
        const viewH = CH / (this.scale * this.zoom);
        const viewCenterX = this.W / 2 - this.camX;
        const viewCenterY = this.H / 2 - this.camY;
        const vx = viewCenterX - viewW / 2;
        const vy = viewCenterY - viewH / 2;

        c.strokeStyle = '#00ff9d';
        c.lineWidth = 1.5;
        c.strokeRect(
            mmX + vx * mmScale,
            mmY + vy * mmScale,
            viewW * mmScale,
            viewH * mmScale
        );

        c.restore();
        c.fillStyle = 'rgba(255,255,255,.4)';
        c.font = '9px "Cascadia Code", monospace';
        c.textAlign = 'right';
        c.fillText('MINIMAP', CW - 20, CH - mmH - 22);
    }

    /* ═══════════ P8-2: 缩放控制按钮 ═══════════ */

    drawZoomControls(c, CW, CH) {
        const bx = 16, by = CH - 100;
        const bw = 32, bh = 32;

        // + 按钮
        c.fillStyle = 'rgba(13,17,23,.8)';
        c.strokeStyle = 'rgba(48,54,61,.8)';
        c.lineWidth = 1;
        this.rrRaw(c, bx, by, bw, bh, 4);
        c.fill(); c.stroke();
        c.fillStyle = 'rgba(255,255,255,.5)';
        c.font = 'bold 16px "Cascadia Code", monospace';
        c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillText('+', bx + bw / 2, by + bh / 2);

        // - 按钮
        this.rrRaw(c, bx, by + bh + 4, bw, bh, 4);
        c.fillStyle = 'rgba(13,17,23,.8)';
        c.fill(); c.stroke();
        c.fillStyle = 'rgba(255,255,255,.5)';
        c.fillText('−', bx + bw / 2, by + bh + 4 + bh / 2);

        // Home 按钮
        this.rrRaw(c, bx, by + (bh + 4) * 2, bw, bh, 4);
        c.fillStyle = 'rgba(13,17,23,.8)';
        c.fill(); c.stroke();
        c.fillStyle = 'rgba(255,255,255,.5)';
        c.font = '12px "Cascadia Code", monospace';
        c.fillText('⌂', bx + bw / 2, by + (bh + 4) * 2 + bh / 2);
    }

    /* ═══════════ Zoom 指示器 ═══════════ */

    drawZoomIndicator(c, CW, CH) {
        const text = `${Math.round(this.zoom * 100)}%`;
        c.save();
        c.fillStyle = 'rgba(0,0,0,.6)';
        c.font = 'bold 12px "Cascadia Code", monospace';
        c.textAlign = 'left';
        const tw = c.measureText(text).width;
        this.rr(c, 16, CH - 36, tw + 16, 24, 4, true);
        c.fillStyle = 'rgba(255,255,255,.6)';
        c.textBaseline = 'middle';
        c.fillText(text, 24, CH - 24);
        c.restore();
    }

    /* ═══════════ P8-2: 悬停提示面板 ═══════════ */

    drawTooltip(c, CW, CH) {
        if (!this.tooltipData) return;

        const dpr = window.devicePixelRatio || 1;
        const a = this.tooltipData.agent;
        let tx = this.tooltipData.screenX * dpr + 20;
        let ty = this.tooltipData.screenY * dpr - 10;

        const tw = 200;
        const th = 120;

        // 边界检测
        if (tx + tw > CW) tx = tx - tw - 40;
        if (ty + th > CH) ty = CH - th - 10;
        if (ty < 0) ty = 10;

        c.save();

        // 背景
        c.fillStyle = 'rgba(22,27,34,.95)';
        this.rr(c, tx, ty, tw, th, 6, true);

        // 边框
        c.strokeStyle = a.accent + '88';
        c.lineWidth = 1.5;
        this.rr(c, tx, ty, tw, th, 6, false, true);

        // 顶部颜色条
        c.fillStyle = a.accent + '33';
        c.fillRect(tx + 1, ty + 1, tw - 2, 4);

        // 名称
        c.fillStyle = a.accent;
        c.font = 'bold 13px "Microsoft YaHei", sans-serif';
        c.textAlign = 'left';
        c.textBaseline = 'top';
        c.fillText(a.name, tx + 12, ty + 14);

        // ID
        c.fillStyle = '#8b949e';
        c.font = '10px "Cascadia Code", monospace';
        c.fillText(`@${a.id}`, tx + 12, ty + 34);

        // 状态
        const sc = this.statusColor(a.status);
        c.fillStyle = sc;
        c.fillRect(tx + 12, ty + 52, 8, 8);
        c.fillStyle = '#c9d1d9';
        c.font = '11px "Cascadia Code", monospace';
        c.fillText(this.statusText(a.status), tx + 26, ty + 52);

        // 当前任务
        if (a.task) {
            c.fillStyle = '#8b949e';
            c.font = '10px "Microsoft YaHei", sans-serif';
            const taskText = a.task.length > 20 ? a.task.substring(0, 20) + '…' : a.task;
            c.fillText(`任务: ${taskText}`, tx + 12, ty + 70);
        }

        // 消息数
        c.fillStyle = '#8b949e';
        c.font = '10px "Cascadia Code", monospace';
        c.fillText(`Messages: ${a.messageCount}`, tx + 12, ty + 90);

        // 提示
        c.fillStyle = 'rgba(255,255,255,.3)';
        c.font = '9px "Cascadia Code", monospace';
        c.fillText('Click for details', tx + 12, ty + 106);

        c.restore();
    }

    /* ═══════════ 粒子 ═══════════ */

    spawnParticles(x, y, color) {
        for (let i = 0; i < 10; i++) {
            const a = (Math.PI * 2 * i) / 10;
            this.particles.push({
                x, y,
                vx: Math.cos(a) * (2 + Math.random()),
                vy: Math.sin(a) * (2 + Math.random()),
                life: 1, color,
                size: 2 + Math.random() * 2
            });
        }
    }

    updateParticles(c) {
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.vx; p.y += p.vy;
            p.vy += 0.05; // 重力
            p.life -= 0.025;
            if (p.life <= 0) { this.particles.splice(i, 1); continue; }

            // 像素风方块粒子
            c.save();
            c.globalAlpha = p.life;
            c.fillStyle = p.color;
            const s = p.size * p.life;
            c.fillRect(p.x - s / 2, p.y - s / 2, s, s);
            c.restore();
        }
    }

    /* ═══════════ 工具 ═══════════ */

    statusColor(s) {
        return { idle: '#8b949e', working: '#58a6ff', communicating: '#3fb950', error: '#f85149', thinking: '#d29922' }[s] || '#8b949e';
    }
    statusText(s) {
        return { idle: '空闲', working: '工作中', communicating: '交流中', error: '出错', thinking: '思考中' }[s] || s;
    }
    ease(t) { return t < .5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2; }

    rr(c, x, y, w, h, r, fill, stroke) {
        c.beginPath();
        c.moveTo(x + r, y);
        c.lineTo(x + w - r, y); c.quadraticCurveTo(x + w, y, x + w, y + r);
        c.lineTo(x + w, y + h - r); c.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        c.lineTo(x + r, y + h); c.quadraticCurveTo(x, y + h, x, y + h - r);
        c.lineTo(x, y + r); c.quadraticCurveTo(x, y, x + r, y);
        c.closePath();
        if (fill) c.fill();
        if (stroke) c.stroke();
    }

    /** 同rr但不自动fill/stroke，让调用者控制 */
    rrRaw(c, x, y, w, h, r) {
        c.beginPath();
        c.moveTo(x + r, y);
        c.lineTo(x + w - r, y); c.quadraticCurveTo(x + w, y, x + w, y + r);
        c.lineTo(x + w, y + h - r); c.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
        c.lineTo(x + r, y + h); c.quadraticCurveTo(x, y + h, x, y + h - r);
        c.lineTo(x, y + r); c.quadraticCurveTo(x, y, x + r, y);
        c.closePath();
    }

    /** P8-2: 绘制五角星 */
    drawStar(c, cx, cy, outerR, innerR, points) {
        c.beginPath();
        for (let i = 0; i < points * 2; i++) {
            const r = i % 2 === 0 ? outerR : innerR;
            const angle = (Math.PI * i / points) - Math.PI / 2;
            const x = cx + Math.cos(angle) * r;
            const y = cy + Math.sin(angle) * r;
            if (i === 0) c.moveTo(x, y);
            else c.lineTo(x, y);
        }
        c.closePath();
        c.fill();
    }

    destroy() {
        if (this.animationId) cancelAnimationFrame(this.animationId);
        this.ready = false;
    }
}

export default OfficeScene;
