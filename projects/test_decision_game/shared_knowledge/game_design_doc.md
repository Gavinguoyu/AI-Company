# test_decision_game 游戏策划文档

## 1. 游戏概述
制作一个简单的测试游戏,用于验证决策机制

## 2. 核心玩法
好的，作为一名资深游戏策划，我已收到项目启动通知及项目规范。`test_decision_game` 验证决策机制的需求非常明确，我将据此编写游戏策划文档 (GDD) 和相应的 YAML 配置表。

---

## 游戏策划文档 (GDD)

### 1. 游戏概述

*   **游戏名称:** 决策测试游戏 (Decision Test Game)
*   **项目名称 (内部):** `test_decision_game`
*   **游戏类型:** 交互式剧情/决策模拟
*   **核心玩法:** 玩家面对一系列情境，通过选择不同的选项来影响角色的状态（如：生命值、士气），并导向不同的后续情境或最终结局。
*   **游戏目标:** 作为技术验证项目，核心目标是测试和展示决策机制的实现，包括情境展示、选项选择、状态变化、条件判断及场景跳转的完整流程。
*   **游戏愿景:** 制作一个极简但功能完整的决策循环，为未来更复杂的决策系统打下基础。
*   **目标受众:** 程序员、美术设计师，以及对游戏决策机制感兴趣的测试人员。

### 2. 核心玩法

#### 2.1 基本游戏循环

游戏遵循一个简单的“情境-选择-结果”循环：

1.  **呈现情境:** 游戏向玩家展示一段文本描述，描述当前所处的情境。
2.  **玩家选择:** 玩家根据情境，从预设的2-3个选项中做出选择。
3.  **应用结果:** 根据玩家的选择，角色的状态（如生命值、士气）会发生变化，并可能触发特定事件或条件。
4.  **跳转:** 游戏根据选择的结果，跳转到下一个情境，或直接进入游戏结局。

#### 2.2 决策机制

*   **场景 (Scenario):** 游戏中的基本单元。每个场景包含：
    *   一个唯一的 `id` (字符串)，用于内部跳转和识别。
    *   一段 `text` (字符串)，描述当前情境。
    *   一组 `options` (列表)，玩家可以从中选择。
*   **选项 (Option):** 每个选项包含：
    *   `text` (字符串)，描述该选项。
    *   `effects` (列表)，选择此选项后将触发的一系列效果。效果可以包括：
        *   `health_change`: 改变生命值 (正值为增加，负值为减少)。
        *   `morale_change`: 改变士气 (正值为增加，负值为减少)。
        *   `next_scenario`: 跳转到指定 `scenario_id` 的场景。
        *   `condition_check` (可选，复杂决策机制可扩展): 检查玩家当前状态是否满足特定条件，例如“如果士气低于X，则此选项无效或导致不同结果”。为了简单起见，本次测试暂不实现此复杂条件，但设计时会预留扩展性。
*   **状态 (State):** 玩家角色拥有以下基本状态：
    *   `health` (生命值): 初始值100，上限100。降至0或以下则游戏失败。
    *   `morale` (士气): 初始值50，上限100。影响玩家的心情，可能在未来影响某些选项的可用性或效果。

### 3. 游戏系统

#### 3.1 状态管理系统

*   **生命值 (Health):**
    *   初始值: 100
    *   上限: 100
    *   下限: 0 (低于或等于0时游戏失败)
    *   每次选择后，根据选项效果进行增减。
*   **士气 (Morale):**
    *   初始值: 50
    *   上限: 100
    *   下限: 0 (士气过低可能会导致特殊负面事件，本次测试暂不实现，但可扩展)
    *   每次选择后，根据选项效果进行增减。

#### 3.2 结局系统

游戏有三种可能的结局：

