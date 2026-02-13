"""
文件: prompts/code_generation_template.py
职责: 代码生成提示词模板 - 为程序员Agent提供游戏代码模板和示例
依赖: 无
被依赖: agents/programmer_agent.py

提供:
  - HTML5游戏标准结构模板
  - JavaScript游戏循环模板
  - 常见游戏类型的代码片段（贪吃蛇、打砖块、跑酷等）

P11优化:
  - 新增精简版Prompt（减少Token消耗）
  - 模板引用替代完整嵌入
"""


# HTML5游戏标准结构模板
HTML5_GAME_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{game_title}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: Arial, sans-serif;
        }}
        #gameCanvas {{
            border: 3px solid #fff;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            background: #000;
        }}
        #ui {{
            margin-top: 20px;
            color: white;
            text-align: center;
            font-size: 18px;
        }}
        #score {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }}
        button {{
            margin: 10px 5px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            background: #fff;
            color: #667eea;
            font-weight: bold;
            transition: transform 0.2s;
        }}
        button:hover {{
            transform: scale(1.05);
        }}
        button:active {{
            transform: scale(0.95);
        }}
    </style>
</head>
<body>
    <h1 style="color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">{game_title}</h1>
    <canvas id="gameCanvas" width="{canvas_width}" height="{canvas_height}"></canvas>
    <div id="ui">
        <div id="score">得分: 0</div>
        <div id="controls">
            <button id="startBtn">开始游戏</button>
            <button id="pauseBtn">暂停</button>
            <button id="restartBtn">重新开始</button>
        </div>
        <div id="instructions" style="margin-top: 15px; font-size: 14px;">
            {game_instructions}
        </div>
    </div>
    <script src="game.js"></script>
</body>
</html>
"""


# JavaScript游戏循环模板
JS_GAME_LOOP_TEMPLATE = """// 游戏主文件 - {game_title}
// 自动生成于 {timestamp}

// 获取Canvas元素和上下文
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// UI元素
const scoreDisplay = document.getElementById('score');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const restartBtn = document.getElementById('restartBtn');

// 游戏状态
let gameState = {{
    running: false,
    paused: false,
    score: 0,
    gameOver: false
}};

// 游戏配置
const config = {{
    fps: 60,
    // 游戏特定配置将在这里添加
}};

// 初始化游戏
function initGame() {{
    console.log('初始化游戏...');
    gameState.running = false;
    gameState.paused = false;
    gameState.score = 0;
    gameState.gameOver = false;
    
    // 初始化游戏对象
    // TODO: 在这里初始化玩家、敌人、道具等
    
    updateScore();
}}

// 游戏主循环
function gameLoop() {{
    if (!gameState.running || gameState.paused) {{
        requestAnimationFrame(gameLoop);
        return;
    }}
    
    // 更新游戏逻辑
    update();
    
    // 渲染画面
    render();
    
    // 检查游戏结束
    if (gameState.gameOver) {{
        handleGameOver();
        return;
    }}
    
    // 继续循环
    requestAnimationFrame(gameLoop);
}}

// 更新游戏逻辑
function update() {{
    // TODO: 更新游戏对象的位置、状态等
    // 例如：移动玩家、移动敌人、检测碰撞等
}}

// 渲染游戏画面
function render() {{
    // 清空画布
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // TODO: 绘制游戏对象
    // 例如：绘制玩家、绘制敌人、绘制UI等
}}

// 处理游戏结束
function handleGameOver() {{
    gameState.running = false;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('游戏结束!', canvas.width / 2, canvas.height / 2 - 30);
    
    ctx.font = '24px Arial';
    ctx.fillText(`最终得分: ${{gameState.score}}`, canvas.width / 2, canvas.height / 2 + 20);
    
    ctx.font = '18px Arial';
    ctx.fillText('点击"重新开始"继续游戏', canvas.width / 2, canvas.height / 2 + 60);
}}

// 更新得分显示
function updateScore() {{
    scoreDisplay.textContent = `得分: ${{gameState.score}}`;
}}

// 键盘输入处理
const keys = {{}};
window.addEventListener('keydown', (e) => {{
    keys[e.key] = true;
    // TODO: 处理特定按键逻辑
}});

window.addEventListener('keyup', (e) => {{
    keys[e.key] = false;
}});

