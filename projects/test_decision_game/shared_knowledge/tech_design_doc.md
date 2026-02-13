# test_decision_game 技术设计文档

## 1. 架构设计
好的，作为一名经验丰富的游戏程序员，我已仔细阅读了`game_design_doc.md`和`project_rules.yaml`。

根据项目需求和规范，我将设计以下技术架构：

**1. 文件结构**

```
projects/test_decision_game/output/
├── index.html                  # 游戏入口文件，包含Canvas和UI元素
├── css/
│   └── style.css               # 游戏样式文件
└── js/
    ├── game.js                 # 游戏主逻辑，包含Game类和游戏循环（适配为事件驱动）
    ├── ui_manager.js           # UI管理类，负责DOM操作和界面更新
    └── game_data.js            # 游戏数据文件，由YAML配置转换而来，包含所有场景和全局配置
```

**2. 模块划分与职责**

*   **`index.html`**:
    *   负责构建游戏的DOM骨架，包括显示游戏状态、场景文本、选项按钮和开始/结束界面的容器。
    *   引入 `style.css` 和 `js/game.js`。
*   **`css/style.css`**:
    *   提供游戏整体的视觉风格，包括字体、颜色、布局、按钮样式等，遵循像素风规范。
*   **`js/game_data.js`**:
    *   这是一个静态数据文件，将 `game_config.yaml` 和 `scenario_data.yaml` 的内容转换为 JavaScript 对象，供 `Game` 类使用，避免运行时解析YAML的复杂性。
    *   导出一个 `GAME_CONFIG` 对象和一个 `SCENARIO_DATA` 数组。
*   **`js/ui_manager.js`**:
    *   定义 `UIManager` 类，封装所有与DOM交互的逻辑。
    *   提供方法来更新玩家状态显示、显示场景文本、生成选项按钮、显示不同的游戏屏幕（开始、游戏主界面、结局）。
    *   负责事件监听（如按钮点击），并将事件传递给 `Game` 类处理。
*   **`js/game.js`**:
    *   定义 `Game` 类，作为游戏的核心控制器。
    *   管理游戏状态（玩家生命值、士气、当前场景ID）。
    *   包含游戏初始化、开始、重置、处理玩家选择、应用效果、检查游戏结局等核心逻辑。
    *   与 `UIManager` 协作，根据游戏逻辑更新UI。
    *   虽然是决策游戏，但仍会包含 `gameLoop` 结构，其中 `update` 和 `render` 会根据玩家操作触发，以符合标准模板要求。

**3. API Registry (`api_registry.yaml`)**

我将更新 `api_registry.yaml` 文件，记录上述设计中的主要API和方法。

---

现在，我将开始生成文件。

---

### **文件: `projects/test_decision_game/output/api_registry.yaml`**

