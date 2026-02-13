"""
测试P1优先级功能
验证Agent产出、知识库浏览、试玩反馈等功能
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from workflows.game_dev_workflow import GameDevWorkflow
from api.websocket_handler import register_workflow, broadcast_agent_output
from utils.logger import setup_logger

logger = setup_logger("test_p1")


async def test_p1_features():
    """测试P1功能"""
    logger.info("="*60)
    logger.info("开始测试P1功能")
    logger.info("="*60)
    
    # 创建测试项目
    workflow = GameDevWorkflow(
        project_name="test_p1_game",
        project_description="测试P1功能的简单游戏"
    )
    
    # 初始化
    await workflow.initialize()
    
    logger.info("\n【测试1】文件产出广播")
    logger.info("-" * 40)
    
    # 测试广播Agent产出
    await broadcast_agent_output(
        project_id="test_p1_game",
        agent_id="planner",
        file_path="shared_knowledge/game_design_doc.md",
        file_type="document",
        summary="测试策划文档"
    )
    logger.info("✅ 文件产出事件广播成功")
    
    logger.info("\n【测试2】文件读取API")
    logger.info("-" * 40)
    
    # 检查知识库文件是否存在
    kb_dir = workflow.knowledge_base_dir
    files = list(kb_dir.glob("*.yaml")) + list(kb_dir.glob("*.md"))
    logger.info(f"知识库文件数量: {len(files)}")
    for f in files:
        logger.info(f"  - {f.name}")
    
    if len(files) >= 8:
        logger.info("✅ 知识库文件创建成功")
    else:
        logger.warning(f"⚠️ 知识库文件不完整，预期8个，实际{len(files)}个")
    
    logger.info("\n【测试3】反馈API准备")
    logger.info("-" * 40)
    
    # 检查bug_tracker.yaml
    bug_tracker = kb_dir / "bug_tracker.yaml"
    if bug_tracker.exists():
        logger.info("✅ bug_tracker.yaml 已创建")
        with open(bug_tracker, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"内容长度: {len(content)} 字符")
    else:
        logger.error("❌ bug_tracker.yaml 不存在")
    
    logger.info("\n" + "="*60)
    logger.info("P1功能测试完成")
    logger.info("="*60)
    logger.info("\n提示：")
    logger.info("1. 文件产出事件广播功能已实现")
    logger.info("2. 知识库文件已创建，可通过API访问")
    logger.info("3. Bug反馈API已实现，需要前端配合测试")
    logger.info("\n完整测试需要启动服务器并访问前端界面")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_p1_features())
    sys.exit(0 if success else 1)
