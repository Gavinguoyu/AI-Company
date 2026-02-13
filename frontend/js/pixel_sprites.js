/**
 * 像素风精灵生成器 – 全部用代码绘制，无需外部素材
 * 每个Agent有独特的像素角色 + 站立/工作两帧动画
 * 装饰物：桌子、电脑、植物、书架、咖啡机、任务板等
 */

/* ═══════════════════════════════════════════
   Agent 像素角色定义 (16x16 网格)
   每个颜色值对应一个像素点
   0 = 透明, 其他 = 颜色代码
   ═══════════════════════════════════════════ */

// 调色板
const PAL = {
    0: 'transparent',
    // 皮肤
    S: '#f5c6a0',  s: '#d4a574',
    // 头发
    H: '#2c1810',  h: '#1a0f08',
    // PM蓝色西装
    B: '#2563eb',  b: '#1d4ed8',
    // 策划橙色
    O: '#ea8c2a',  o: '#c97b22',
    // 程序员绿色
    G: '#22c55e',  g: '#16a34a',
    // 美术粉色
    P: '#ec4899',  p: '#db2777',
    // 测试紫色
    V: '#a855f7',  v: '#9333ea',
    // 通用
    W: '#ffffff',  w: '#e2e8f0',
    K: '#1e293b',  k: '#0f172a',
    D: '#334155',  d: '#475569',
    E: '#64748b',  // 眼睛
    R: '#ef4444',  // 红色
    Y: '#facc15',  // 黄色
    C: '#06b6d4',  // 青色
};

