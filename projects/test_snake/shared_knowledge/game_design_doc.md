# test_snake 游戏策划文档

## 1. 游戏概述
make a simple snake game

## 2. 核心玩法
好的，PM。我已收到项目启动通知，项目名称为 `test_snake`。需求是 `make a simple snake game`。

根据您的需求和项目规范，我将为您编写游戏策划文档（GDD）和必要的配置表。

---

## 游戏策划文档 (GDD)

### 文件: `test_snake_gdd.md`

#### 1. 游戏概述

*   **游戏名称:** Test Snake
*   **版本:** 1.0 (初始草案)
*   **日期:** 2026-02-13
*   **设计师:** [您的姓名/职位] (资深游戏策划)
*   **游戏类型:** 经典街机 / 休闲益智
*   **游戏目标:** 玩家控制一条蛇在网格区域内移动，吃掉随机出现的食物，使蛇身变长，并尽可能获得高分。避免撞墙或撞到自己的身体。

#### 2. 核心玩法

##### 2.1 玩家目标

*   控制蛇吃掉食物，使蛇身增长。
*   获得尽可能高的分数。
*   避免游戏失败（撞墙或撞到自己）。

##### 2.2 基本操作

*   **移动:** 使用键盘方向键（↑ ↓ ← →）或 `W A S D` 控制蛇的移动方向。
    *   蛇只能进行90度转向，不能180度反向移动（例如，向右移动时不能直接按左）。
*   **暂停:** `P` 键 (可选，但推荐)。
*   **重新开始:** 游戏结束后，点击或按 `R` 键。

##### 2.3 游戏机制

*   **网格地图:** 游戏区域由一个固定大小的网格组成。蛇和食物都占据网格中的一个单元格。
*   **蛇的移动:** 蛇会持续向当前方向移动，每隔一定时间移动一个单元格。
*   **食物生成:**
    *   游戏开始时，在随机一个空闲单元格生成一个食物。
    *   当蛇吃掉一个食物后，该食物消失，并在另一个随机的空闲单元格重新生成一个食物。
*   **蛇身增长:** 每吃掉一个食物，蛇身会增长一个节。新增长的节会出现在蛇尾。
*   **分数:** 每吃掉一个食物，玩家获得固定分数。
*   **游戏失败:**
    *   **撞墙:** 蛇头撞到游戏区域的边界。
    *   **撞自己:** 蛇头撞到自己的身体（除了刚吃掉食物瞬间的尾巴）。
*   **速度提升 (可选，根据平衡性调整):** 随着蛇身长度的增加，游戏难度可以逐渐提升，例如蛇的移动速度加快。为了“simple snake game”的初期需求，我们可以先保持速度不变，后续再考虑加入。
    *   *当前设计:* 初始版本保持速度不变，以简化。

#### 3. 游戏界面 (UI/UX)

##### 3.1 启动界面 (或游戏开始前)

*   **标题:** "Test Snake"
*   **开始按钮:** "开始游戏"
*   **高分显示:** (可选) 显示历史最高分数。

##### 3.2 游戏进行中界面

*   **游戏区域:** 占据大部分屏幕，显示蛇、食物、网格。
*   **当前分数:** 实时显示在屏幕上方或侧边。
*   **高分显示:** (可选) 显示历史最高分数。

##### 3.3 游戏结束界面

*   **提示信息:** "游戏结束!"
*   **本次得分:** 显示玩家本次游戏的最终分数。
*   **高分显示:** 显示历史最高分数。如果本次分数超过高分，则提示“新纪录！”。
*   **操作按钮:** "重新开始" / "返回主菜单" (或直接按键重新开始)。

#### 4. 游戏元素

##### 4.1 蛇 (Snake)

*   **组成:** 蛇头 (Head) 和蛇身 (Body Segments)。
*   **表现:** 像素方块，蛇头和蛇身颜色可区分。
*   **行为:** 持续移动，根据玩家输入改变方向，吃食物后增长。

##### 4.2 食物 (Food)

*   **类型:** 单一类型，如苹果或能量块。
*   **表现:** 像素方块，与蛇和背景颜色区分开。
*   **行为:** 随机生成在空闲单元格，被吃后消失并重新生成。

##### 4.3 游戏区域 (Game Board)

