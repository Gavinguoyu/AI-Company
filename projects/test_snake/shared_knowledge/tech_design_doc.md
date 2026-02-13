# test_snake 技术设计文档

## 1. 架构设计
好的，PM。我已仔细阅读了您提供的 `game_design_doc.md` 和 `project_rules.yaml`。

根据这些文档，我设计了技术架构，确定了文件结构和模块划分，并更新了 `api_registry.yaml` 以反映这些设计决策。

---

## 技术架构设计

### 1. 文件结构

为了遵循 `project_rules.yaml` 中的文件结构规范并实现模块化，我们将采用以下文件结构：

```
projects/test_snake/output/
├── index.html                  # 游戏入口，包含Canvas和UI元素
├── css/
│   └── style.css               # 游戏样式表
└── js/                         # JavaScript 脚本目录
    ├── config.js               # 游戏配置常量
    ├── utils.js                # 通用工具函数
    ├── snake.js                # 蛇的逻辑 (Snake 类)
    ├── food.js                 # 食物的逻辑 (Food 类)
    ├── ui.js                   # 用户界面管理 (UIManager 类)
    ├── input.js                # 用户输入处理 (InputHandler 类)
    └── game.js                 # 游戏主逻辑和协调 (GameManager 类或直接对象)
```

### 2. 模块划分与职责

*   **`index.html`**:
    *   **职责**: 提供游戏的 HTML 骨架，包括 `<canvas>` 元素用于游戏渲染，以及用于显示分数、最高分、游戏结束信息和开始/重新开始按钮的 UI 元素。引入 `style.css` 和 `js/game.js`。
*   **`css/style.css`**:
    *   **职责**: 定义 Canvas 容器、UI 元素（如分数显示、游戏结束弹窗、按钮）的样式，确保游戏界面美观且响应式。
*   **`js/config.js`**:
    *   **职责**: 存储所有从 `game_config.yaml` 转换而来的游戏配置常量。所有游戏数值都应从这里读取，避免硬编码。
*   **`js/utils.js`**:
    *   **职责**: 提供通用的辅助函数，例如在网格中生成随机空闲位置的函数。
*   **`js/snake.js`**:
    *   **职责**: 封装 `Snake` 类的所有逻辑。管理蛇的身体节、移动、方向改变、增长、自身碰撞检测以及在 Canvas 上的绘制。
*   **`js/food.js`**:
    *   **职责**: 封装 `Food` 类的所有逻辑。管理食物的位置生成、获取以及在 Canvas 上的绘制。
*   **`js/ui.js`**:
    *   **职责**: 封装 `UIManager` 类的所有逻辑。负责与 DOM 交互，更新分数、最高分显示，以及控制游戏开始/结束界面的显示与隐藏。
*   **`js/input.js`**:
    *   **职责**: 封装 `InputHandler` 类的所有逻辑。负责监听键盘事件，并将玩家的输入（如方向键、重新开始键）转换为游戏可以处理的动作，通过回调函数通知游戏核心逻辑。
*   **`js/game.js`**:
    *   **职责**: 游戏的中心协调者。包含游戏主循环 (`gameLoop`)，负责初始化所有模块，管理游戏状态（运行中、暂停、结束），处理游戏逻辑更新 (`update`) 和画面渲染 (`render`)，以及协调蛇、食物、UI 和输入之间的交互。处理墙壁碰撞和食物碰撞，以及游戏结束条件。

### 3. 更新 `api_registry.yaml`

我已根据上述技术架构设计，对 `api_registry.yaml` 进行了更新。主要变化包括：

*   为每个 API/函数添加了 `module` 字段，明确其所属的文件。
*   将一些通用函数（如 `eatFood`）从特定实体模块（如 `food_logic`）移到了 `game_core`，因为它们涉及多个实体的交互。
*   细化了类构造函数和方法的描述，使其更符合模块化设计。
*   新增了 `utility_functions` 和 `game_configuration` 分类，以包含 `utils.js` 和 `config.js` 中的内容。