1.  **成功结局 (Success Ending):** 玩家通过一系列正确或有利的选择，达到特定的“成功场景” (`success_scenario_id`)。
2.  **失败结局 (Failure Ending):** 玩家的 `health` 降至0或以下，或者通过选择直接进入特定的“失败场景” (`fail_scenario_id`)。
3.  **中立结局 (Neutral Ending):** 玩家的旅程平稳结束，没有明显的成功或失败，达到特定的“中立场景” (`neutral_scenario_id`)。

### 4. 用户界面 (UI)

*   **整体风格:** 像素风 (根据项目规范)。
*   **主界面:**
    *   **顶部:** 状态显示区域。
        *   `生命值:` (Health Value)
        *   `士气:` (Morale Value)
    *   **中部:** 情境文本区域。
        *   显示当前场景的 `text` 内容。文本框应足够大，支持多行显示。
    *   **底部:** 选项按钮区域。
        *   根据当前场景的 `options` 数量，动态生成对应的按钮。
        *   每个按钮显示选项的 `text`。
        *   点击按钮后，触发对应选项的效果并更新界面。
*   **开始/结束界面:**
    *   **开始界面:** 包含游戏标题和一个“开始游戏”按钮。
    *   **结束界面:** 显示结局标题（如“游戏结束”、“恭喜成功”）、结局描述文本，以及一个“重新开始”按钮。

### 5. 游戏流程

1.  **加载游戏:** 游戏启动，显示开始界面。
2.  **开始游戏:** 玩家点击“开始游戏”按钮。
3.  **初始化状态:** 角色 `health` 和 `morale` 初始化为配置表中的值。
4.  **加载初始场景:** 显示 `start` 场景的文本和选项。
5.  **循环决策:**
    *   玩家阅读场景文本。
    *   玩家选择一个选项。
    *   游戏根据选项效果，更新 `health` 和 `morale`。
    *   检查 `health` 是否低于或等于0。如果是，则进入失败结局。
    *   检查选项是否直接跳转到结局场景 (`success_scenario_id`, `fail_scenario_id`, `neutral_scenario_id`)。如果是，则进入对应结局。
    *   否则，跳转到选项指定的 `next_scenario_id`，并重新显示新场景的文本和选项。
6.  **显示结局:** 游戏进入结局界面，显示结局文本和“重新开始”按钮。
7.  **重新开始:** 玩家点击“重新开始”按钮，游戏回到步骤2。

### 6. 数值设计

所有数值均通过 YAML 配置文件进行管理，避免硬编码。

#### 6.1 全局游戏设置 (`game_config.yaml`)

*   **`game_settings`:**
    *   `game_name`: 游戏的显示名称。
    *   `initial_health`: 初始生命值。
    *   `max_health`: 生命值上限。
    *   `initial_morale`: 初始士气。
    *   `max_morale`: 士气上限。
    *   `game_over_health_threshold`: 生命值低于或等于此值时游戏失败。
    *   `success_scenario_id`: 成功结局的场景ID。
    *   `fail_scenario_id`: 默认失败结局的场景ID。
    *   `neutral_scenario_id`: 中立结局的场景ID。

#### 6.2 场景与选项数据 (`scenario_data.yaml`)

*   **`scenarios`:** 一个列表，包含所有场景的定义。
    *   每个场景是一个字典，包含：
        *   `id`: 场景的唯一标识符 (字符串)。
        *   `text`: 场景描述文本 (字符串)。
        *   `options`: 玩家可选择的选项列表。
            *   每个选项是一个字典，包含：
                *   `text`: 选项描述文本 (字符串)。
                *   `effects`: 选择此选项后触发的效果列表。
                    *   每个效果是一个字典，包含：
                        *   `type`: 效果类型 (字符串，如 "health_change", "morale_change", "next_scenario")。
                        *   `value`: 效果值 (整数，`health_change` 和 `morale_change` 为增减量，`next_scenario` 为目标场景ID字符串)。

### 7. 美术需求

根据 `project_rules.yaml` 规范：

