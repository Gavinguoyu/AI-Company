/**
 * 消息气泡动画系统
 * 负责消息在Agent之间的飞行动画
 */

export class MessageBubble {
    /**
     * 创建消息飞行动画
     * @param {PIXI.Container} container - 场景容器
     * @param {Object} fromPos - 起始位置 {x, y}
     * @param {Object} toPos - 目标位置 {x, y}
     * @param {Function} onComplete - 完成回调
     */
    static flyMessage(container, fromPos, toPos, onComplete) {
        // 创建消息图标（橙色圆球）
        const message = new window.PIXI.Graphics();
        message.beginFill(0xf39c12);  // 橙色
        message.drawCircle(0, 0, 12);
        message.endFill();
        
        // 添加白色边框
        message.lineStyle(2, 0xffffff, 1);
        message.drawCircle(0, 0, 12);
        
        // 添加邮件图标（简单的线条）
        const icon = new window.PIXI.Graphics();
        icon.lineStyle(2, 0xffffff, 1);
        icon.moveTo(-6, -3);
        icon.lineTo(0, 2);
        icon.lineTo(6, -3);
        message.addChild(icon);
        
        message.position.set(fromPos.x, fromPos.y);
        container.addChild(message);
        
        // 动画参数
        const startTime = Date.now();
        const duration = 1000; // 1秒
        const startX = fromPos.x;
        const startY = fromPos.y;
        const endX = toPos.x;
        const endY = toPos.y;
        
        // 计算贝塞尔曲线控制点（让消息走弧线）
        const controlX = (startX + endX) / 2;
        const controlY = Math.min(startY, endY) - 50; // 弧线顶点
        
        // 动画循环
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // 缓动函数（ease-in-out）
            const easeProgress = progress < 0.5
                ? 2 * progress * progress
                : 1 - Math.pow(-2 * progress + 2, 2) / 2;
            
            // 贝塞尔曲线插值（二次贝塞尔）
            const t = easeProgress;
            const x = Math.pow(1 - t, 2) * startX + 2 * (1 - t) * t * controlX + Math.pow(t, 2) * endX;
            const y = Math.pow(1 - t, 2) * startY + 2 * (1 - t) * t * controlY + Math.pow(t, 2) * endY;
            
            message.position.set(x, y);
            
            // 添加旋转效果
            message.rotation = progress * Math.PI * 2;
            
            // 添加缩放效果（飞行时变小，到达时变大）
            const scale = progress < 0.5 
                ? 1 - progress * 0.4 
                : 0.8 + (progress - 0.5) * 0.4;
            message.scale.set(scale);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // 动画完成
                container.removeChild(message);
                message.destroy();
                
                if (onComplete) {
                    onComplete();
                }
            }
        };
        
        // 开始动画
        animate();
    }

    /**
     * 创建系统通知气泡（在屏幕中央）
     * @param {PIXI.Container} container - 场景容器
     * @param {string} text - 通知文本
     * @param {number} duration - 显示时长（毫秒）
     */
    static showNotification(container, text, duration = 2000) {
        // 创建通知容器
        const notification = new window.PIXI.Container();
        notification.position.set(400, 100); // 屏幕上方中央
        
        // 背景
        const bg = new window.PIXI.Graphics();
        bg.beginFill(0x2c3e50, 0.9);
        bg.drawRoundedRect(-150, -30, 300, 60, 10);
        bg.endFill();
        
        // 边框
        bg.lineStyle(2, 0x3498db, 1);
        bg.drawRoundedRect(-150, -30, 300, 60, 10);
        
        notification.addChild(bg);
        
        // 文字
        const notificationText = new window.PIXI.Text(text, {
            fontSize: 16,
            fill: 0xffffff,
            fontWeight: 'bold',
            align: 'center',
            wordWrap: true,
            wordWrapWidth: 280
        });
        notificationText.anchor.set(0.5);
        notification.addChild(notificationText);
        
        // 添加到场景
        container.addChild(notification);
        
        // 淡入动画
        notification.alpha = 0;
        const fadeInDuration = 300;
        const fadeInStart = Date.now();
        
        const fadeIn = () => {
            const elapsed = Date.now() - fadeInStart;
            notification.alpha = Math.min(elapsed / fadeInDuration, 1);
            
            if (elapsed < fadeInDuration) {
                requestAnimationFrame(fadeIn);
            } else {
                // 停留一段时间后淡出
                setTimeout(() => {
                    const fadeOutStart = Date.now();
                    const fadeOutDuration = 300;
                    
                    const fadeOut = () => {
                        const elapsed = Date.now() - fadeOutStart;
                        notification.alpha = Math.max(1 - elapsed / fadeOutDuration, 0);
                        
                        if (elapsed < fadeOutDuration) {
                            requestAnimationFrame(fadeOut);
                        } else {
                            container.removeChild(notification);
                            notification.destroy({ children: true });
                        }
                    };
                    
                    fadeOut();
                }, duration);
            }
        };
        
        fadeIn();
    }

    /**
     * 创建状态变化特效（彩色粒子效果）
     * @param {PIXI.Container} container - 场景容器
     * @param {Object} position - 位置 {x, y}
     * @param {number} color - 颜色
     */
    static showStatusEffect(container, position, color = 0x2ecc71) {
        const particleCount = 8;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = new window.PIXI.Graphics();
            particle.beginFill(color);
            particle.drawCircle(0, 0, 4);
            particle.endFill();
            
            particle.position.set(position.x, position.y);
            container.addChild(particle);
            
            // 随机方向
            const angle = (Math.PI * 2 * i) / particleCount;
            const speed = 2;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;
            
            // 粒子动画
            const startTime = Date.now();
            const duration = 500;
            
            const animate = () => {
                const elapsed = Date.now() - startTime;
                const progress = elapsed / duration;
                
                if (progress < 1) {
                    particle.x += vx;
                    particle.y += vy;
                    particle.alpha = 1 - progress;
                    particle.scale.set(1 - progress * 0.5);
                    
                    requestAnimationFrame(animate);
                } else {
                    container.removeChild(particle);
                    particle.destroy();
                }
            };
            
            animate();
        }
    }
}

export default MessageBubble;
