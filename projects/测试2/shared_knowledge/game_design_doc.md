# 测试2 游戏策划文档

## 1. 游戏概述
制作一个Flappy Bird风格的游戏。玩家点击屏幕让小鸟飞起来，需要在管道之间穿梭。

## 2. 核心玩法
好的，PM。我已收到新的游戏需求：`制作一个Flappy Bird风格的游戏。玩家点击屏幕让小鸟飞起来，需要在管道之间穿梭。`

这是一个经典且广受欢迎的游戏类型，其核心机制简单但富有挑战性。我将根据您的需求和项目规范，为您编写详细的游戏策划文档 (GDD) 和相应的配置表。

---

## 游戏策划文档 (GDD)

### 文件: gdd_flappy_bird_v1.0.md

#### 1. 项目概述

*   **游戏名称:** P10 Flappy Bird (p10_flappy_bird)
*   **版本号:** 1.0
*   **撰写日期:** 2026-02-12
*   **设计者:** 资深游戏策划
*   **游戏类型:** 休闲、街机、无限跑酷
*   **核心玩法:** 玩家控制一只小鸟，通过点击屏幕使其向上飞行，躲避不断出现的管道障碍物，努力获得高分。
*   **游戏目标:** 获得最高分数，挑战个人极限。

#### 2. 核心玩法循环

1.  **开始界面:** 游戏启动，显示标题、“点击开始”提示、和可能的高分记录。小鸟可能在原地扑腾动画。
2.  **游戏进行中:**
    *   玩家点击屏幕，小鸟向上飞行一小段距离（“扑腾”）。
    *   小鸟受重力影响持续下落。
    *   屏幕从右向左不断生成并移动管道障碍物。
    *   玩家需控制小鸟穿过管道的缝隙。
    *   成功穿过一对管道，得分增加。
    *   小鸟碰到管道、地面或屏幕顶部/底部，游戏结束。
3.  **游戏结束:**
    *   显示玩家当前分数和历史最高分。
    *   提供“重新开始”按钮。
    *   小鸟可能以坠落动画结束。

#### 3. 游戏机制

##### 3.1. 玩家控制 (Player Control)

*   **点击/触摸:** 玩家每次在游戏区域内进行点击或触摸，小鸟会获得一个向上的瞬时速度（“扑腾”）。
*   **重力:** 小鸟在没有点击时，会持续受到重力作用向下加速下落。
*   **飞行角度:** 小鸟的朝向会根据其垂直速度进行微调，例如：上升时头部略微向上倾斜，下落时头部略微向下倾斜，增加视觉反馈。

##### 3.2. 障碍物生成与移动 (Obstacle Generation & Movement)

*   **障碍物类型:** 仅有上下两根管道组成的“门”。
*   **生成:** 管道从屏幕右侧生成，以恒定速度向左移动。
*   **间隔:** 管道以固定的时间间隔或屏幕距离间隔生成。
*   **高度随机性:** 每对管道之间的垂直缝隙高度固定，但其整体垂直位置（即缝隙相对于屏幕的高度）是随机的，但有最小和最大限制，确保可玩性。
*   **销毁:** 管道移出屏幕左侧后销毁，可考虑使用对象池优化性能。

##### 3.3. 碰撞检测 (Collision Detection)

*   **小鸟与管道:** 小鸟的碰撞体与任何管道的碰撞体发生接触，游戏结束。
*   **小鸟与地面:** 小鸟的碰撞体与屏幕底部（地面）发生接触，游戏结束。
*   **小鸟与屏幕边界:** 小鸟飞出屏幕顶部或底部（除了地面），游戏结束。

##### 3.4. 得分机制 (Scoring Mechanism)

*   **计分条件:** 小鸟成功穿过一对管道（即小鸟的X坐标完全越过管道的X坐标区域），得分增加1分。
*   **得分显示:** 实时显示在屏幕顶部中央。
*   **最高分:** 记录并显示玩家的历史最高分。

##### 3.5. 游戏状态 (Game States)

*   **`START_SCREEN`:** 显示游戏标题、操作提示、高分记录。等待玩家首次点击。
*   **`PLAYING`:** 游戏进行中，小鸟飞行，管道移动，碰撞和得分检测。
*   **`GAME_OVER`:** 游戏结束，显示分数、最高分、以及“重新开始”按钮。

