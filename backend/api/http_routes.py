"""
文件: api/http_routes.py
职责: HTTP REST API 路由定义
依赖: fastapi, workflows/game_dev_workflow.py
被依赖: main.py
关键接口:
  - POST /project/start - 发起新项目
  - GET /project/{project_id}/status - 获取项目状态
  - POST /boss/decision - 老板提交决策
  - GET /projects - 获取所有项目列表
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi import APIRouter, HTTPException, Body, BackgroundTasks, Request
from pydantic import BaseModel, Field
import asyncio

from config import Config
from utils.logger import setup_logger
from workflows.game_dev_workflow import GameDevWorkflow
from api.websocket_handler import (
    broadcast_agent_message, 
    broadcast_agent_status, 
    broadcast_phase_change,
    register_workflow,
    unregister_workflow
)


# 创建路由器
router = APIRouter(tags=["HTTP API"])

# 创建日志器
logger = setup_logger("http_routes", log_level=Config.LOG_LEVEL, log_to_file=Config.LOG_TO_FILE)


# =====================================================
# 请求/响应模型定义
# =====================================================

class ProjectStartRequest(BaseModel):
    """发起新项目的请求"""
    game_idea: str = Field(..., description="游戏创意描述", min_length=5)
    project_name: Optional[str] = Field(None, description="项目名称（可选，自动生成）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "game_idea": "做一个贪吃蛇游戏，像素风格，带道具系统",
                "project_name": "snake_game"
            }
        }


class ProjectStartResponse(BaseModel):
    """发起新项目的响应"""
    success: bool
    project_id: str
    message: str
    created_at: str


class ProjectStatusResponse(BaseModel):
    """项目状态响应"""
    project_id: str
    project_name: str
    status: str  # 状态: pending, planning, developing, testing, completed, failed
    current_phase: str
    progress: float  # 进度百分比 0-100
    tasks_completed: int
    tasks_total: int
    agents_status: Dict[str, str]  # Agent ID -> 状态
    created_at: str
    updated_at: str


class BossDecisionRequest(BaseModel):
    """老板决策请求"""
    project_id: str = Field(..., description="项目ID")
    decision_id: str = Field(..., description="决策点ID")
    decision_type: str = Field(..., description="决策类型: approve/reject/modify/custom")
    decision_content: Optional[str] = Field(None, description="决策内容（自定义输入）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "snake_game_20260211",
                "decision_id": "design_approval_1",
                "decision_type": "approve",
                "decision_content": None
            }
        }


class BossDecisionResponse(BaseModel):
    """老板决策响应"""
    success: bool
    message: str


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    total: int
    projects: List[Dict[str, Any]]


# =====================================================
# 全局状态管理（临时，后续可用 Redis 替代）
# =====================================================

# 项目存储（内存中）
projects_store: Dict[str, Dict[str, Any]] = {}

# 待处理的决策请求
pending_decisions: Dict[str, Dict[str, Any]] = {}

# 运行中的工作流
running_workflows: Dict[str, GameDevWorkflow] = {}


# =====================================================
# API 路由定义
# =====================================================

@router.get("/health")
async def health_check():
    """
    健康检查接口
    
    Returns:
        服务状态信息
    """
    return {
        "status": "healthy",
        "service": "AI Game Studio",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


async def run_workflow_background(project_id: str, project_name: str, game_idea: str):
    """
    后台运行工作流
    """
    try:
        logger.info(f"🚀 启动工作流: {project_id}")
        
        # 创建工作流实例
        workflow = GameDevWorkflow(project_name, game_idea)
        running_workflows[project_id] = workflow
        
        # 注册工作流到 WebSocket 处理器（用于决策处理）
        register_workflow(project_id, workflow)
        
        # 更新项目状态
        if project_id in projects_store:
            projects_store[project_id]["status"] = "running"
            projects_store[project_id]["current_phase"] = "立项"
        
        # 启动工作流（start()内部会调用initialize()，无需额外初始化）
        await workflow.start()
        
        # 工作流完成
        logger.info(f"✅ 工作流完成: {project_id}")
        
        if project_id in projects_store:
            projects_store[project_id]["status"] = "completed"
            projects_store[project_id]["progress"] = 100.0
            
    except Exception as e:
        logger.error(f"❌ 工作流执行失败: {e}", exc_info=True)
        if project_id in projects_store:
            projects_store[project_id]["status"] = "failed"
    finally:
        # 注销工作流
        unregister_workflow(project_id)
        if project_id in running_workflows:
            del running_workflows[project_id]


@router.post("/project/start", response_model=ProjectStartResponse)
async def start_project(request: ProjectStartRequest, background_tasks: BackgroundTasks):
    """
    发起新游戏开发项目
    
    Args:
        request: 项目启动请求
        background_tasks: 后台任务
    
    Returns:
        项目创建结果
    """
    try:
        logger.info(f"收到新项目请求: {request.game_idea[:50]}...")
        
        # 生成项目ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = request.project_name or f"game_{timestamp}"
        project_id = f"{project_name}_{timestamp}"
        
        # 创建项目记录
        project = {
            "project_id": project_id,
            "project_name": project_name,
            "game_idea": request.game_idea,
            "status": "pending",
            "current_phase": "立项",
            "progress": 0.0,
            "tasks_completed": 0,
            "tasks_total": 14,  # 7个阶段，每个阶段约2个任务
            "agents_status": {
                "pm": "idle",
                "planner": "idle",
                "programmer": "idle",
                "artist": "idle",
                "tester": "idle"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存到存储
        projects_store[project_id] = project
        
        logger.info(f"✅ 项目创建成功: {project_id}")
        
        # 启动游戏开发工作流（后台任务）
        background_tasks.add_task(run_workflow_background, project_id, project_name, request.game_idea)
        
        return ProjectStartResponse(
            success=True,
            project_id=project_id,
            message=f"项目 '{project_name}' 已创建，AI 团队正在启动...",
            created_at=project["created_at"]
        )
        
    except Exception as e:
        logger.error(f"创建项目失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")


@router.get("/project/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(project_id: str):
    """
    获取项目状态
    
    Args:
        project_id: 项目ID
    
    Returns:
        项目当前状态信息
    """
    try:
        # 查找项目
        project = projects_store.get(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
        
        logger.debug(f"查询项目状态: {project_id}")
        
        return ProjectStatusResponse(**project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询项目状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    获取所有项目列表
    
    Args:
        status: 可选的状态过滤（pending/planning/developing/testing/completed/failed）
        limit: 返回数量限制
        offset: 偏移量（分页）
    
    Returns:
        项目列表
    """
    try:
        # 获取所有项目
        all_projects = list(projects_store.values())
        
        # 状态过滤
        if status:
            all_projects = [p for p in all_projects if p["status"] == status]
        
        # 按创建时间倒序排序
        all_projects.sort(key=lambda x: x["created_at"], reverse=True)
        
        # 分页
        total = len(all_projects)
        projects = all_projects[offset:offset + limit]
        
        logger.debug(f"查询项目列表: 总数={total}, 返回={len(projects)}")
        
        return ProjectListResponse(
            total=total,
            projects=projects
        )
        
    except Exception as e:
        logger.error(f"查询项目列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/boss/decision", response_model=BossDecisionResponse)
