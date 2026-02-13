"""
测试P0优先级: 决策机制端到端测试
验证4个决策点是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 到路径
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from workflows.game_dev_workflow import GameDevWorkflow
from api.websocket_handler import register_workflow
from utils.logger import setup_logger

logger = setup_logger("test_p0_decision")


async def test_decision_flow():
    """测试决策流程"""
    logger.info("="*60)
    logger.info("开始测试P0决策流程")
    logger.info("="*60)
    
    # 创建工作流
    workflow = GameDevWorkflow(
        project_name="test_decision_game",
        project_description="制作一个简单的测试游戏,用于验证决策机制"
    )
    
    # 注册工作流
    register_workflow("test_decision_game", workflow)
    
    # 模拟自动决策函数
    decision_count = 0
    
    async def auto_decide():
        """自动提交决策（模拟用户点击）"""
        nonlocal decision_count
        await asyncio.sleep(3)  # 等待3秒模拟用户思考
        
        # 检查是否有待决策
        if workflow.pending_decisions:
            decision_id = list(workflow.pending_decisions.keys())[0]
            decision_count += 1
            
            # 根据决策点选择不同的选项
            if decision_count == 1:
                # 决策点1: 立项确认
                choice = "确认,开始策划"
                logger.info(f"🤖 自动决策 #{decision_count}: {choice}")
            elif decision_count == 2:
                # 决策点2: 策划审批
                choice = "批准,进入技术设计"
                logger.info(f"🤖 自动决策 #{decision_count}: {choice}")
            elif decision_count == 3:
                # 决策点3: 开发验收
                choice = "进入测试"
                logger.info(f"🤖 自动决策 #{decision_count}: {choice}")
            elif decision_count == 4:
                # 决策点4: 交付确认
                choice = "确认交付"
                logger.info(f"🤖 自动决策 #{decision_count}: {choice}")
            else:
                choice = "继续"
                logger.info(f"🤖 自动决策 #{decision_count}: {choice}")
            
            # 提交决策
            workflow.submit_boss_decision(decision_id, choice)
    
    # 启动自动决策循环
    async def auto_decision_loop():
        """持续检查并自动决策"""
        while workflow.status != "已完成" and workflow.status != "失败":
            await auto_decide()
            await asyncio.sleep(2)
    
    # 并行运行工作流和自动决策
    try:
        await asyncio.gather(
            workflow.start(),
            auto_decision_loop()
        )
        
        logger.info("")
        logger.info("="*60)
        logger.info("✅ 决策流程测试完成!")
        logger.info(f"总决策次数: {decision_count}")
        logger.info(f"工作流状态: {workflow.status}")
        logger.info("="*60)
        
        # 验证决策日志
        decision_log_path = workflow.knowledge_base_dir / "decision_log.yaml"
        if decision_log_path.exists():
            logger.info("✅ 决策日志文件已生成")
            with open(decision_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"决策日志内容预览:\n{content[:500]}...")
        else:
            logger.warning("⚠️ 决策日志文件未生成")
        
        # 检查是否达到预期的4个决策点
        if decision_count >= 4:
            logger.info(f"✅ 成功触发了 {decision_count} 个决策点")
            return True
        else:
            logger.error(f"❌ 只触发了 {decision_count} 个决策点,预期4个")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_decision_flow())
    sys.exit(0 if success else 1)