#### 4. 用户界面 (UI)

##### 4.1. 开始界面

*   **游戏标题:** 屏幕顶部中央，大字体。
*   **“点击开始”提示:** 屏幕中央，提示玩家进行操作。
*   **小鸟动画:** 屏幕中央，小鸟进行原地扑腾动画。
*   **最高分显示:** 屏幕底部或顶部，显示历史最高分。

##### 4.2. 游戏进行中界面

*   **当前分数:** 屏幕顶部中央，实时更新，大字体。

##### 4.3. 游戏结束界面

*   **“游戏结束”文本:** 屏幕中央上方。
*   **当前分数:** 屏幕中央，显示本次游戏得分。
*   **最高分:** 屏幕中央下方，显示历史最高分。
*   **“重新开始”按钮:** 屏幕底部中央，可点击。

##### 4.4. 视觉风格

*   **整体风格:** 严格遵循 `project_rules.yaml` 中定义的“像素风”。
*   **背景:** 循环滚动的背景（天空、云朵），体现无限跑酷感。
*   **地面:** 循环滚动的地面，与背景形成视差效果。
*   **角色:** 小鸟应有飞行（扑腾）动画帧。
*   **字体:** 像素风格字体，确保数字和文本清晰易读。

#### 5. 美术资源需求

根据像素风格，我们需要以下美术资源：

*   **角色 (Bird):**
    *   `bird_frame_01.png`
    *   `bird_frame_02.png`
    *   `bird_frame_03.png` (用于飞行动画)
    *   `bird_dead.png` (可选，用于死亡坠落)
*   **障碍物 (Pipes):**
    *   `pipe_top.png` (上半部分管道)
    *   `pipe_bottom.png` (下半部分管道)
*   **背景 (Background):**
    *   `background_sky.png` (主背景图，可循环)
    *   `ground.png` (地面图，可循环，与背景有视差)
*   **UI 元素:**
    *   `button_restart_default.png`
    *   `button_restart_pressed.png`
    *   `title_logo.png` (游戏标题)
*   **字体:**
    *   `pixel_font.ttf` 或 `pixel_font.woff`: 用于显示分数和UI文本。

#### 6. 音效需求

*   `sfx_flap.wav`: 小鸟每次点击扑腾时的音效。
*   `sfx_score.wav`: 每次成功穿过管道时的音效。
*   `sfx_hit_pipe.wav`: 小鸟撞到管道时的音效。
*   `sfx_hit_ground.wav`: 小鸟撞到地面时的音效。
*   `sfx_game_over.wav`: 游戏结束时的提示音效。

#### 7. 技术实现考量

*   **物理引擎:** 简单的2D物理，实现重力、速度、位置更新。
*   **碰撞检测:** 矩形碰撞体 (AABB) 或圆形碰撞体，用于检测小鸟与管道/地面/边界的碰撞。
*   **对象池 (Object Pooling):** 用于管道的生成和销毁，减少GC开销，优化性能。
*   **视差滚动 (Parallax Scrolling):** 实现背景和地面的层次感，增加视觉深度。
*   **状态机 (State Machine):** 管理 `START_SCREEN`, `PLAYING`, `GAME_OVER` 之间的切换。
*   **本地存储:** 用于保存最高分。

#### 8. 难度平衡与数值调整建议

*   **重力 (`gravity`):** 影响小鸟下落速度，值越大越难。
*   **扑腾力量 (`flap_force`):** 影响小鸟每次点击上升的高度，值越大越容易。
*   **管道移动速度 (`pipe_speed`):** 影响游戏节奏，值越大越难。
*   **管道生成间隔 (`pipe_interval`):** 影响管道密度，间隔越短越难。
*   **管道缝隙高度 (`pipe_gap_height`):** 影响通过难度，值越小越难。
*   **管道垂直随机范围 (`pipe_min_y`, `pipe_max_y`):** 影响管道位置的不可预测性，范围越大越难。

通过调整这些数值，可以在测试阶段快速迭代，找到最佳的游戏难度曲线。

#### 9. 未来扩展方向

