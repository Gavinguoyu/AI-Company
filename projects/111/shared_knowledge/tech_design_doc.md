# 111 技术设计文档

## 1. 架构设计
好的，PM。我已收到项目启动通知，并了解了制作Flappy Bird风格游戏的需求。

作为一名经验丰富的游戏程序员，我将按照以下架构和文件结构来开发：

**技术架构设计：**

1.  **文件结构:**
    *   `index.html`: 游戏入口，负责设置Canvas元素和加载游戏脚本及样式。
    *   `style.css`: 负责Canvas和页面元素的样式。
    *   `game.js`: 包含所有游戏逻辑，包括游戏循环、对象（小鸟、管道）、碰撞检测、得分管理和游戏状态。

2.  **模块划分 (`game.js` 内部):**
    *   **`CONFIG` 对象:** 集中管理所有游戏参数，如Canvas尺寸、小鸟速度、重力、管道间距、移动速度等。
    *   **`gameState` 对象:** 存储当前游戏状态，如是否运行、是否暂停、当前分数等。
    *   **`Bird` 类:**
        *   管理小鸟的位置 (`x`, `y`)、速度 (`velocityY`)。
        *   提供 `flap()` 方法处理玩家输入。
        *   提供 `update()` 方法根据重力更新小鸟位置和速度。
        *   提供 `draw()` 方法绘制小鸟。
        *   提供 `getBounds()` 方法获取小鸟的碰撞边界。
    *   **`Pipe` 类:**
        *   管理单个管道（顶部和底部）的位置、尺寸。
        *   提供 `update()` 方法使其向左移动。
        *   提供 `draw()` 方法绘制管道。
        *   提供 `getTopBounds()` 和 `getBottomBounds()` 方法获取管道的碰撞边界。
    *   **`Game` 类 (主游戏逻辑):**
        *   初始化Canvas和2D渲染上下文。
        *   实例化 `Bird` 对象和管理 `pipes` 数组。
        *   处理用户输入（点击/空格键）来启动游戏或让小鸟拍打翅膀。
        *   包含 `gameLoop()` 方法，负责调用 `update()` 和 `render()`。
        *   `update()`:
            *   更新小鸟状态。
            *   生成新管道。
            *   更新所有管道状态，并移除屏幕外的管道。
            *   执行碰撞检测（小鸟与管道，小鸟与地面）。
            *   更新分数。
            *   更新背景（视差滚动）。
        *   `render()`:
            *   清空Canvas。
            *   绘制背景。
            *   绘制所有管道。
            *   绘制小鸟。
            *   绘制地面。
            *   绘制当前分数。
        *   `spawnPipe()`: 负责生成新的随机高度的管道。
        *   `checkCollision()`: 负责检测小鸟与管道的碰撞。
        *   `gameOver()`: 处理游戏结束逻辑，显示结束画面并提供重新开始选项。
        *   `resetGame()`: 重置所有游戏状态，准备重新开始。
        *   `startGame()`: 开始游戏。

3.  **游戏循环 (`game.js`):**
    ```javascript
    function gameLoop() {
        if (!gameState.running || gameState.paused) return; // 检查游戏状态
        update();  // 更新游戏逻辑
        render();  // 绘制画面
        requestAnimationFrame(gameLoop); // 请求下一帧
    }
    ```

**`api_registry.yaml` 更新:**
当前项目是一个独立的HTML5游戏，不涉及外部API调用，因此无需更新 `api_registry.yaml`。

现在，我将开始编写代码文件。

---
### 1. 编写 `index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flappy Bird Clone</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="game-container">
        <!-- 游戏Canvas元素 -->
        <canvas id="gameCanvas"></canvas>
    </div>

    <!-- 引入游戏主逻辑脚本 -->
    <script src="game.js"></script>
</body>
</html>
```
已写入 `projects/111/output/index.html`

---
### 2. 编写 `style.css`

```css
/* style.css: 基础样式，用于居中Canvas和设置背景 */
body {
    margin: 0;
    overflow: hidden; /* 防止滚动条 */
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh; /* 确保body至少占满视口高度 */
    background-color: #333; /* 页面背景色 */
    font-family: Arial, sans-serif;
}

#game-container {
    border: 5px solid #000; /* 游戏边框 */
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5); /* 阴影效果 */
    background-color: #fff; /* Canvas容器背景 */
}

canvas {
    display: block; /* 移除Canvas底部多余空间 */
    background-color: #70c5ce; /* 游戏背景色，将被游戏绘制覆盖 */
}
```
已写入 `projects/111/output/style.css`

---
### 3. 编写 `game.js`

```javascript
/**
 * game.js
 * Flappy Bird 风格游戏主逻辑
 * 作者: 经验丰富的游戏程序员
 * 日期: 2023-10-27
 */