---
**文件: projects/test_snake/output/api_registry.yaml**
```yaml
# 文件: api_registry.yaml
# 职责: 注册和描述项目中的主要API/函数，避免重复开发
# ==========================================
# 项目名称: test_snake
# 创建时间: 2026-02-13T15:40:40.860580
# ==========================================

# ------------------------------------------
# Module: game.js (Core Game Logic)
# ------------------------------------------
game_core:
  initGame:
    description: "初始化游戏环境，包括Canvas、上下文、模块实例、事件监听和初始游戏状态。"
    module: "game.js"
    params: []
    returns: "void"
  startGame:
    description: "重置游戏状态，启动主游戏循环，显示游戏界面。"
    module: "game.js"
    params: []
    returns: "void"
  endGame:
    description: "处理游戏结束逻辑，停止游戏循环，保存最高分，显示游戏结束界面。"
    module: "game.js"
    params:
      - name: "isNewHighscore"
        type: "boolean"
        description: "是否创造了新的最高分"
    returns: "void"
  gameLoop:
    description: "主游戏循环，使用requestAnimationFrame进行动画更新和渲染。"
    module: "game.js"
    params:
      - name: "currentTime"
        type: "DOMHighResTimeStamp"
        description: "当前时间戳，由requestAnimationFrame提供"
    returns: "void"
  update:
    description: "更新游戏逻辑，包括蛇的移动、碰撞检测、食物生成等。"
    module: "game.js"
    params: []
    returns: "void"
  render:
    description: "绘制画面，清空Canvas并绘制所有游戏元素。"
    module: "game.js"
    params: []
    returns: "void"
  checkWallCollision:
    description: "检测蛇头是否与游戏边界发生碰撞。"
    module: "game.js"
    params:
      - name: "headPosition"
        type: "object {x: number, y: number}"
        description: "蛇头的当前网格坐标"
    returns: "boolean"
  checkFoodCollision:
    description: "检测蛇头是否与食物发生碰撞。"
    module: "game.js"
    params:
      - name: "headPosition"
        type: "object {x: number, y: number}"
        description: "蛇头的当前网格坐标"
    returns: "boolean"
  eatFood:
    description: "处理蛇吃掉食物的逻辑，包括分数增加、蛇身增长和新食物生成。"
    module: "game.js"
    params: []
    returns: "void"

# ------------------------------------------
# Module: snake.js (Snake Entity Logic)
# ------------------------------------------
snake_logic:
  Snake_constructor:
    description: "创建Snake类实例。"
    module: "snake.js"
    params:
      - name: "initialPosition"
        type: "object {x: number, y: number}"
        description: "蛇头的初始网格坐标"
      - name: "initialDirection"
        type: "string"
        description: "蛇的初始移动方向 (UP, DOWN, LEFT, RIGHT)"
      - name: "initialLength"
        type: "number"
        description: "蛇的初始长度"
    returns: "Snake instance"
  Snake_move:
    description: "根据当前方向更新蛇的位置，并处理身体节的跟随。"
    module: "snake.js"
    params: []
    returns: "object {x: number, y: number} (新的蛇头位置)"
  Snake_changeDirection:
    description: "根据玩家输入改变蛇的移动方向，避免180度反转。"
    module: "snake.js"
    params:
      - name: "newDirection"
        type: "string"
        description: "新的方向 (UP, DOWN, LEFT, RIGHT)"
    returns: "void"
  Snake_grow:
    description: "在蛇尾添加一个新的身体节。"
    module: "snake.js"
    params: []
    returns: "void"
  Snake_checkSelfCollision:
    description: "检测蛇头是否与自身发生碰撞。"
    module: "snake.js"
    params: []
    returns: "boolean"
  Snake_getHead:
    description: "获取蛇头的当前网格坐标。"
    module: "snake.js"
    params: []
    returns: "object {x: number, y: number}"
  Snake_getBody:
    description: "获取蛇身体所有节的网格坐标列表。"
    module: "snake.js"
    params: []
    returns: "array of {x: number, y: number}"
  Snake_draw:
    description: "在Canvas上绘制蛇。"
    module: "snake.js"
    params:
      - name: "ctx"
        type: "CanvasRenderingContext2D"
        description: "Canvas 2D渲染上下文"
      - name: "cellSize"
        type: "number"
        description: "每个网格单元的像素大小"
      - name: "headColor"
        type: "string"
        description: "蛇头的颜色"
      - name: "bodyColor"
        type: "string"
        description: "蛇身的颜色"
    returns: "void"

# ------------------------------------------
# Module: food.js (Food Entity Logic)
# ------------------------------------------
food_logic:
  Food_constructor:
    description: "创建Food类实例。"
    module: "food.js"
    params: []
    returns: "Food instance"
  Food_spawn:
    description:

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
创建时间: 2026-02-13T15:42:27.158341
创建人: 程序员Agent