*   **多种小鸟皮肤:** 玩家可以解锁或购买不同外观的小鸟。
*   **成就系统:** 达成特定分数或完成特定操作解锁成就。
*   **每日挑战/任务:** 增加玩家的留存动力。
*   **排行榜:** 与朋友或全球玩家竞争高分。
*   **道具/能力:** 短暂无敌、加速等，增加游戏变数。

---

## 游戏配置表 (YAML)

以下是根据上述GDD和项目规范生成的YAML配置文件。这些文件将提供给程序员，用于初始化游戏参数和UI元素。

### 文件: game_config.yaml

```yaml
# 文件: game_config.yaml
# 职责: 定义游戏的核心数值配置和物理参数
# ==========================================

game_parameters:
  initial_score: 0           # 游戏开始时的初始分数
  score_increment: 1         # 每次成功穿过管道增加的分数
  
physics:
  gravity: 1000              # 小鸟受到的重力加速度 (像素/秒^2)。值越大，下落越快。
  flap_force: -350           # 小鸟每次点击获得的垂直速度 (像素/秒)。负值表示向上。
  terminal_velocity_y: 800   # 小鸟最大下落速度，防止速度过快 (像素/秒)

player:
  initial_position_x_ratio: 0.2 # 小鸟初始X坐标相对于屏幕宽度的比例 (0.0 - 1.0)
  initial_position_y_ratio: 0.5 # 小鸟初始Y坐标相对于屏幕高度的比例 (0.0 - 1.0)
  rotation_speed: 360        # 小鸟旋转速度 (度/秒)，用于根据速度调整角度

obstacles:
  pipe_speed: 180            # 管道从右向左移动的速度 (像素/秒)。值越大，游戏越快。
  pipe_generation_interval: 1.8 # 生成一对新管道的时间间隔 (秒)。值越小，管道越密集。
  pipe_width: 52             # 单根管道的宽度 (像素)
  pipe_gap_height: 120       # 上下管道之间的垂直缝隙高度 (像素)。值越小，通过越难。
  pipe_min_y_offset: -150    # 管道缝隙中心相对于屏幕中心Y轴的最小偏移 (像素)
  pipe_max_y_offset: 150     # 管道缝隙中心相对于屏幕中心Y轴的最大偏移 (像素)
  ground_height: 100         # 地面高度 (像素)，小鸟碰到即游戏结束

# 游戏状态转换时的动画或过渡时间 (秒)
game_state_transitions:
  game_over_delay: 0.5       # 碰撞后到显示游戏结束界面的延迟
```

### 文件: ui_config.yaml

```yaml
# 文件: ui_config.yaml
# 职责: 定义用户界面 (UI) 的布局和样式配置
# ==========================================

ui_elements:
  # --- 通用字体配置 ---
  default_font: pixel_font
  default_text_color: "#FFFFFF"

  # --- 开始界面 (START_SCREEN) ---
  title_logo:
    type: image
    asset_key: title_logo
    position:
      anchor: top_center
      offset_x: 0
      offset_y: 50
    size:
      width: 200
      height: 80

  tap_to_start_text:
    type: text
    text: "TAP TO START"
    font: default_font
    font_size: 32
    color: default_text_color
    position:
      anchor: center
      offset_x: 0
      offset_y: 50
    text_align: center
  
  start_screen_bird:
    type: sprite_animation
    asset_keys: [bird_frame_01, bird_frame_02, bird_frame_03]
    frame_duration: 0.15 # 每帧持续时间
    position:
      anchor: center
      offset_x: 0
      offset_y: -50
    size:
      width: 34 # 小鸟图片实际宽度
      height: 24 # 小鸟图片实际高度
    
  high_score_display_start:
    type: text
    text_prefix: "BEST: "
    font: default_font
    font_size: 24
    color: default_text_color
    position:
      anchor: bottom_center
      offset_x: 0
      offset_y: -20
    text_align: center

  # --- 游戏进行中界面 (PLAYING) ---
  current_score_display:
    type: text
    text: "0" # 初始显示
    font: default_font
    font_size: 48
    color: default_text_color
    position:
      anchor: top_center
      offset_x: 0
      offset_y: 20
    text_align: center

  # --- 游戏结束界面 (GAME_OVER) ---
  game_over_text:
    type: text
    text: "GAME OVER"
    font: default_font
    font_size: 48
    color: "#FF0000" # 红色
    position:
      anchor: center
      offset_x: 0
      offset_y: -100
    text_align: center

  final_score_display:
    type: text
    text_prefix: "SCORE: "
    font: default_font
    font_size: 36
    color: default_text_color
    position:
      anchor: center
      offset_x: 0
      offset_y: -30
    text_align: center

  high_score_display_game_over:
    type: text
    text_prefix: "BEST: "
    font: default_font
    font_size: 28
    color: default_text_color
    position:
      anchor: center
      offset_x: 0
      offset_y: 20
    text_align: center

  restart_button:
    type: button
    asset_default: button_restart_default
    asset_pressed: button_restart_pressed
    position:
      anchor: bottom_center
      offset_x: 0
      offset_y: -50
    size:
      width: 150
      height: 60
    text: "RESTART"
    text_font: default_font
    text_font_size: 28
    text_color: "#000000" # 按钮文本颜色
```