// 按钮事件监听
startBtn.addEventListener('click', () => {{
    if (!gameState.running) {{
        initGame();
        gameState.running = true;
        startBtn.textContent = '游戏中...';
        startBtn.disabled = true;
        gameLoop();
    }}
}});

pauseBtn.addEventListener('click', () => {{
    if (gameState.running) {{
        gameState.paused = !gameState.paused;
        pauseBtn.textContent = gameState.paused ? '继续' : '暂停';
    }}
}});

restartBtn.addEventListener('click', () => {{
    initGame();
    gameState.running = true;
    gameState.gameOver = false;
    startBtn.textContent = '游戏中...';
    startBtn.disabled = true;
    pauseBtn.textContent = '暂停';
    gameLoop();
}});

// 页面加载完成后初始化
window.addEventListener('load', () => {{
    initGame();
    console.log('游戏已准备就绪！点击"开始游戏"按钮开始。');
}});
"""


# 贪吃蛇游戏代码片段
SNAKE_GAME_SNIPPET = """
// 贪吃蛇游戏核心逻辑

// 游戏配置
const GRID_SIZE = 20;  // 网格大小
const GRID_WIDTH = canvas.width / GRID_SIZE;
const GRID_HEIGHT = canvas.height / GRID_SIZE;

// 蛇的初始状态
let snake = {
    body: [{x: 10, y: 10}, {x: 9, y: 10}, {x: 8, y: 10}],
    direction: {x: 1, y: 0},
    nextDirection: {x: 1, y: 0}
};

// 食物位置
let food = {x: 15, y: 15};

// 生成随机食物位置
function generateFood() {
    food = {
        x: Math.floor(Math.random() * GRID_WIDTH),
        y: Math.floor(Math.random() * GRID_HEIGHT)
    };
    
    // 确保食物不在蛇身上
    for (let segment of snake.body) {
        if (segment.x === food.x && segment.y === food.y) {
            generateFood();
            return;
        }
    }
}

// 更新蛇的位置
function updateSnake() {
    // 更新方向（避免反向移动）
    if (snake.nextDirection.x !== -snake.direction.x || 
        snake.nextDirection.y !== -snake.direction.y) {
        snake.direction = {...snake.nextDirection};
    }
    
    // 计算新头部位置
    const head = {
        x: snake.body[0].x + snake.direction.x,
        y: snake.body[0].y + snake.direction.y
    };
    
    // 检查墙壁碰撞
    if (head.x < 0 || head.x >= GRID_WIDTH || 
        head.y < 0 || head.y >= GRID_HEIGHT) {
        gameState.gameOver = true;
        return;
    }
    
    // 检查自身碰撞
    for (let segment of snake.body) {
        if (segment.x === head.x && segment.y === head.y) {
            gameState.gameOver = true;
            return;
        }
    }
    
    // 添加新头部
    snake.body.unshift(head);
    
    // 检查是否吃到食物
    if (head.x === food.x && head.y === food.y) {
        gameState.score += 10;
        updateScore();
        generateFood();
    } else {
        // 移除尾部
        snake.body.pop();
    }
}

// 绘制蛇
function drawSnake() {
    ctx.fillStyle = '#00ff00';
    for (let i = 0; i < snake.body.length; i++) {
        const segment = snake.body[i];
        ctx.fillRect(
            segment.x * GRID_SIZE,
            segment.y * GRID_SIZE,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        );
        
        // 蛇头颜色不同
        if (i === 0) {
            ctx.fillStyle = '#ffff00';
            ctx.fillRect(
                segment.x * GRID_SIZE + 2,
                segment.y * GRID_SIZE + 2,
                GRID_SIZE - 6,
                GRID_SIZE - 6
            );
            ctx.fillStyle = '#00ff00';
        }
    }
}

// 绘制食物
function drawFood() {
    ctx.fillStyle = '#ff0000';
    ctx.fillRect(
        food.x * GRID_SIZE,
        food.y * GRID_SIZE,
        GRID_SIZE - 2,
        GRID_SIZE - 2
    );
}

// 键盘控制
window.addEventListener('keydown', (e) => {
    switch(e.key) {
        case 'ArrowUp':
            snake.nextDirection = {x: 0, y: -1};
            break;
        case 'ArrowDown':
            snake.nextDirection = {x: 0, y: 1};
            break;
        case 'ArrowLeft':
            snake.nextDirection = {x: -1, y: 0};
            break;
        case 'ArrowRight':
            snake.nextDirection = {x: 1, y: 0};
            break;
    }
});
"""


# 打砖块游戏代码片段
BREAKOUT_GAME_SNIPPET = """
// 打砖块游戏核心逻辑