```yaml
# 文件: api_registry.yaml
# 职责: 记录游戏中主要的API、函数和方法
# ==========================================

# 全局API/函数
global_apis:
  - name: "initGame"
    description: "游戏初始化入口点"
    parameters: []
    returns: "void"

# 类: Game (js/game.js)
game_class_apis:
  - name: "constructor"
    description: "Game类的构造函数，初始化游戏状态和依赖"
    parameters:
      - name: "uiManager"
        type: "UIManager"
        description: "UI管理器实例"
      - name: "gameConfig"
        type: "object"
        description: "游戏全局配置数据"
      - name: "scenarioData"
        type: "object"
        description: "所有场景数据"
    returns: "Game实例"
  - name: "init"
    description: "初始化游戏逻辑，绑定UI事件，显示开始界面"
    parameters: []
    returns: "void"
  - name: "startGame"
    description: "开始新游戏，重置玩家状态并加载初始场景"
    parameters: []
    returns: "void"
  - name: "resetGame"
    description: "重置玩家状态到初始值"
    parameters: []
    returns: "void"
  - name: "processOption"
    description: "处理玩家选择的选项，应用效果并推进游戏"
    parameters:
      - name: "optionIndex"
        type: "number"
        description: "玩家选择的选项索引"
    returns: "void"
  - name: "applyEffect"
    description: "根据效果类型更新玩家状态或游戏流程"
    parameters:
      - name: "effect"
        type: "object"
        description: "单个效果对象，包含type和value"
    returns: "void"
  - name: "checkGameEnd"
    description: "检查游戏是否达到结束条件"
    parameters: []
    returns: "boolean"
  - name: "endGame"
    description: "触发游戏结局，显示结局界面"
    parameters:
      - name: "endingType"
        type: "string"
        description: "结局类型（success, fail, neutral）"
      - name: "endingText"
        type: "string"
        description: "结局描述文本"
    returns: "void"
  - name: "loadScenario"
    description: "加载并显示指定ID的场景"
    parameters:
      - name: "scenarioId"
        type: "string"
        description: "要加载的场景ID"
    returns: "void"
  - name: "getScenarioById"
    description: "根据ID获取场景数据"
    parameters:
      - name: "id"
        type: "string"
        description: "场景ID"
    returns: "object | undefined"
  - name: "gameLoop"
    description: "游戏主循环 (适用于连续更新，本游戏主要由事件驱动)"
    parameters: []
    returns: "void"
  - name: "update"
    description: "更新游戏逻辑和状态"
    parameters: []
    returns: "void"
  - name: "render"
    description: "渲染游戏画面和UI"
    parameters: []
    returns: "void"

# 类: UIManager (js/ui_manager.js)
ui_manager_class_apis:
  - name: "constructor"
    description: "UIManager类的构造函数，获取DOM元素引用"
    parameters:
      - name: "elements"
        type: "object"
        description: "包含DOM元素引用的对象"
    returns: "UIManager实例"
  - name: "showStartScreen"
    description: "显示开始界面"
    parameters: []
    returns: "void"
  - name: "hideStartScreen"
    description: "隐藏开始界面"
    parameters: []
    returns: "void"
  - name: "showGameScreen"
    description: "显示游戏主界面"
    parameters: []
    returns: "void"
  - name: "hideGameScreen"
    description: "隐藏游戏主界面"
    parameters: []
    returns: "void"
  - name: "showEndingScreen"
    description: "显示游戏结局界面"
    parameters:
      - name: "title"
        type: "string"
        description: "结局标题"
      - name: "message"
        type: "string"
        description: "结局消息"
    returns: "void"
  - name: "updatePlayerStats"
    description: "更新玩家生命值和士气显示"
    parameters:
      - name: "health"
        type: "number"
        description: "当前生命值"
      - name: "morale"
        type: "number"
        description: "当前士气"
    returns: "void"
  - name: "displayScenario"
    description: "显示场景文本和选项按钮"
    parameters:
      - name: "scenario"
        type: "object"
        description: "当前场景数据"
    returns: "void"
  - name: "clearOptions"
    description: "清除所有选项按钮"
    parameters: []
    returns: "void"
  - name: "setOptionButtonClickHandler"
    description: "为选项按钮设置点击事件处理器"
    parameters:
      - name: "handler"
        type: "function"
        description: "点击事件回调函数，参数为选项索引"
    returns: "void"
  - name: "setRestartButtonClickHandler"
    description: "为重新开始按钮设置点击事件处理器"
    parameters:
      - name: "handler"
        type: "function"
        description: "点击事件回调函数"
    returns: "void"
  - name: "setStartButtonClickHandler"
    description: "为开始游戏按钮设置点击事件处理器"
    parameters:
      - name: "handler"
        type: "function"
        description: "点击事件回调函数"
    returns: "void"

# 模块: game_data (js/game_data.js)
game_data_module_apis:
  - name: "GAME_CONFIG"
    type: "object"
    description: "游戏全局配置对象"
  - name: "SCENARIO_DATA"
    type: "object"
    description: "所有游戏场景数据对象"
```
已写入 projects/test_decision_game/output/api_registry.yaml

---

### **文件: `projects/test_decision_game/output/js/game_data.js`**