### 文件: assets_config.yaml

```yaml
# 文件: assets_config.yaml
# 职责: 定义游戏所需的所有资源路径和类型
# ==========================================

assets:
  images:
    # --- 角色 (Bird) ---
    bird_frame_01:
      path: assets/images/player/bird_frame_01.png
      description: "小鸟飞行动画帧 1"
    bird_frame_02:
      path: assets/images/player/bird_frame_02.png
      description: "小鸟飞行动画帧 2"
    bird_frame_03:
      path: assets/images/player/bird_frame_03.png
      description: "小鸟飞行动画帧 3"
    bird_dead: # 可选
      path: assets/images/player/bird_dead.png
      description: "小鸟死亡坠落状态图片"

    # --- 障碍物 (Pipes) ---
    pipe_top:
      path: assets/images/obstacles/pipe_top.png
      description: "上半部分管道图片"
    pipe_bottom:
      path: assets/images/obstacles/pipe_bottom.png
      description: "下半部分管道图片"

    # --- 背景 (Background) ---
    background_sky:
      path: assets/images/background/background_sky.png
      description: "主背景天空图片，可循环滚动"
    ground:
      path: assets/images/background/ground.png
      description: "地面图片，可循环滚动并与背景有视差"

    # --- UI 元素 ---
    button_restart_default:
      path: assets/images/ui/button_restart_default.png
      description: "重新开始按钮的默认状态图片"
    button_restart_pressed:
      path: assets/images/ui/button_restart_pressed.png
      description: "重新开始按钮的按下状态图片"
    title_logo:
      path: assets/images/ui/title_logo.png
      description: "游戏标题Logo图片"
  
  fonts:
    pixel_font:
      path: assets/fonts/pixel_font.ttf
      description: "游戏UI和数字显示使用的像素风格字体"

  audio:
    sfx_flap:
      path: assets/audio/sfx/sfx_flap.wav
      description: "小鸟扑腾音效"
    sfx_score:
      path: assets/audio/sfx/sfx_score.wav
      description: "成功穿过管道得分音效"
    sfx_hit_pipe:
      path: assets/audio/sfx/sfx_hit_pipe.wav
      description: "小鸟撞到管道音效"
    sfx_hit_ground:
      path: assets/audio/sfx/sfx_hit_ground.wav
      description: "小鸟撞到地面音效"
    sfx_game_over:
      path: assets/audio/sfx/sfx_game_over.wav
      description: "游戏结束提示音效"
```

---

请程序员和美术团队查阅以上文档和配置。我已经尝试将所有可配置的数值和资源路径都提取到YAML文件中，方便后续调整。

关于GDD中的“难度平衡与数值调整建议”部分，程序员可以在开发过程中根据实际体验，调整 `game_config.yaml` 中的 `physics`, `player`, `obstacles` 等参数，以达到最佳的游戏手感和难度。

如有任何疑问，或需要更详细的说明，请随时提出，我会耐心解答。

## 3. 技术要求
- 技术栈: HTML5 + Canvas + JavaScript
- 平台: 浏览器
- 风格: 像素风

## 4. 配置说明
详见 config_tables.yaml

---
文档版本: 1.0
创建时间: 2026-02-12T19:02:13.558344
创建人: 策划Agent