// 挡板
let paddle = {
    x: canvas.width / 2 - 50,
    y: canvas.height - 30,
    width: 100,
    height: 10,
    speed: 8
};

// 球
let ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    radius: 8,
    dx: 4,
    dy: -4
};

// 砖块
let bricks = [];
const BRICK_ROWS = 5;
const BRICK_COLS = 8;
const BRICK_WIDTH = canvas.width / BRICK_COLS - 10;
const BRICK_HEIGHT = 20;

// 初始化砖块
function initBricks() {
    bricks = [];
    for (let row = 0; row < BRICK_ROWS; row++) {
        for (let col = 0; col < BRICK_COLS; col++) {
            bricks.push({
                x: col * (BRICK_WIDTH + 10) + 5,
                y: row * (BRICK_HEIGHT + 10) + 30,
                width: BRICK_WIDTH,
                height: BRICK_HEIGHT,
                visible: true,
                color: `hsl(${row * 40}, 70%, 50%)`
            });
        }
    }
}

// 更新游戏逻辑
function updateBreakout() {
    // 移动球
    ball.x += ball.dx;
    ball.y += ball.dy;
    
    // 球碰墙壁
    if (ball.x - ball.radius < 0 || ball.x + ball.radius > canvas.width) {
        ball.dx = -ball.dx;
    }
    if (ball.y - ball.radius < 0) {
        ball.dy = -ball.dy;
    }
    
    // 球掉落
    if (ball.y + ball.radius > canvas.height) {
        gameState.gameOver = true;
        return;
    }
    
    // 球碰挡板
    if (ball.y + ball.radius > paddle.y &&
        ball.x > paddle.x && ball.x < paddle.x + paddle.width) {
        ball.dy = -Math.abs(ball.dy);
        // 根据击球位置改变角度
        let hitPos = (ball.x - paddle.x) / paddle.width;
        ball.dx = (hitPos - 0.5) * 10;
    }
    
    // 球碰砖块
    for (let brick of bricks) {
        if (!brick.visible) continue;
        
        if (ball.x + ball.radius > brick.x &&
            ball.x - ball.radius < brick.x + brick.width &&
            ball.y + ball.radius > brick.y &&
            ball.y - ball.radius < brick.y + brick.height) {
            
            brick.visible = false;
            ball.dy = -ball.dy;
            gameState.score += 10;
            updateScore();
            
            // 检查是否全部消除
            if (bricks.every(b => !b.visible)) {
                alert('恭喜通关！');
                gameState.gameOver = true;
            }
            break;
        }
    }
    
    // 移动挡板
    if (keys['ArrowLeft'] && paddle.x > 0) {
        paddle.x -= paddle.speed;
    }
    if (keys['ArrowRight'] && paddle.x < canvas.width - paddle.width) {
        paddle.x += paddle.speed;
    }
}

// 绘制游戏
function renderBreakout() {
    // 清空画布
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制挡板
    ctx.fillStyle = '#fff';
    ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
    
    // 绘制球
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
    ctx.closePath();
    
    // 绘制砖块
    for (let brick of bricks) {
        if (brick.visible) {
            ctx.fillStyle = brick.color;
            ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
        }
    }
}
"""


# 跑酷游戏代码片段
RUNNER_GAME_SNIPPET = """
// 跑酷游戏核心逻辑

// 玩家
let player = {
    x: 50,
    y: canvas.height - 60,
    width: 30,
    height: 50,
    velocityY: 0,
    jumping: false
};

// 重力和跳跃
const GRAVITY = 0.6;
const JUMP_STRENGTH = -12;
const GROUND_Y = canvas.height - 60;

// 障碍物
let obstacles = [];
let obstacleTimer = 0;
const OBSTACLE_INTERVAL = 100;  // 帧数

// 创建障碍物
function createObstacle() {
    obstacles.push({
        x: canvas.width,
        y: GROUND_Y,
        width: 20,
        height: 40,
        speed: 4
    });
}