async def submit_boss_decision(request: BossDecisionRequest):
    """
    老板提交决策
    
    Args:
        request: 决策请求
    
    Returns:
        决策处理结果
    """
    try:
        logger.info(f"收到老板决策: 项目={request.project_id}, 决策={request.decision_type}")
        
        # 验证项目存在
        if request.project_id not in projects_store:
            raise HTTPException(status_code=404, detail=f"项目不存在: {request.project_id}")
        
        # 验证决策点存在
        if request.decision_id not in pending_decisions:
            raise HTTPException(
                status_code=404,
                detail=f"决策点不存在或已处理: {request.decision_id}"
            )
        
        # 获取决策点信息
        decision_point = pending_decisions[request.decision_id]
        
        # 记录决策结果
        decision_result = {
            "decision_id": request.decision_id,
            "decision_type": request.decision_type,
            "decision_content": request.decision_content,
            "timestamp": datetime.now().isoformat()
        }
        
        # TODO: 将决策结果传递给等待的 Agent
        # 当前 P5 阶段先记录，P4 工作流集成时再实现
        
        # 从待处理列表移除
        del pending_decisions[request.decision_id]
        
        logger.info(f"✅ 决策已处理: {request.decision_id}")
        
        return BossDecisionResponse(
            success=True,
            message="决策已提交，AI 团队继续工作中..."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理决策失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.delete("/project/{project_id}")
async def delete_project(project_id: str):
    """
    删除项目
    
    Args:
        project_id: 项目ID
    
    Returns:
        删除结果
    """
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
        
        # 删除项目
        del projects_store[project_id]
        
        logger.info(f"✅ 项目已删除: {project_id}")
        
        return {
            "success": True,
            "message": f"项目 {project_id} 已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除项目失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/project/{project_id}/file")
async def get_project_file(project_id: str, path: str):
    """
    获取项目文件内容
    
    Args:
        project_id: 项目ID
        path: 文件路径（相对于项目目录）
    
    Returns:
        文件内容和元信息
    """
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
        
        # 构建完整文件路径
        from pathlib import Path
        project_dir = Config.PROJECTS_DIR / project_id
        file_path = project_dir / path
        
        # 安全检查：确保文件在项目目录内
        try:
            file_path = file_path.resolve()
            project_dir = project_dir.resolve()
            if not str(file_path).startswith(str(project_dir)):
                raise HTTPException(status_code=403, detail="访问被拒绝：文件路径不合法")
        except Exception:
            raise HTTPException(status_code=403, detail="访问被拒绝：文件路径不合法")
        
        # 检查文件是否存在
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"文件不存在: {path}")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail=f"不是文件: {path}")
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果不是文本文件，返回错误
            raise HTTPException(status_code=400, detail="不支持读取二进制文件")
        
        # 获取文件信息
        file_stat = file_path.stat()
        
        return {
            "success": True,
            "file_path": path,
            "content": content,
            "size": file_stat.st_size,
            "modified_time": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"读取失败: {str(e)}")


