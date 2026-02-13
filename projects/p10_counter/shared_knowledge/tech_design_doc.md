# p10_counter 技术设计文档

## 1. 架构设计
我已经根据您的要求，结合 `game_design_doc.md` 和 `project_rules.yaml`，设计了游戏的技术架构、文件结构和模块划分。

现在，我将更新 `api_registry.yaml` 文件，注册所有模块、类和关键函数，以供后续开发参考和避免重复。

---
正在写入 `api_registry.yaml`...
```yaml
# 文件: api_registry.yaml
# 职责: 注册游戏中所有模块、类和关键函数，避免重复开发，并提供API概览
# ==========================================

modules:
  - name: Config
    path: js/config.js
    description: 负责加载和管理所有游戏配置（game_config, ui_config, assets_config）。
    classes:
      - name: Config
        methods:
          - name: loadConfigs
            description: 异步加载所有YAML配置文件。
            params: []
            returns: "Promise<void>"
          - name: getGameConfig
            description: 获取游戏核心参数配置。
            params: []
            returns: "Object"
          - name: getUiConfig
            description: 获取UI元素配置。
            params: []
            returns: "Object"
          - name: getAssetsConfig
            description: 获取资源路径配置。
            params: []
            returns: "Object"

  - name: AssetManager
    path: js/asset_manager.js
    description: 负责加载并管理所有图片、音频和字体资源。
    classes:
      - name: AssetManager
        methods:
          - name: loadAssets
            description: 根据assets_config.yaml加载所有资源。
            params: []
            returns: "Promise<void>"
          - name: getImage
            description: 根据key获取已加载的图片。
            params:
              - name: key
                type: String
                description: 资源key
            returns: "Image | undefined"
          - name: getAudio
            description: 根据key获取已加载的音频。
            params:
              - name: key
                type: String
                description: 资源key
            returns: "Audio | undefined"
          - name: getFont
            description: 根据key获取已加载的字体路径。
            params:
              - name: key
                type: String
                description: 资源key
            returns: "String | undefined"

  - name: SoundManager
    path: js/sound_manager.js
    description: 负责播放游戏音效。
    classes:
      - name: SoundManager
        methods:
          - name: play
            description: 播放指定key的音效。
            params:
              - name: key
                type: String
                description: 音效资源key
            returns: "void"
          - name: mute
            description: 静音所有音效。
            params: []
            returns: "void"
          - name: unmute
            description: 取消静音。
            params: []
            returns: "void"

  - name: GameState
    path: js/game_state.js
    description: 定义游戏状态枚举和简单的状态管理。
    constants:
      - name: GameState
        type: Enum
        values: [START_SCREEN, PLAYING, GAME_OVER]
    functions:
      - name: setGameState
        description: 设置当前游戏状态。
        params:
          - name: newState
            type: GameState
            description: 新的游戏状态
        returns: "void"
      - name: getGameState
        description: 获取当前游戏状态。
        params: []
        returns: "GameState"

  - name: Bird
    path: js/entities/bird.js
    description: 玩家小鸟实体，处理其物理、动画和输入响应。
    classes:
      - name: Bird
        methods:
          - name: constructor
            description: 初始化小鸟。
            params:
              - name: config
                type: Object
                description: 小鸟相关配置
              - name: assetManager
                type: AssetManager
                description: 资源管理器实例
            returns: "Bird"
          - name: flap
            description: 小鸟向上扑腾。
            params: []
            returns: "void"
          - name: update
            description: 更新小鸟物理状态和动画。
            params:
              - name: deltaTime
                type: Number
                description: 帧时间差
              - name: gameConfig
                type: Object
                description: 游戏配置
            returns: "void"
          - name: render
            description: 绘制小鸟。
            params:
              - name: ctx
                type: CanvasRenderingContext2D
                description: Canvas 2D渲染上下文
            returns: "void"
          - name: reset
            description: 重置小鸟位置和状态。
            params: []
            returns: "void"
          - name: getBounds
            description: 获取小鸟的碰撞边界。
            params: []
            returns: "Object { x, y, width, height }"

  - name: Pipe
    path: js/entities/pipe.js
    description: 单个管道实体（上或下）。
    classes:
      - name: Pipe
        methods:
          - name: constructor
            description: 初始化管道。
            params:
              - name: type
                type: String
                description: 管道类型 ('top' 或 'bottom')
              - name: config
                type: Object
                description: 管道相关配置
              - name: assetManager
                type: AssetManager
                description: 资源管理器实例
            returns: "Pipe"
          - name: update
            description: 更新管道位置。
            params:
              - name: deltaTime
                type: Number
                description: 帧时间差
            returns: "void"
          - name: render
            description: 绘制管道。
            params:
              - name: ctx
                type: CanvasRenderingContext2D
                description: Canvas 2D渲染上下文
            returns: "void"
          - name: reset
            description: 重置管道到初始状态，用于对象池。
            params:
              - name: x
                type: Number
                description: 新的X坐标
              - name: y
                type: Number
                description: 新的Y坐标
              - name: height
                type: Number
                description: 管道图片绘制高度
            returns: "void"
          - name: getBounds
            description: 获取管道的碰撞边界。
            params: []
            returns: "Object { x, y, width, height }"
          - name: isOffscreen
            description: 检查管道是否移出屏幕。
            params:
              - name: screenWidth
                type: Number
                description: 屏幕宽度
            returns: "Boolean"
          - name: getX
            description: 获取管道的X坐标。
            params: []
            returns: "Number"

  - name: PipeManager
    path: js/entities/pipe_manager.js
    description: 管理管道的生成、移动、销毁和得分。
    classes:
      - name: PipeManager
        methods:
          - name: constructor
            description: 初始化管道管理器。
            params:
              - name: config
                type: Object
                description: 管道相关配置
              - name: assetManager
                type: AssetManager
                description: 资源管理器实例
              - name: soundManager
                type: SoundManager
                description: 音效管理器实例
            returns: "PipeManager"
          - name: update
            description: 更新所有管道，生成新管道，检查得分。
            params:
              - name: deltaTime
                type: Number
                description: 帧时间差
              - name: canvasWidth
                type: Number
                description: Canvas宽度
              - name: canvasHeight
                type: Number
                description: Canvas高度
              - name: birdX
                type: Number
                description: 小鸟的X坐标
            returns: "void"
          - name: render
            description: 绘制所有管道。
            params:
              - name: ctx
                type: CanvasRenderingContext2D
                description: Canvas 2D渲染上下文
            returns: "void"
          - name: getActivePipes
            description: 获取当前所有活动的管道（用于碰撞检测）。
            params: []
            returns: "Array<Pipe>"
          - name: reset
            description: 重置所有管道。
            params: []
            returns: "void"
          - name: getScore
            description: 获取当前分数。
            params: []
            returns: "Number"

  - name: Background
    path: js/entities/background.js
    description: 循环滚动的背景。
    classes:
      - name: Background
        methods:
          - name: constructor
            description: 初始化背景。
            params:
              - name: assetManager
                type: AssetManager
                description: 资源管理器实例
              - name: assetKey
                type: String
                description: 背景图片资源key
              - name: scrollSpeedRatio
                type: Number
                description: 相对于管道速度的滚动比例
            returns: "Background"
          - name: update
            description: 更新背景滚动位置。
            params:
              - name: deltaTime
                type: Number
                description: 帧时间差
              - name: pipeSpeed
                type: Number
                description: 管道速度，用于计算背景滚动速度
            returns: "void"
          - name: render
            description: 绘制背景。
            params:
              - name: ctx
                type: CanvasRenderingContext2D
                description: Canvas 2D渲染上下文
              - name: canvasWidth
                type: Number
                description: Canvas宽度
              - name: canvasHeight
                type: Number
                description: Canvas高度
            returns: "void"
          - name: reset
            description

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
创建时间: 2026-02-12T19:03:06.511617
创建人: 程序员Agent
