# p10_counter 游戏策划文档

## 1. 游戏概述
A simple click counter game. Click a button and the number increases by 1. Display the count in the center of the screen.

## 2. 核心玩法
好的，PM。我已收到项目启动通知和初步需求，并仔细阅读了 `project_rules.yaml` 文件，了解了项目的规范和目标。

根据您提出的需求 `A simple click counter game. Click a button and the number increases by 1. Display the count in the center of the screen.`，我将为您编写游戏策划文档 (GDD) 和相应的配置表。

---

## 游戏策划文档 (GDD)

### 文件: gdd_p10_counter_v1.0.md

#### 1. 项目概述

*   **游戏名称:** P10 Click Counter (p10_counter)
*   **版本号:** 1.0
*   **撰写日期:** 2026-02-12
*   **设计者:** 资深游戏策划
*   **游戏类型:** 休闲点击类游戏
*   **核心玩法:** 玩家通过点击屏幕上的按钮，使计数器数字增加。
*   **游戏目标:** 持续点击，挑战个人最高计数。

#### 2. 核心玩法循环

1.  **开始游戏:** 游戏启动，显示初始计数（通常为0）和一个可点击的按钮。
2.  **玩家输入:** 玩家点击屏幕上的按钮。
3.  **系统反馈:**
    *   计数器上的数字立即增加1。
    *   （可选，未来可考虑）播放点击音效。
4.  **显示更新:** 屏幕中心实时显示更新后的计数。
5.  **循环:** 玩家可以无限次重复点击。

#### 3. 游戏机制

##### 3.1. 点击机制 (Clicking Mechanism)

*   **触发条件:** 玩家在游戏区域内（具体为按钮区域）进行鼠标左键点击或触屏点击。
*   **效果:** 每次有效点击，游戏内的计数变量 `current_count` 增加 `increment_amount` (默认为1)。
*   **冷却时间:** 无冷却时间，玩家可以以最快速度连续点击。

##### 3.2. 计数机制 (Counting Mechanism)

*   **初始值:** 游戏开始时，计数器显示 `initial_count` (默认为0)。
*   **增量:** 每次点击，计数器增加 `increment_amount`。
*   **上限:** 计数器无理论上限，可以持续增长。

##### 3.3. 显示机制 (Display Mechanism)

*   **位置:** 计数器数字将显示在屏幕的中心位置。
*   **格式:** 显示为纯数字文本。
*   **实时更新:** 每次计数增加后，显示内容应立即刷新。

#### 4. 用户界面 (UI)

##### 4.1. 主界面布局

*   **计数显示:** 屏幕正中央，以大字体显示当前计数。
*   **点击按钮:** 位于计数显示下方，作为主要的交互区域。按钮应有清晰的视觉标识，表明其可点击性。

##### 4.2. 视觉风格

*   **整体风格:** 遵循 `project_rules.yaml` 中定义的“像素风”。
*   **按钮:** 像素风格的按钮图标或简单的矩形按钮。
*   **字体:** 选用清晰易读的像素风格字体，确保数字在大尺寸下依然美观。

#### 5. 美术资源需求

根据像素风格，我们需要以下基础美术资源：

*   **UI 元素:**
    *   `button_default.png`: 按钮默认状态。
    *   `button_pressed.png`: 按钮按下状态 (可选，但推荐提供视觉反馈)。
*   **字体:**
    *   `pixel_font.ttf` 或 `pixel_font.woff`: 用于显示计数数字的像素风格字体。

#### 6. 音效需求 (未来可扩展)

*   `click_sfx.wav`: 每次点击按钮时播放的音效。

#### 7. 技术实现考量

*   **计数逻辑:** 简单的JavaScript变量即可实现。
*   **UI 更新:** 利用Canvas API或DOM操作实时更新文本显示。
*   **事件监听:** 监听按钮的 `click` 或 `touchstart` 事件。
*   **响应式设计:** 考虑不同屏幕尺寸下UI元素的居中和缩放。