@router.post("/project/{project_id}/feedback")
async def submit_feedback(project_id: str, request: Request):
    """
    提交游戏反馈/Bug报告
    
    Args:
        project_id: 项目ID
        request: 包含feedback和severity的JSON
    
    Returns:
        提交结果
    """
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
        
        # 解析请求体
        body = await request.json()
        feedback = body.get('feedback', '')
        severity = body.get('severity', 'normal')
        
        if not feedback:
            raise HTTPException(status_code=400, detail="反馈内容不能为空")
        
        # 读取或创建bug_tracker.yaml
        from pathlib import Path
        project_dir = Config.PROJECTS_DIR / project_id
        bug_tracker_path = project_dir / "shared_knowledge" / "bug_tracker.yaml"
        
        if bug_tracker_path.exists():
            with open(bug_tracker_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = f"# Bug追踪器\n# 项目名称: {project_id}\n\nBug列表:\n"
        
        # 添加新的Bug记录
        bug_id = f"bug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        new_bug = f"""
  - id: {bug_id}
    status: open
    severity: {severity}
    description: {feedback}
    reported_by: boss
    reported_at: {datetime.now().isoformat()}
"""
        
        # 如果Bug列表为空，初始化
        if "Bug列表:" in content and content.strip().endswith("Bug列表:"):
            content = content.rstrip() + " []"
        
        content += new_bug
        
        # 写入文件
        with open(bug_tracker_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ 收到反馈: {project_id} - {feedback[:50]}...")
        
        # TODO: 触发Bug修复流程（需要重新启动工作流的Bug修复阶段）
        # 这里先简单记录，完整实现需要工作流支持
        
        return {
            "success": True,
            "message": "反馈已提交，AI团队将进行修复",
            "bug_id": bug_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交反馈失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"提交失败: {str(e)}")


@router.get("/project/{project_id}/files")
async def list_project_files(project_id: str, directory: str = ""):
    """
    列出项目文件列表
    
    Args:
        project_id: 项目ID
        directory: 目录路径（相对于项目目录，默认为根目录）
    
    Returns:
        文件和目录列表
    """
    try:
        if project_id not in projects_store:
            raise HTTPException(status_code=404, detail=f"项目不存在: {project_id}")
        
        # 构建完整目录路径
        from pathlib import Path
        project_dir = Config.PROJECTS_DIR / project_id
        target_dir = project_dir / directory if directory else project_dir
        
        # 安全检查
        try:
            target_dir = target_dir.resolve()
            project_dir = project_dir.resolve()
            if not str(target_dir).startswith(str(project_dir)):
                raise HTTPException(status_code=403, detail="访问被拒绝：目录路径不合法")
        except Exception:
            raise HTTPException(status_code=403, detail="访问被拒绝：目录路径不合法")
        
        # 检查目录是否存在
        if not target_dir.exists():
            raise HTTPException(status_code=404, detail=f"目录不存在: {directory}")
        
        if not target_dir.is_dir():
            raise HTTPException(status_code=400, detail=f"不是目录: {directory}")
        
        # 列出文件和目录
        items = []
        for item in target_dir.iterdir():
            item_stat = item.stat()
            relative_path = item.relative_to(project_dir)
            
            items.append({
                "name": item.name,
                "path": str(relative_path).replace("\\", "/"),
                "type": "directory" if item.is_dir() else "file",
                "size": item_stat.st_size if item.is_file() else 0,
                "modified_time": datetime.fromtimestamp(item_stat.st_mtime).isoformat()
            })
        
        # 按类型和名称排序（目录在前）
        items.sort(key=lambda x: (x["type"] != "directory", x["name"]))
        
        return {
            "success": True,
            "directory": directory,
            "items": items,
            "total": len(items)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"列出文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出失败: {str(e)}")
