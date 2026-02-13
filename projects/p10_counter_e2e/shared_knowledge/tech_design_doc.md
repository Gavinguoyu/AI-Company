# p10_counter_e2e 技术设计文档

## 1. 架构设计
好的，资深游戏程序员已就位！

根据您提供的 `game_design_doc.md`、`project_rules.yaml` 和 `config/game_config.yaml`，我将为您设计技术架构，确定文件结构和模块划分，并更新 `api_registry.yaml`。

### 1. 技术架构设计

#### 1.1 文件结构
严格遵循 `project_rules.yaml` 中的文件结构规范：

```
projects/p10_counter_e2e/output/
├── index.html                  # 游戏入口文件
├── css/
│   └── style.css               # 基础样式和字体导入
├── js/
│   ├── config.js               # 游戏配置，从 game_config.yaml 转换而来
│   └── game.js                 # 游戏主逻辑，包含游戏循环、UI渲染和事件处理
└── api_registry.yaml           # API 注册表 (更新后)
```

#### 1.2 模块划分与职责
*   **`index.html`**:
    *   职责：HTML 骨架，包含 `<canvas>` 元素作为游戏渲染区域。
    *   引入 `style.css` 和 `js/config.js`、`js/game.js`。
*   **`css/style.css`**:
    *   职责：页面整体布局，居中 Canvas，设置背景色。
    *   导入自定义字体（如 `Pixelify Sans`）。
    *   控制 Canvas 的响应式显示（保持宽高比并适应屏幕）。
*   **`js/config.js`**:
    *   职责：将 `game_config.yaml` 中的所有配置项转换为 JavaScript 对象并导出。
    *   作为游戏所有可配置参数的单一数据源，避免硬编码。
*   **`js/game.js`**:
    *   职责：实现 `CounterGame` 类，封装所有游戏逻辑。
    *   **初始化 (`init`)**: 获取 Canvas 和 Context，加载 `config`，初始化游戏状态（`currentValue`），计算按钮位置，设置事件监听器（鼠标点击、移动）。
    *   **游戏循环 (`gameLoop`)**: 遵循标准模板，调用 `update` 和 `render`。
    *   **更新 (`update`)**: 处理游戏逻辑更新。在此简单计数器游戏中，主要用于状态管理和未来可能的动画。
    *   **渲染 (`render`)**: 清空 Canvas，绘制背景、当前数字、以及 “+1” 和 “-1” 按钮（包括悬停/点击反馈）。
    *   **事件处理 (`handleCanvasClick`, `handleMouseMove`, `handleMouseDown`, `handleMouseUp`)**: 监听 Canvas 上的鼠标事件，检测按钮区域点击，更新计数器数值，并触发渲染。
    *   **辅助函数**: `drawButton`、`drawCenteredText`、`getCanvasMousePos`、`isPointInRect` 等，用于封装常用的绘图和交互逻辑。

#### 1.3 游戏状态管理
*   使用一个 `gameState` 对象来统一管理所有游戏状态，例如 `{ currentValue: 0, running: true, hoveredButton: null, activeButton: null }`。
*   所有对游戏状态的修改都通过 `CounterGame` 类的方法进行，确保状态的一致性。

#### 1.4 响应式设计
*   **Canvas 尺寸**: `index.html` 中的 `<canvas>` 元素将通过 `width` 和 `height` 属性定义一个固定的内部绘制分辨率（例如 800x600）。
*   **CSS 缩放**: `style.css` 将利用 `max-width`, `max-height`, `object-fit: contain` 来确保 Canvas 在不同屏幕尺寸下能够自适应缩放，同时保持其内部绘制内容的宽高比不变。
*   **鼠标坐标转换**: `getCanvasMousePos` 函数将负责将浏览器事件的屏幕坐标转换为 Canvas 内部绘制坐标，以正确检测按钮点击。

### 2. 更新 `api_registry.yaml`

我将根据上述设计更新 `api_registry.yaml` 文件。

```yaml
# 文件: api_registry.yaml
# 职责: 记录项目中已定义和计划定义的API（函数、类、全局对象等）
# ==========================================
# 项目名称: p10_counter_e2e
# 创建时间: 2026-02-12T19:37:09.245779
# ==========================================

apis:
  # 游戏核心配置对象
  - name: config
    type: object
    description: "从 config.js 加载的游戏配置对象，包含所有游戏数值和UI设置。"
    source_file: "js/config.js"
    usage: "config.game_settings.initial_value, config.ui_settings.button_plus.label"

  # CounterGame 类
  - name: CounterGame
    type: class
    description: "负责整个计数器游戏的初始化、运行和管理。"
    source_file: "js/game.js"
    methods:
      - name: constructor
        parameters:
          - name: canvasId
            type: string
            description: "HTML canvas 元素的ID。"
        description: "初始化游戏类，获取 canvas 元素和绘图上下文，绑定事件处理函数。"
      - name: init
        parameters: []
        description: "初始化游戏状态、加载配置、计算UI元素位置、设置事件监听器。"
      - name: startGame
        parameters: []
        description: "启动游戏主循环。"
      - name: gameLoop
        parameters: []
        description: "游戏主循环函数，负责调用 update 和 render。"
      - name: update
        parameters: []
        description: "更新游戏逻辑和状态（在此游戏中主要处理状态变化和动画）。"
      - name: render
        parameters: []
        description: "根据当前游戏状态在 canvas 上绘制所有元素，包括数字和按钮。"
      - name: handleCanvasClick
        parameters:
          - name: event
            type: MouseEvent
            description: "鼠标点击事件对象。"
        description: "处理 canvas 上的点击事件，检测按钮点击并更新计数器数值。"
      - name: handleMouseMove
        parameters:
          - name: event
            type: MouseEvent
            description: "鼠标移动事件对象。"
        description: "处理 canvas 上的鼠标移动事件，更新悬停按钮状态以提供视觉反馈。"
      - name: handleMouseDown
        parameters:
          - name: event
            type: MouseEvent
            description: "鼠标按下事件对象。"
        description: "处理 canvas 上的鼠标按下事件，更新激活按钮状态。"
      - name: handleMouseUp
        parameters:
          - name: event
            type: MouseEvent
            description: "鼠标抬起事件对象。"
        description: "处理 canvas 上的鼠标抬起事件，重置激活按钮状态。"
      - name: drawButton
        parameters:
          - name: ctx
            type: CanvasRenderingContext2D
            description: "Canvas 2D 渲染上下文。"
          - name: button
            type: object
            description: "按钮配置对象 (包含 x, y, width, height, label, colors等)。"
          - name: isHovered
            type: boolean
            description: "指示按钮是否被鼠标悬停。"
          - name: isActive
            type: boolean
            description: "指示按钮是否处于激活（点击）状态。"
        description: "在 canvas 上绘制一个带圆角的按钮，根据状态应用不同颜色。"
      - name: draw

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
创建时间: 2026-02-12T19:48:44.164390
创建人: 程序员Agent