*   **类型:** 固定大小的矩形网格。
*   **表现:** 边框清晰，内部可有简单的网格线（可选）。
*   **行为:** 定义了蛇的活动范围和食物的生成范围。

#### 5. 数值设计 (详细配置见 `game_config.yaml`)

*   **地图尺寸:** 宽度和高度（单元格数量）。
*   **单元格大小:** 每个单元格在屏幕上的像素大小。
*   **初始蛇长:** 游戏开始时蛇的初始身体节数。
*   **初始速度:** 蛇每秒移动的单元格数或更新间隔时间。
*   **食物得分:** 每吃一个食物增加的分数。
*   **速度提升机制:** (暂时不启用，但预留配置)

#### 6. 关卡设计

*   **地图:** 只有一个固定大小的地图，无特殊障碍物。
*   **初始状态:**
    *   蛇的初始位置在地图中央偏左侧。
    *   蛇的初始方向向右。
    *   食物初始生成在随机的空闲位置。

#### 7. 技术实现考量

*   **技术栈:** HTML5 + Canvas + JavaScript (根据 `project_rules.yaml`)。
*   **渲染:** 使用 Canvas 绘制所有游戏元素，每帧清空并重绘。
*   **碰撞检测:** 基于网格坐标进行精确的碰撞检测。
*   **数据管理:** 所有配置数据从 `game_config.yaml` 读取，禁止硬编码。

#### 8. 美术风格

*   **整体风格:** 像素风 (根据 `project_rules.yaml`)。
*   **元素设计:** 蛇头、蛇身、食物、背景网格等都应采用简洁的像素风格。
*   **颜色:** 选用对比鲜明的颜色，确保游戏元素清晰可见。

#### 9. 音效设计 (可选，但推荐为提升体验)

*   **吃食物音效:** 短促、清脆的音效。
*   **游戏失败音效:** 稍长、低沉的音效。
*   **背景音乐:** 简单、循环的休闲风格音乐 (可选)。

---

## 配置文件

根据GDD和`project_rules.yaml`，我将输出以下YAML配置文件。

### 文件: `game_config.yaml`

```yaml
# 文件: game_config.yaml
# 职责: 包含游戏的所有可配置数值和设置
# ==========================================
# 项目名称: test_snake
# 创建时间: 2026-02-13T15:40:40.860580 (此处沿用项目规范中的创建时间，实际应为当前时间)
# ==========================================

game_settings:
  # 游戏地图配置
  GRID_WIDTH: 20             # 游戏区域的网格宽度 (单元格数量)
  GRID_HEIGHT: 20            # 游戏区域的网格高度 (单元格数量)
  CELL_SIZE: 20              # 每个单元格的像素大小 (例如: 20x20像素)
  
  # 游戏循环和速度配置
  INITIAL_GAME_SPEED_MS: 150 # 游戏更新间隔时间，单位毫秒 (值越小蛇越快)
  # SPEED_INCREASE_INTERVAL: 5 # 每吃掉多少个食物后速度提升 (当前版本不启用，设置为0或注释)
  # SPEED_INCREASE_AMOUNT_MS: 5 # 每次速度提升减少的毫秒数 (当前版本不启用)

  # 游戏分数配置
  SCORE_PER_FOOD: 10         # 每吃一个食物获得的分数

  # 游戏结束条件
  GAME_OVER_CONDITIONS:
    - WALL_COLLISION         # 撞墙导致游戏结束
    - SELF_COLLISION         # 撞到自己身体导致游戏结束

snake_settings:
  INITIAL_SNAKE_LENGTH: 3    # 游戏开始时蛇的初始长度 (包括头部)
  INITIAL_POSITION_X: 5      # 蛇头初始X坐标 (基于网格，左上角为0,0)
  INITIAL_POSITION_Y: 10     # 蛇头初始Y坐标
  INITIAL_DIRECTION: "RIGHT" # 蛇的初始移动方向 (UP, DOWN, LEFT, RIGHT)
  
  # 蛇的颜色配置 (HTML颜色字符串或RGB值)
  HEAD_COLOR: "#4CAF50"      # 蛇头颜色 (绿色)
  BODY_COLOR: "#8BC34A"      # 蛇身颜色 (浅绿色)

food_settings:
  # 食物的颜色配置
  FOOD_COLOR: "#F44336"      # 食物颜色 (红色)
  
ui_text:
  GAME_TITLE: "Test Snake"
  START_BUTTON_TEXT: "开始游戏"
  RESTART_BUTTON_TEXT: "重新开始"
  GAME_OVER_MESSAGE: "游戏结束!"
  NEW_HIGHSCORE_MESSAGE: "新纪录!"
  SCORE_LABEL: "分数:"
  HIGHSCORE_LABEL: "最高分:"
```