// 更新跑酷游戏
function updateRunner() {
    // 更新玩家
    if (player.jumping) {
        player.velocityY += GRAVITY;
        player.y += player.velocityY;
        
        // 落地
        if (player.y >= GROUND_Y) {
            player.y = GROUND_Y;
            player.velocityY = 0;
            player.jumping = false;
        }
    }
    
    // 跳跃控制
    if (keys[' '] && !player.jumping) {
        player.jumping = true;
        player.velocityY = JUMP_STRENGTH;
    }
    
    // 生成障碍物
    obstacleTimer++;
    if (obstacleTimer >= OBSTACLE_INTERVAL) {
        createObstacle();
        obstacleTimer = 0;
    }
    
    // 更新障碍物
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= obs.speed;
        
        // 移除屏幕外的障碍物
        if (obs.x + obs.width < 0) {
            obstacles.splice(i, 1);
            gameState.score += 5;
            updateScore();
            continue;
        }
        
        // 碰撞检测
        if (player.x < obs.x + obs.width &&
            player.x + player.width > obs.x &&
            player.y < obs.y + obs.height &&
            player.y + player.height > obs.y) {
            gameState.gameOver = true;
        }
    }
}

// 绘制跑酷游戏
function renderRunner() {
    // 清空画布
    ctx.fillStyle = '#87CEEB';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 绘制地面
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(0, GROUND_Y + player.height, canvas.width, 10);
    
    // 绘制玩家
    ctx.fillStyle = '#ff0000';
    ctx.fillRect(player.x, player.y, player.width, player.height);
    
    // 绘制障碍物
    ctx.fillStyle = '#000';
    for (let obs of obstacles) {
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
    }
}
"""


def get_code_template(game_type: str = "generic") -> dict:
    """
    获取特定游戏类型的代码模板
    
    Args:
        game_type: 游戏类型 ("snake", "breakout", "runner", "generic")
    
    Returns:
        包含HTML和JS代码的字典
    """
    templates = {
        "snake": {
            "title": "贪吃蛇游戏",
            "canvas_width": 400,
            "canvas_height": 400,
            "instructions": "使用方向键控制蛇的移动，吃到食物得分",
            "js_snippet": SNAKE_GAME_SNIPPET
        },
        "breakout": {
            "title": "打砖块游戏",
            "canvas_width": 600,
            "canvas_height": 400,
            "instructions": "使用左右方向键移动挡板，消除所有砖块",
            "js_snippet": BREAKOUT_GAME_SNIPPET
        },
        "runner": {
            "title": "跑酷游戏",
            "canvas_width": 600,
            "canvas_height": 300,
            "instructions": "按空格键跳跃，躲避障碍物",
            "js_snippet": RUNNER_GAME_SNIPPET
        },
        "generic": {
            "title": "HTML5游戏",
            "canvas_width": 600,
            "canvas_height": 400,
            "instructions": "使用键盘控制游戏",
            "js_snippet": ""
        }
    }
    
    return templates.get(game_type, templates["generic"])


def get_programmer_enhancement_prompt(project_name: str) -> str:
    """
    生成增强的程序员Agent提示词
    
    这个提示词明确告知Agent必须调用工具写文件
    """
    return f"""你是一位经验丰富的游戏程序员。

【重要】你必须调用工具来写文件，而不是仅仅回复"我会写代码"！

当前项目目录: projects/{project_name}/
输出目录: projects/{project_name}/output/

你的工作流程：
1. 阅读game_design_doc.md和tech_design_doc.md
2. 使用LLM思考游戏代码结构
3. **调用file工具写入代码**：
   await self.call_tool("file", "write", 
                        "projects/{project_name}/output/index.html",
                        html_code)
4. 至少生成3个文件：index.html、game.js、style.css（可选）
5. 回复"代码已写入output目录"

【代码模板】HTML5游戏标准结构：
{HTML5_GAME_TEMPLATE}

【游戏循环模板】：
{JS_GAME_LOOP_TEMPLATE}

【必须使用的工具】：
- self.call_tool("file", "write", path, content)  # 写文件
- self.call_tool("code_search", "check_function_exists", name)  # 检查重复

【代码质量要求】：
1. 使用ES6+语法
2. 代码要有详细注释
3. 函数要单一职责
4. 完善的错误处理
5. 所有数值配置从代码顶部的config对象读取