#### 8. 未来扩展方向 (作为“深度”考虑)

虽然当前需求简单，但为体现游戏设计的深度，未来可考虑：

*   **升级系统:** 引入商店，玩家可以用累计的点击数购买“每秒自动点击”或“每次点击增量提升”的升级。
*   **成就系统:** 设定里程碑成就（如“首次点击”、“点击100次”、“点击1000次”等）。
*   **主题/皮肤:** 允许玩家更改按钮和背景的视觉主题。
*   **排行榜:** 记录玩家最高计数，进行全球或本地排名。

---

## 游戏配置表 (YAML)

以下是根据上述GDD和项目规范生成的YAML配置文件。这些文件将提供给程序员，用于初始化游戏参数和UI元素。

### 文件: game_config.yaml

```yaml
# 文件: game_config.yaml
# 职责: 定义游戏的核心数值配置
# ==========================================

game_parameters:
  initial_count: 0             # 游戏开始时的初始计数
  increment_amount: 1          # 每次点击按钮时，计数器增加的数值
  
# 未来扩展配置 (当前版本未使用)
# upgrade_costs:
#   auto_click_level_1: 100
#   click_power_level_1: 50
```

### 文件: ui_config.yaml

```yaml
# 文件: ui_config.yaml
# 职责: 定义用户界面 (UI) 的布局和样式配置
# ==========================================

ui_elements:
  counter_display:
    type: text
    position:
      anchor: center           # 锚点位置，例如: center, top_left
      offset_x: 0              # 相对于锚点的X轴偏移 (像素)
      offset_y: 0              # 相对于锚点的Y轴偏移 (像素)
    font: pixel_font           # 使用的字体名称 (需在assets_config中定义)
    font_size: 64              # 字体大小 (像素)
    color: "#FFFFFF"           # 字体颜色 (十六进制)
    text_align: center         # 文本水平对齐方式

  click_button:
    type: button
    position:
      anchor: bottom_center    # 锚点位置
      offset_x: 0              # 相对于锚点的X轴偏移 (像素)
      offset_y: -100           # 相对于锚点的Y轴偏移 (像素，负值表示向上)
    size:
      width: 200               # 按钮宽度 (像素)
      height: 80               # 按钮高度 (像素)
    sprite_default: button_default.png # 按钮默认状态的图片 (需在assets_config中定义)
    sprite_pressed: button_pressed.png # 按钮按下状态的图片 (可选，需在assets_config中定义)
    text: "Click Me!"          # 按钮上显示的文本
    text_font: pixel_font      # 按钮文本字体
    text_font_size: 32         # 按钮文本字体大小
    text_color: "#000000"      # 按钮文本颜色
```

### 文件: assets_config.yaml

```yaml
# 文件: assets_config.yaml
# 职责: 定义游戏所需的所有资源路径和类型
# ==========================================

assets:
  images:
    button_default:
      path: assets/images/ui/button_default.png
      description: "主点击按钮的默认状态图片"
    button_pressed:
      path: assets/images/ui/button_pressed.png
      description: "主点击按钮的按下状态图片"
  
  fonts:
    pixel_font:
      path: assets/fonts/pixel_font.ttf
      description: "游戏UI和数字显示使用的像素风格字体"

  # audio: # 未来可扩展
  #   click_sfx:
  #     path: assets/audio/sfx/click_sfx.wav
  #     description: "点击按钮时的音效"
```

---

请程序员和美术团队查阅以上文档和配置。如有任何疑问，或需要更详细的说明，请随时提出，我会耐心解答。

## 3. 技术要求
- 技术栈: HTML5 + Canvas + JavaScript
- 平台: 浏览器
- 风格: 像素风

## 4. 配置说明
详见 config_tables.yaml

---
文档版本: 1.0
创建时间: 2026-02-12T18:57:30.519314
创建人: 策划Agent
