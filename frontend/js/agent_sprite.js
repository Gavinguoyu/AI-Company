/**
 * Agent精灵类
 * 代表办公室中的一个AI Agent
 */

export class AgentSprite {
    constructor(agentId, x, y, name, emoji) {
        this.agentId = agentId;
        this.name = name;
        this.emoji = emoji;
        this.status = 'idle';
        this.currentTask = '';
        
        // 创建容器
        this.container = new window.PIXI.Container();
        this.container.position.set(x, y);
        
        // 创建工位背景（桌子）
        this.createDesk();
        
        // 创建头像（使用Emoji）
        this.createAvatar();
        
        // 创建名牌
        this.createNameTag();
        
        // 创建状态指示器
        this.createStatusIndicator();
        
        // 气泡容器
        this.bubbleContainer = null;
    }

    /**
     * 创建桌子背景
     */
    createDesk() {
        const desk = new window.PIXI.Graphics();
        desk.beginFill(0x8b4513, 0.5);  // 棕色半透明
        desk.drawRoundedRect(-40, 20, 80, 60, 5);
        desk.endFill();
        this.container.addChild(desk);
    }

    /**
     * 创建头像（使用Emoji作为文字精灵）
     */
    createAvatar() {
        this.avatar = new window.PIXI.Text(this.emoji, {
            fontSize: 48,
            fontFamily: 'Arial, sans-serif'
        });
        this.avatar.anchor.set(0.5);
        this.avatar.position.y = 0;
        this.container.addChild(this.avatar);
        
        // 添加简单的呼吸动画
        let time = 0;
        this.app = this.container;
        const animate = () => {
            time += 0.05;
            this.avatar.scale.set(1 + Math.sin(time) * 0.05);
        };
        
        // 如果有ticker就添加动画
        if (window.PIXI && window.PIXI.Ticker) {
            window.PIXI.Ticker.shared.add(animate);
        }
    }

    /**
     * 创建名牌
     */
    createNameTag() {
        this.nameText = new window.PIXI.Text(this.name, {
            fontSize: 14,
            fill: 0xffffff,
            fontWeight: 'bold',
            align: 'center'
        });
        this.nameText.anchor.set(0.5);
        this.nameText.position.y = 60;
        this.container.addChild(this.nameText);
        
        // 角色ID（小字）
        this.roleText = new window.PIXI.Text(this.agentId, {
            fontSize: 10,
            fill: 0xaaaaaa,
            align: 'center'
        });
        this.roleText.anchor.set(0.5);
        this.roleText.position.y = 75;
        this.container.addChild(this.roleText);
    }

    /**
     * 创建状态指示器（彩色圆圈）
     */
    createStatusIndicator() {
        this.statusCircle = new window.PIXI.Graphics();
        this.statusCircle.position.set(0, -35);
        this.container.addChild(this.statusCircle);
        
        // 初始状态
        this.updateStatusIndicator();
    }

    /**
     * 更新状态
     * @param {string} status - 状态 (idle/working/communicating/error)
     * @param {string} task - 当前任务
     */
    updateStatus(status, task = '') {
        this.status = status;
        this.currentTask = task;
        this.updateStatusIndicator();
    }

    /**
     * 更新状态指示器颜色
     */
    updateStatusIndicator() {
        const colors = {
            'idle': 0x95a5a6,          // 灰色 - 空闲
            'working': 0x3498db,        // 蓝色 - 工作中
            'communicating': 0x2ecc71,  // 绿色 - 交流中
            'error': 0xe74c3c,          // 红色 - 错误
            'thinking': 0xf39c12        // 橙色 - 思考中
        };
        
        const color = colors[this.status] || colors.idle;
        
        this.statusCircle.clear();
        this.statusCircle.beginFill(color);
        this.statusCircle.drawCircle(0, 0, 10);
        this.statusCircle.endFill();
        
        // 添加发光效果
        this.statusCircle.lineStyle(2, color, 0.5);
        this.statusCircle.drawCircle(0, 0, 12);
    }

    /**
     * 显示对话气泡
     * @param {string} content - 消息内容
     */
    showBubble(content) {
        // 移除旧气泡
        if (this.bubbleContainer) {
            this.container.removeChild(this.bubbleContainer);
        }
        
        // 创建新气泡
        this.bubbleContainer = new window.PIXI.Container();
        this.bubbleContainer.position.set(0, -80);
        
        // 截断长文本
        const displayText = content.length > 30 ? content.substring(0, 30) + '...' : content;
        
        // 气泡文字
        const bubbleText = new window.PIXI.Text(displayText, {
            fontSize: 12,
            fill: 0x000000,
            wordWrap: true,
            wordWrapWidth: 150,
            align: 'center'
        });
        bubbleText.anchor.set(0.5);
        
        // 气泡背景
        const bubbleBg = new window.PIXI.Graphics();
        const padding = 8;
        const bubbleWidth = Math.min(bubbleText.width + padding * 2, 160);
        const bubbleHeight = bubbleText.height + padding * 2;
        
        bubbleBg.beginFill(0xffffff);
        bubbleBg.drawRoundedRect(
            -bubbleWidth / 2,
            -bubbleHeight / 2,
            bubbleWidth,
            bubbleHeight,
            8
        );
        bubbleBg.endFill();
        
        // 添加边框
        bubbleBg.lineStyle(2, 0x333333, 1);
        bubbleBg.drawRoundedRect(
            -bubbleWidth / 2,
            -bubbleHeight / 2,
            bubbleWidth,
            bubbleHeight,
            8
        );
        
        // 气泡尾巴（三角形）
        bubbleBg.beginFill(0xffffff);
        bubbleBg.moveTo(-5, bubbleHeight / 2);
        bubbleBg.lineTo(5, bubbleHeight / 2);
        bubbleBg.lineTo(0, bubbleHeight / 2 + 8);
        bubbleBg.lineTo(-5, bubbleHeight / 2);
        bubbleBg.endFill();
        
        this.bubbleContainer.addChild(bubbleBg);
        this.bubbleContainer.addChild(bubbleText);
        
        this.container.addChild(this.bubbleContainer);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (this.bubbleContainer) {
                this.container.removeChild(this.bubbleContainer);
                this.bubbleContainer = null;
            }
        }, 3000);
    }

    /**
     * 销毁精灵
     */
    destroy() {
        if (this.container) {
            this.container.destroy({ children: true });
        }
    }
}

export default AgentSprite;