```javascript
// 文件: js/game_data.js
// 职责: 存储游戏的全局配置和所有场景数据
// 由 game_config.yaml 和 scenario_data.yaml 转换而来
// ==========================================

/**
 * @typedef {object} GameConfig
 * @property {string} game_name - 游戏的显示名称
 * @property {number} initial_health - 初始生命值
 * @property {number} max_health - 生命值上限
 * @property {number} initial_morale - 初始士气
 * @property {number} max_morale - 士气上限
 * @property {number} game_over_health_threshold - 生命值低于或等于此值时游戏失败
 * @property {string} success_scenario_id - 成功结局的场景ID
 * @property {string} fail_scenario_id - 默认失败结局的场景ID
 * @property {string} neutral_scenario_id - 中立结局的场景ID
 */

/**
 * @typedef {object} Effect
 * @property {string} type - 效果类型 (e.g., "health_change", "morale_change", "next_scenario")
 * @property {(number|string)} value - 效果值 (数值增减量或目标场景ID)
 */

/**
 * @typedef {object} Option
 * @property {string} text - 选项描述文本
 * @property {Effect[]} effects - 选择此选项后触发的效果列表
 */

/**
 * @typedef {object} Scenario
 * @property {string} id - 场景的唯一标识符
 * @property {string} text - 场景描述文本
 * @property {Option[]} options - 玩家可选择的选项列表
 */

/**
 * 游戏全局配置对象
 * @type {GameConfig}
 */
export const GAME_CONFIG = {
  game_settings: {
    game_name: "决策测试游戏",
    initial_health: 100,
    max_health: 100,
    initial_morale: 50,
    max_morale: 100,
    game_over_health_threshold: 0,
    success_scenario_id: "ending_success",
    fail_scenario_id: "ending_fail_generic",
    neutral_scenario_id: "ending_neutral",
  },
};

/**
 * 所有游戏场景数据数组
 * @type {Scenario[]}
 */
export const SCENARIO_DATA = [
  // 初始场景
  {
    id: "start",
    text: "你是一名新手冒险者，独自来到一个古老的森林边缘。天色渐晚，你必须做出第一个选择。",
    options: [
      {
        text: "进入森林深处，寻找庇护所。",
        effects: [
          { type: "health_change", value: -10 },
          { type: "morale_change", value: -5 },
          { type: "next_scenario", value: "forest_path" },
        ],
      },
      {
        text: "在森林边缘扎营，等待天亮。",
        effects: [
          { type: "health_change", value: +5 },
          { type: "morale_change", value: +10 },
          { type: "next_scenario", value: "camp_night" },
        ],
      },
    ],
  },

  // 场景1: 森林深处
  {
    id: "forest_path",
    text: "森林深处阴森恐怖，你发现一条岔路。左边似乎有一丝光亮，右边则更加黑暗，但传来微弱的水声。",
    options: [
      {
        text: "走向有光亮的路。",
        effects: [
          { type: "health_change", value: -15 },
          { type: "morale_change", value: -10 },
          { type: "next_scenario", value: "light_path_event" },
        ],
      },
      {
        text: "走向有水声的路。",
        effects: [
          { type: "health_change", value: +5 },
          { type: "morale_change", value: +15 },
          { type: "next_scenario", value: "water_path_event" },
        ],
      },
    ],
  },

  // 场景2.1: 光亮处事件
  {
    id: "light_path_event",
    text: "你走到光亮处，发现一个废弃的营地。没有食物，但你找到一个破旧的背包。",
    options: [
      {
        text: "检查背包。",
        effects: [
          { type: "health_change", value: -5 }, // 检查背包可能有风险
          { type: "morale_change", value: +10 }, // 但可能找到好东西
          { type: "next_scenario", value: "check_bag" },
        ],
      },
      {
        text: "离开营地，继续探索。",
        effects: [
          { type: "health_change", value: -5 },
          { type: "morale_change", value: -5 },
          { type: "next_scenario", value: "forest_continue" }, // 继续在森林中探索的通用场景
        ],
      },
    ],
  },

  // 场景2.1.1: 检查背包
  {
    id: "check_bag",
    text: "背包里空无一物，你感到失望。然而，你发现一个隐藏的隔层，里面有几枚闪亮的金币！",
    options: [
      {
        text: "收起金币，离开营地。",
        effects: [
          { type: "health_change", value: 0 },
          { type: "morale_change", value: +20 },
          { type: "next_scenario", value: "ending_success" }, // 获得财富，直接成功结局
        ],
      },
    ],
  },

  // 场景2.1.2: 继续探索 (通用场景)
  {
    id: "forest_continue",
    text: "你决定不理会废弃营地，继续在森林中前行。不久，你迷失了方向，感到精疲力尽。",
    options: [
      {
        text: "找地方休息。",
        effects: [
          { type: "health_change", value: -10 },
          { type: "morale_change", value: -15 },
          { type: "next_scenario", value: "ending_fail_generic" }, // 疲惫不堪，导致失败
        ],
      },
    ],
  },

  // 场景2.2: 水声处事件
  {
    id: "water_path_event",
    text: "你沿着水声来到一条清澈的小溪边。你感到口渴，但水边似乎有奇怪的脚印。",
    options: [
      {
        text: "直接饮水。",
        effects: [
          { type: "health_change", value: -20 }, // 饮用不洁净的水，可能中毒
          { type: "morale_change", value: -10 },
          { type: "next_scenario", value: "ending_fail_generic" }, // 直接导致失败
        ],
      },
      {
        text: "寻找其他水源。",
        effects: [
          { type: "health_change", value: -5 }, // 寻找过程中体力消耗
          { type: "morale_change", value: +5 }, // 但士气保持
          { type: "next_scenario", value: "find_other_water" },
        ],
      },
    ],
  },

  // 场景2.2.1: 寻找其他水源
  {
    id: "find_other_water",
    text: "你谨慎地寻找，发现了一个隐藏的泉

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
创建时间: 2026-02-12T15:02:21.665497
创建人: 程序员Agent