【游戏类型代码片段】：
- 贪吃蛇: {SNAKE_GAME_SNIPPET[:200]}...
- 打砖块: {BREAKOUT_GAME_SNIPPET[:200]}...
- 跑酷: {RUNNER_GAME_SNIPPET[:200]}...

铁律(不可违反):
1. 收到开发任务后，必须实际调用file工具写文件
2. 不能只回复"我会写xxx"，必须真正执行写文件操作
3. 每个文件写完后，在回复中说明"已写入xxx文件"
4. 所有游戏文件必须写入projects/{project_name}/output/目录
"""


# ==================== P11新增: 精简版Prompt ====================

def get_compact_programmer_prompt(project_name: str) -> str:
    """
    P11优化: 精简版程序员Agent提示词
    
    相比原版减少约70%的Token消耗:
    - 不嵌入完整代码模板，只提供结构指引
    - 使用简洁的格式
    
    Args:
        project_name: 项目名称
        
    Returns:
        精简版提示词
    """
    return f"""你是游戏程序员。

【输出目录】projects/{project_name}/output/

【必须操作】
1. 先读取shared_knowledge/下的GDD和TDD
2. 生成index.html和game.js
3. 调用工具写文件: await self.call_tool("file", "write", path, content)

【HTML结构】
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>游戏</title></head>
<body><canvas id="gameCanvas"></canvas><script src="game.js"></script></body></html>

【JS结构】
- initGame() 初始化
- gameLoop() 主循环: update() + render()
- handleInput() 输入处理
- config = {{}} 配置对象

【质量要求】ES6+ | 注释完整 | 配置外置 | 无硬编码

【铁律】必须实际调用file工具写文件，不能只回复"我会写"。"""


def get_compact_planner_prompt() -> str:
    """
    P11优化: 精简版策划Agent提示词
    """
    return """你是游戏策划。

【输出文件】shared_knowledge/game_design_doc.md

【GDD结构】
1. 游戏概述（类型、目标用户）
2. 核心玩法（操作、规则、胜负条件）
3. 游戏元素（角色、道具、场景）
4. 界面设计（UI布局）

【要求】
- 使用Markdown格式
- 内容具体可执行
- 考虑HTML5 Canvas实现

完成后调用: await self.call_tool("file", "write", path, content)"""


def get_compact_tester_prompt() -> str:
    """
    P11优化: 精简版测试Agent提示词
    """
    return """你是测试工程师。

【任务】测试游戏功能，检查Bug

【测试流程】
1. 读取game_design_doc.md了解预期行为
2. 运行游戏检查:
   - 页面是否正常加载
   - 核心功能是否工作
   - 边界情况处理
3. 发现Bug记录到bug_tracker.yaml

【Bug报告格式】
- 问题描述
- 复现步骤  
- 期望行为
- 实际行为

调用code_runner工具测试: await self.call_tool("code_runner", "execute_game_test", project_dir)"""


def get_game_type_template_hint(game_type: str) -> str:
    """
    根据游戏类型返回简洁的实现提示
    
    Args:
        game_type: 游戏类型
        
    Returns:
        实现提示字符串
    """
    hints = {
        "counter": """
【计数器游戏要点】
- 变量: count = 0
- 按钮: increment(), decrement(), reset()
- 显示: 更新DOM元素textContent""",

        "snake": """
【贪吃蛇要点】
- 网格: GRID_SIZE = 20
- 蛇: body数组, direction方向
- 食物: 随机位置
- 碰撞: 检测墙壁和自身""",

        "breakout": """
【打砖块要点】
- 挡板: 跟随鼠标/键盘
- 球: dx, dy速度
- 砖块: 二维数组
- 碰撞: 矩形检测""",

        "runner": """
【跑酷要点】
- 玩家: 重力, 跳跃
- 障碍: 随机生成, 向左移动
- 碰撞: AABB检测
- 分数: 时间或距离"""
    }
    
    # 尝试模糊匹配
    game_type_lower = game_type.lower()
    for key, hint in hints.items():
        if key in game_type_lower:
            return hint
    
    return ""  # 默认不返回提示


def estimate_prompt_tokens(prompt: str) -> int:
    """
    估算Prompt的Token数量
    
    Args:
        prompt: 提示词文本
        
    Returns:
        估算的Token数量
    """
    # 简单估算: 英文约4字符/token, 中文约2字符/token
    # 这里用保守估计: 3字符/token
    return len(prompt) // 3