*   **风格:** 像素风。
*   **图片格式:** PNG (透明背景)。
*   **命名:** 小写字母下划线（如: `player_sprite.png`）。

#### 7.1 UI 元素

*   **背景图:** 至少一张主界面背景图 (如：森林、洞穴等情境背景，可简化为纯色或简单图案)。
*   **按钮:** 两种状态 (正常、悬停/点击) 的按钮贴图，用于选项和“开始/重新开始”按钮。
*   **状态条/图标:** 用于显示 `health` 和 `morale` 的简单图标或条形图元素。
*   **字体:** 像素风格的字体。

#### 7.2 可选元素 (若时间允许)

*   **角色头像:** 简单的主角像素头像，在状态栏旁边显示。
*   **情境插图:** 为部分关键场景提供小的像素风插图，增强代入感。

### 8. 音效需求

*   **背景音乐:** 一段简单、循环播放的背景音乐，营造氛围。
*   **UI 交互音效:**
    *   按钮点击音效。
    *   场景切换音效 (轻微的过渡音)。
*   **结果音效:**
    *   成功音效。
    *   失败音效。
    *   状态变化音效 (如：生命值增加/减少的提示音)。

### 9. 技术需求 (补充说明)

*   **数据加载:** 游戏启动时，需从 `game_config.yaml` 和 `scenario_data.yaml` 加载所有配置数据。
*   **状态存储:** 玩家当前 `health`、`morale` 和 `current_scenario_id` 需要在内存中实时更新。
*   **界面更新:** 每次决策后，UI 必须根据新的场景文本、选项和状态值进行动态更新。
*   **兼容性:** 确保在主流浏览器上运行流畅。

---

## YAML 配置表

### 文件: `game_config.yaml`

```yaml
# 文件: game_config.yaml
# 职责: 存储游戏的全局配置和初始数值
# ==========================================

game_settings:
  game_name: "决策测试游戏"
  initial_health: 100
  max_health: 100
  initial_morale: 50
  max_morale: 100
  game_over_health_threshold: 0 # 生命值小于等于此值时游戏失败
  success_scenario_id: "ending_success" # 成功结局的场景ID
  fail_scenario_id: "ending_fail_generic" # 默认失败结局的场景ID
  neutral_scenario_id: "ending_neutral" # 中立结局的场景ID
```

### 文件: `scenario_data.yaml`