### 文件: `api_registry.yaml`

```yaml
# 文件: api_registry.yaml
# 职责: 注册和描述项目中的主要API/函数，避免重复开发
# ==========================================
# 项目名称: test_snake
# 创建时间: 2026-02-13T15:40:40.860580
# ==========================================

game_core:
  initGame:
    description: "初始化游戏环境，包括Canvas、上下文、事件监听和初始游戏状态。"
    params: []
    returns: "void"
  startGame:
    description: "重置游戏状态，启动主游戏循环。"
    params: []
    returns: "void"
  endGame:
    description: "处理游戏结束逻辑，停止游戏循环，显示分数和重新开始选项。"
    params:
      - name: "isNewHighscore"
        type: "boolean"
        description: "是否创造了新的最高分"
    returns: "void"
  updateGame:
    description: "主游戏循环的更新函数，负责蛇的移动、碰撞检测、食物生成等逻辑。"
    params: []
    returns: "void"
  drawGame:
    description: "主游戏循环的绘制函数，负责清空Canvas并绘制所有游戏元素。"
    params: []
    returns: "void"

snake_logic:
  moveSnake:
    description: "根据当前方向更新蛇的位置，并处理身体节的跟随。"
    params: []
    returns: "void"
  changeDirection:
    description: "根据玩家输入改变蛇的移动方向，避免180度反转。"
    params:
      - name: "newDirection"
        type: "string"
        description: "新的方向 (UP, DOWN, LEFT, RIGHT)"
    returns: "void"
  checkCollision:
    description: "检测蛇头是否与墙壁或自身发生碰撞。"
    params: []
    returns: "boolean"
  growSnake:
    description: "在蛇尾添加一个新的身体节。"
    params: []
    returns: "void"
  getSnakeHeadPosition:
    description: "获取蛇头的当前网格坐标。"
    params: []
    returns: "object {x: number, y: number}"
  getSnakeBodyPositions:
    description: "获取蛇身体所有节的网格坐标列表。"
    params: []
    returns: "array of {x: number, y: number}"

food_logic:
  spawnFood:
    description: "在地图上的随机空闲位置生成食物。"
    params: []
    returns: "object {x: number, y: number} (食物的新位置)"
  eatFood:
    description: "处理蛇吃掉食物的逻辑，包括分数增加、蛇身增长和新食物生成。"
    params: []
    returns: "void"
  getFoodPosition:
    description: "获取食物的当前网格坐标。"
    params: []
    returns: "object {x: number, y: number}"

input_handler:
  handleKeyPress:
    description: "监听键盘事件，处理蛇的移动方向和游戏暂停/重新开始等操作。"
    params:
      - name: "event"
        type: "KeyboardEvent"
        description: "键盘事件对象"
    returns: "void"

ui_manager:
  updateScoreDisplay:
    description: "更新UI上显示的分数。"
    params:
      - name: "score"
        type: "number"
        description: "当前分数"
    returns: "void"
  updateHighscoreDisplay:
    description: "更新UI上显示的最高分数。"
    params:
      - name: "highscore"
        type: "number"
        description: "当前最高分数"
    returns: "void"
  displayGameOverScreen:
    description: "在游戏结束时显示游戏结束界面，包括分数和重新开始按钮。"
    params:
      - name: "score"
        type: "number"
        description: "本次游戏得分"
      - name: "isNewHighscore"
        type: "boolean"
        description: "是否创造了新的最高分"
    returns: "void"
  hideGameOverScreen:
    description: "隐藏游戏结束界面。"
    params: []
    returns: "void"
```

---

请程序员和美术团队查阅这些文档和配置。如有任何疑问或需要进一步的澄清，请随时提出。我将耐心解答。

## 3. 技术要求
- 技术栈: HTML5 + Canvas + JavaScript
- 平台: 浏览器
- 风格: 像素风

## 4. 配置说明
详见 config_tables.yaml

---
文档版本: 1.0
创建时间: 2026-02-13T15:41:40.050162
创建人: 策划Agent