// ============================================================================
// 1. 游戏配置 (CONFIG)
// 集中管理所有游戏参数，方便调整
// ============================================================================
const CONFIG = {
    // Canvas 尺寸
    CANVAS_WIDTH: 800,
    CANVAS_HEIGHT: 600,

    // 小鸟属性
    BIRD_WIDTH: 40,
    BIRD_HEIGHT: 30,
    BIRD_START_X: 100, // 小鸟初始X位置
    BIRD_FLAP_VELOCITY: -7, // 拍打翅膀时的垂直速度 (向上为负)
    BIRD_GRAVITY: 0.5, // 重力加速度 (向下为正)
    BIRD_MAX_VELOCITY: 10, // 最大下落速度
    BIRD_MIN_VELOCITY: -10, // 最大上升速度

    // 管道属性
    PIPE_WIDTH: 80,
    PIPE_GAP: 180, // 上下管道之间的垂直间距
    PIPE_SPEED: 3, // 管道水平移动速度
    PIPE_SPAWN_INTERVAL: 2000, // 生成新管道的时间间隔 (毫秒)
    PIPE_MIN_HEIGHT: 80, // 管道的最小高度 (顶部或底部)

    // 游戏属性
    GROUND_HEIGHT: 50, // 地面高度
    BACKGROUND_SCROLL_SPEED: 0.5, // 背景视差滚动速度
    GAME_OVER_TEXT_COLOR: 'white',
    GAME_OVER_BACKGROUND_COLOR: 'rgba(0, 0, 0, 0.7)',
    SCORE_TEXT_COLOR: 'white',
};

// ============================================================================
// 2. 游戏状态 (gameState)
// 存储当前游戏运行状态和分数
// ============================================================================
const gameState = {
    running: false, // 游戏是否正在运行
    paused: false,  // 游戏是否暂停 (本游戏未使用，但保留标准)
    score: 0,       // 当前得分
    lastPipeSpawnTime: 0, // 上次生成管道的时间戳
};

// ============================================================================
// 3. Bird 类
// 管理小鸟的属性、行为和绘制
// ============================================================================
class Bird {
    /**
     * @param {CanvasRenderingContext2D} ctx - 2D渲染上下文
     * @param {number} startY - 小鸟的初始Y坐标
     */
    constructor(ctx, startY) {
        this.ctx = ctx;
        this.x = CONFIG.BIRD_START_X;
        this.y = startY;
        this.width = CONFIG.BIRD_WIDTH;
        this.height = CONFIG.BIRD_HEIGHT;
        this.velocityY = 0; // 垂直速度
    }

    /**
     * 拍打翅膀，给予小鸟一个向上的速度
     */
    flap() {
        this.velocityY = CONFIG.BIRD_FLAP_VELOCITY;
    }

    /**
     * 更新小鸟的位置和速度
     */
    update() {
        // 应用重力
        this.velocityY += CONFIG.BIRD_GRAVITY;

        // 限制垂直速度，防止过快上升或下落
        if (this.velocityY > CONFIG.BIRD_MAX_VELOCITY) {
            this.velocityY = CONFIG.BIRD_MAX_VELOCITY;
        }
        if (this.velocityY < CONFIG.BIRD_MIN_VELOCITY) {
            this.velocityY = CONFIG.BIRD_MIN_VELOCITY;
        }

        // 更新Y坐标
        this.y += this.velocityY;

        // 边界检查：防止小鸟飞出屏幕顶部
        if (this.y < 0) {
            this.y = 0;
            this.velocityY = 0; // 碰到顶部后停止上升
        }
    }

    /**
     * 绘制小鸟
     */
    draw() {
        this.ctx.fillStyle = 'yellow'; // 小鸟颜色
        this.ctx.strokeStyle = 'orange'; // 小鸟边框
        this.ctx.lineWidth = 2;

        this.ctx.beginPath();
        this.ctx.arc(this.x + this.width / 2, this.y + this.height / 2, this.width / 2, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.stroke();

        // 简单的眼睛
        this.ctx.fillStyle = 'black';
        this.ctx.beginPath();
        this.ctx.arc(this.x + this.width * 0.7, this.y + this.height * 0.3, 3, 0, Math.PI * 2);
        this.ctx.fill();
    }

    /**
     * 获取小鸟的碰撞边界
     * @returns {{x: number, y: number, width: number, height: number}} 边界矩形
     */
    getBounds() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height
        };
    }
}