```yaml
# 文件: scenario_data.yaml
# 职责: 存储所有游戏场景、选项及其效果数据
# ==========================================

scenarios:
  # 初始场景
  - id: "start"
    text: "你是一名新手冒险者，独自来到一个古老的森林边缘。天色渐晚，你必须做出第一个选择。"
    options:
      - text: "进入森林深处，寻找庇护所。"
        effects:
          - type: "health_change"
            value: -10
          - type: "morale_change"
            value: -5
          - type: "next_scenario"
            value: "forest_path"
      - text: "在森林边缘扎营，等待天亮。"
        effects:
          - type: "health_change"
            value: +5
          - type: "morale_change"
            value: +10
          - type: "next_scenario"
            value: "camp_night"

  # 场景1: 森林深处
  - id: "forest_path"
    text: "森林深处阴森恐怖，你发现一条岔路。左边似乎有一丝光亮，右边则更加黑暗，但传来微弱的水声。"
    options:
      - text: "走向有光亮的路。"
        effects:
          - type: "health_change"
            value: -15
          - type: "morale_change"
            value: -10
          - type: "next_scenario"
            value: "light_path_event"
      - text: "走向有水声的路。"
        effects:
          - type: "health_change"
            value: +5
          - type: "morale_change"
            value: +15
          - type: "next_scenario"
            value: "water_path_event"

  # 场景2.1: 光亮处事件
  - id: "light_path_event"
    text: "你走到光亮处，发现一个废弃的营地。没有食物，但你找到一个破旧的背包。"
    options:
      - text: "检查背包。"
        effects:
          - type: "health_change"
            value: -5 # 检查背包可能有风险
          - type: "morale_change"
            value: +10 # 但可能找到好东西
          - type: "next_scenario"
            value: "check_bag"
      - text: "离开营地，继续探索。"
        effects:
          - type: "health_change"
            value: -5
          - type: "morale_change"
            value: -5
          - type: "next_scenario"
            value: "forest_continue" # 继续在森林中探索的通用场景

  # 场景2.1.1: 检查背包
  - id: "check_bag"
    text: "背包里空无一物，你感到失望。然而，你发现一个隐藏的隔层，里面有几枚闪亮的金币！"
    options:
      - text: "收起金币，离开营地。"
        effects:
          - type: "health_change"
            value: 0
          - type: "morale_change"
            value: +20
          - type: "next_scenario"
            value: "ending_success" # 获得财富，直接成功结局

  # 场景2.1.2: 继续探索 (通用场景)
  - id: "forest_continue"
    text: "你决定不理会废弃营地，继续在森林中前行。不久，你迷失了方向，感到精疲力尽。"
    options:
      - text: "找地方休息。"
        effects:
          - type: "health_change"
            value: -10
          - type: "morale_change"
            value: -15
          - type: "next_scenario"
            value: "ending_fail_generic" # 疲惫不堪，导致失败

  # 场景2.2: 水声处事件
  - id: "water_path_event"
    text: "你沿着水声来到一条清澈的小溪边。你感到口渴，但水边似乎有奇怪的脚印。"
    options:
      - text: "直接饮水。"
        effects:
          - type: "health_change"
            value: -20 # 饮用不洁净的水，可能中毒
          - type: "morale_change"
            value: -10
          - type: "next_scenario"
            value: "ending_fail_generic" # 直接导致失败
      - text: "寻找其他水源。"
        effects:
          - type: "health_change"
            value: -5 # 寻找过程中体力消耗
          - type: "morale_change"
            value: +5 # 但士气保持
          - type: "next_scenario"
            value: "find_other_water"

  # 场景2.2.1: 寻找其他水源
  - id: "find_other_water"
    text: "你谨慎地寻找，发现了一个隐藏的泉眼。泉水甘甜，你感到精神焕发。"
    options:
      - text: "继续旅程。"
        effects:
          - type: "health_change"
            value: +15
          - type: "morale_change"
            value: +15
          - type: "next_scenario"
            value: "ending_neutral" # 平稳过渡，中立结局

  # 场景1.1: 扎营过夜
  - id: "camp_night"
    text: "你在森林边缘扎营，度过了一个相对平静的夜晚。虽然有些寒冷，但你得到了休息。"
    options:
      - text: "天亮后继续前进。"
        effects:
          - type: "health_change"
            value: +10
          - type: "morale_change"
            value: +10
          - type: "next_scenario"
            value: "forest_path" # 休息后回到森林深处，重新面对选择

  # 结局场景
  - id: "ending_success"
    text: "恭喜你！你成功地做出了明智的选择，度过了这次危机，并获得了宝贵的财富。你的冒险才刚刚开始！"
    options: [] # 结局场景没有选项

  - id: "ending_fail_generic"
    text: "你的冒险以失败告终。由于你的决策失误，你失去了生命或陷入绝境。请重新开始。"
    options: [] # 结局场景没有选项

  - id: "ending_neutral"
    text: "你的旅程暂时告一段落。虽然没有大富大贵，但也平稳地度过了一段时光。前方的路还很长。"
    options: [] # 结局场景没有选项
```

## 3. 技术要求
- 技术栈: HTML5 + Canvas + JavaScript
- 平台: 浏览器
- 风格: 像素风

## 4. 配置说明
详见 config_tables.yaml

---
文档版本: 1.0
创建时间: 2026-02-12T15:01:48.139792
创建人: 策划Agent