// ── PM (项目经理) - 蓝西装领带 ──
const PM_IDLE = [
    '0000HHHH00000000',
    '000HHHHH00000000',
    '000HSSSH00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS0000000000',
    '00BBRBBB00000000',
    '00BBRBBB00000000',
    '00bBBBBb00000000',
    '000BSBB000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

const PM_WORK = [
    '0000HHHH00000000',
    '000HHHHH00000000',
    '000HSSSH00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS0000000000',
    '0sBBRBBBS0000000',
    '00BBRBBB00000000',
    '00bBBBBb00000000',
    '000BSBB000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

// ── 策划 (Planner) - 橙色衬衫+眼镜 ──
const PLANNER_IDLE = [
    '000hhhhh00000000',
    '00hhhhhh00000000',
    '00hHSSHh00000000',
    '000SESSE00000000',
    '000KSSKK00000000',
    '0000SS0000000000',
    '00OOWOOO00000000',
    '00OOOOOO00000000',
    '00oOOOOo00000000',
    '000OSOO000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000D00D000000000',
    '000D00D000000000',
    '00DD00DD00000000',
    '0000000000000000',
];

const PLANNER_WORK = [
    '000hhhhh00000000',
    '00hhhhhh00000000',
    '00hHSSHh00000000',
    '000SESSE00000000',
    '000KSSKK00000000',
    '00Y0SS0000000000',
    '0YOOWOOO00000000',
    '00OOOOOO00000000',
    '00oOOOOo00000000',
    '000OSOO000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000D00D000000000',
    '000D00D000000000',
    '00DD00DD00000000',
    '0000000000000000',
];

// ── 程序员 (Programmer) - 绿色帽衫+笔记本 ──
const PROGRAMMER_IDLE = [
    '00GGGGGG00000000',
    '00GHHHHG00000000',
    '000HSSSH00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS0000000000',
    '00GGGGGG00000000',
    '00GGGGGG00000000',
    '00gGGGGg00000000',
    '000GSGG000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

const PROGRAMMER_WORK = [
    '00GGGGGG00000000',
    '00GHHHHG00000000',
    '000HSSSH00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS0000000000',
    '00GGGGGGs0000000',
    '00GGGGGG0DDDD000',
    '00gGGGGg0DggD000',
    '000GSGG00DDDD000',
    '000S00S000000000',
    '000S00S000000000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

// ── 美术 (Artist) - 粉色贝雷帽+画笔 ──
const ARTIST_IDLE = [
    '00PPPP0000000000',
    '0PPPPPPP0000000 ',
    '00PHSSHP00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS0000000000',
    '00PPWPPP00000000',
    '00PPPPPP00000000',
    '00pPPPPp00000000',
    '000PSPP000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

const ARTIST_WORK = [
    '00PPPP0000000000',
    '0PPPPPPP00000000',
    '00PHSSHP00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS00Y0000000',
    '00PPWPPPsY000000',
    '00PPPPPP00000000',
    '00pPPPPp00000000',
    '000PSPP000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

// ── 测试 (Tester) - 紫色T恤+放大镜 ──
const TESTER_IDLE = [
    '0000HHHH00000000',
    '000HHHHH00000000',
    '000HSSSH00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS0000000000',
    '00VVVVVV00000000',
    '00VVWVVV00000000',
    '00vVVVVv00000000',
    '000VSVV000000000',
    '000S00S000000000',
    '000S00S000000000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

const TESTER_WORK = [
    '0000HHHH00000000',
    '000HHHHH00000000',
    '000HSSSH00000000',
    '000SESSE00000000',
    '000SSSS000000000',
    '0000SS0000000000',
    '00VVVVVVs0000000',
    '00VVWVVVsCCC0000',
    '00vVVVVv0C0C0000',
    '000VSVV00CCC0000',
    '000S00S0000D0000',
    '000S00S000D00000',
    '000K00K000000000',
    '000K00K000000000',
    '00KK00KK00000000',
    '0000000000000000',
];

/* ═══════════════════════════════════════════
   精灵渲染缓存系统
   ═══════════════════════════════════════════ */

class PixelSpriteRenderer {
    constructor() {
        /** @type {Map<string, OffscreenCanvas|HTMLCanvasElement>} */
        this.cache = new Map();
        this.pixelSize = 3;  // 每个像素渲染为 3x3 CSS像素
    }

    /**
     * 将16x16像素数组渲染到离屏canvas并缓存
     * @param {string} key 缓存键
     * @param {string[]} data 16行字符串数组
     * @param {number} scale 缩放倍数
     * @returns {HTMLCanvasElement}
     */
    renderSprite(key, data, scale = this.pixelSize) {
        if (this.cache.has(key)) return this.cache.get(key);

        const size = 16 * scale;
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');

        for (let y = 0; y < 16; y++) {
            const row = data[y] || '';
            for (let x = 0; x < 16; x++) {
                const ch = row[x] || '0';
                if (ch === '0' || ch === ' ') continue;
                const color = PAL[ch];
                if (!color || color === 'transparent') continue;
                ctx.fillStyle = color;
                ctx.fillRect(x * scale, y * scale, scale, scale);
            }
        }

        this.cache.set(key, canvas);
        return canvas;
    }

    /** 获取Agent的两帧动画 */
    getAgentFrames(agentId) {
        const sprites = {
            pm:         { idle: PM_IDLE,         work: PM_WORK },
            planner:    { idle: PLANNER_IDLE,     work: PLANNER_WORK },
            programmer: { idle: PROGRAMMER_IDLE,  work: PROGRAMMER_WORK },
            artist:     { idle: ARTIST_IDLE,      work: ARTIST_WORK },
            tester:     { idle: TESTER_IDLE,      work: TESTER_WORK },
        };
        const def = sprites[agentId];
        if (!def) return null;

        return {
            idle: this.renderSprite(`${agentId}_idle`, def.idle),
            work: this.renderSprite(`${agentId}_work`, def.work),
        };
    }
}

/* ═══════════════════════════════════════════
   装饰物像素图
   ═══════════════════════════════════════════ */

// 办公桌 (16x8)
const DESK_PIXELS = [
    '0KKKKKKKKKKKKKK0',
    'KddddddddddddddK',
    'KddddddddddddddK',
    'KDDDDDDDDDDDDDDK',
    '0K0000000000000K0',
    '0K0000000000000K0',
    '0K0000000000000K0',
    '0KK000000000000KK',
];

// 电脑显示器 (10x8)
const MONITOR_PIXELS = [
    '00KKKKKKKK000000',
    '00KggggggK000000',
    '00KgCgCggK000000',
    '00KggggggK000000',
    '00KggGgggK000000',
    '00KKKKKKKK000000',
    '0000KKKK00000000',
    '000KKKKKK0000000',
];

// 植物 (8x12)
const PLANT_PIXELS = [
    '0000GG0000000000',
    '000GgGG000000000',
    '00GGGgGG00000000',
    '00GgGGgG00000000',
    '0GGGggGGG0000000',
    '0GgGGGGgG0000000',
    '00GGgGGG00000000',
    '000GgGG000000000',
    '0000KK0000000000',
    '0000KK0000000000',
    '00OOOOOO00000000',
    '00OOOOOO00000000',
];

// 书架 (12x16)
const BOOKSHELF_PIXELS = [
    'KKKKKKKKKKKK0000',
    'KBRGOBRPBRGK0000',
    'KBRGOBRPBRGK0000',
    'KBRGOBRPBRGK0000',
    'KDDDDDDDDDDKK00',
    'KGPBROGPBROK0000',
    'KGPBROGPBROK0000',
    'KGPBROGPBROK0000',
    'KDDDDDDDDDDKK00',
    'KOBRGPOBRGPK0000',
    'KOBRGPOBRGPK0000',
    'KOBRGPOBRGPK0000',
    'KDDDDDDDDDDKK00',
    'K00000000000K000',
    'KKKKKKKKKKKKKK00',
    '0000000000000000',
];

// 咖啡机 (8x10)
const COFFEE_PIXELS = [
    '00DDDDDD00000000',
    '00DKKKKD00000000',
    '00DKOOKD00000000',
    '00DKKKKD00000000',
    '00DDDDDD00000000',
    '000DKKD000000000',
    '0000dd0000000000',
    '000DDDD000000000',
    '000DWWD000000000',
    '000DDDD000000000',
];

// 任务板 (14x10)
const TASKBOARD_PIXELS = [
    '0KKKKKKKKKKKK000',
    '0KwwwwwwwwwwK000',
    '0KwYwwGwwBwwK000',
    '0KwYwwGwwBwwK000',
    '0KwwwwwwwwwwK000',
    '0KwRwwYwwGwwK000',
    '0KwRwwYwwGwwK000',
    '0KwwwwwwwwwwK000',
    '0KKKKKKKKKKKK000',
    '0000000000000000',
];

// 游戏展示屏幕 (14x12)
const GAME_SCREEN_PIXELS = [
    '0KKKKKKKKKKKKKK0',
    '0KCCCCCCCCCCCCK0',
    '0KCgCCCCCCCCCCK0',
    '0KCCCGCCCgCCCCK0',
    '0KCCCCCCCCCCgCK0',
    '0KCCgCCCGCCCCCK0',
    '0KCCCCCCCCCCCCK0',
    '0KCCCCCCCCCCGCK0',
    '0KCCCGCCCCCCCCK0',
    '0KKKKKKKKKKKKKK0',
    '000000KKKK000000',
    '0000KKKKKKKK0000',
];


/* ═══════════════════════════════════════════
   导出
   ═══════════════════════════════════════════ */

export const spriteRenderer = new PixelSpriteRenderer();

// 装饰物精灵数据
export const DECORATIONS = {
    desk: DESK_PIXELS,
    monitor: MONITOR_PIXELS,
    plant: PLANT_PIXELS,
    bookshelf: BOOKSHELF_PIXELS,
    coffee: COFFEE_PIXELS,
    taskboard: TASKBOARD_PIXELS,
    gameScreen: GAME_SCREEN_PIXELS,
};

export { PixelSpriteRenderer, PAL };
export default spriteRenderer;