// ============================================================================
// 4. Pipe 类
// 管理单个管道（顶部和底部）的属性、行为和绘制
// ============================================================================
class Pipe {
    /**
     * @param {CanvasRenderingContext2D} ctx - 2D渲染上下文
     * @param {number} x - 管道的X坐标 (最右侧)
     * @param {number} topHeight - 顶部管道的高度
     * @param {number} bottomHeight - 底部管道的高度
     * @param {number} canvasHeight - Canvas的高度
     * @param {number} groundHeight - 地面高度
     */
    constructor(ctx, x, topHeight, bottomHeight, canvasHeight, groundHeight) {
        this.ctx = ctx;
        this.x = x;
        this.width = CONFIG.PIPE_WIDTH;
        this.topHeight = topHeight;
        // 底部管道的Y坐标计算：Canvas总高 - 地面高 - 底部管道高
        this.bottomY = canvasHeight - groundHeight - bottomHeight;
        this.bottomHeight = bottomHeight;
        this.passed = false; // 标记小鸟是否已通过此管道，用于计分
    }

    /**
     * 更新管道的位置
     */
    update() {
        this.x -= CONFIG.PIPE_SPEED; // 管道向左移动
    }

    /**
     * 绘制管道
     */
    draw() {
        this.ctx.fillStyle = 'green'; // 管道颜色
        this.ctx.strokeStyle = 'darkgreen'; // 管道边框
        this.ctx.lineWidth = 2;

        // 绘制顶部管道
        this.ctx.fillRect(this.x, 0, this.width, this.topHeight);
        this.ctx.strokeRect(this.x, 0, this.width, this.topHeight);

        // 绘制底部管道
        this.ctx.fillRect(this.x, this.bottomY, this.width, this.bottomHeight);
        this.ctx.strokeRect(this.x, this.bottomY, this.width, this.bottomHeight);
    }

    /**
     * 获取顶部管道的碰撞边界
     * @returns {{x: number, y: number, width: number, height: number}} 边界矩形
     */
    getTopBounds() {
        return {
            x: this.x,
            y: 0,
            width: this.width,
            height: this.topHeight
        };
    }

    /**
     * 获取底部管道的碰撞边界
     * @returns {{x: number, y: number, width: number, height: number}} 边界矩形
     */
    getBottomBounds() {
        return {
            x: this.x,
            y: this.bottomY,
            width: this.width,
            height: this.bottomHeight
        };
    }
}

// ============================================================================
// 5. Game 类
// 游戏主逻辑，管理游戏流程、对象和状态
// ============================================================================
class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        // 错误处理：检查Canvas元素是否存在
        if (!this.canvas) {
            console.error("Critical Error: Canvas element with ID 'gameCanvas' not found!");
            return;
        }
        this.ctx = this.canvas.getContext('2d');
        // 错误处理：检查2D渲染上下文是否可用
        if (!this.ctx) {
            console.error("Critical Error: 2D rendering context not supported by the browser!");
            return;
        }

        // 设置Canvas尺寸
        this.canvas.width = CONFIG.CANVAS_WIDTH;
        this.canvas.height = CONFIG.CANVAS_HEIGHT;

        this.bird = null; // 小鸟实例，将在resetGame中初始化
        this.pipes = [];  // 管道数组
        this.backgroundX = 0; // 用于背景视差滚动

        this.initEventListeners();
        this.resetGame(); // 初始化游戏状态并显示开始画面
    }

    /**
     * 初始化事件监听器 (鼠标点击和键盘输入)
     */
    initEventListeners() {
        // 鼠标点击事件：用于拍打翅膀或开始游戏
        this.canvas.addEventListener('click', () => {
            if (gameState.running && !gameState.paused) {
                this.bird.flap();
            } else if (!gameState.running) {
                this.startGame();
            }
        });

        // 键盘按下事件：空格键用于拍打翅膀或开始游戏
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault(); // 阻止空格键的默认行为 (如页面滚动)
                if (gameState.running && !gameState.paused) {
                    this.bird.flap();
                } else if (!gameState.running) {
                    this.startGame();
                }
            }
        });
    }

    /**
     * 重置游戏到初始状态
     */
    resetGame() {
        gameState.running = false;
        gameState.paused = false

## 2. 文件结构
```
output/
├── index.html      # 入口文件
├── js/             # JavaScript文件
│   ├── game.js     # 主游戏逻辑
│   └── config.js   # 配置文件
├── assets/         # 美术素材
└── css/            # 样式文件
```

## 3. 模块划分
详见 api_registry.yaml

---
文档版本: 1.0
创建时间: 2026-02-12T16:15:27.908394
创建人: 程序员Agent
