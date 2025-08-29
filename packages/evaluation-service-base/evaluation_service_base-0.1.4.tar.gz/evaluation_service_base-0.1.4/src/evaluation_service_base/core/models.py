
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from evaluation_service_base.core.enum import TaskStatus, EvaluationStep


@dataclass
class TaskProgressState:
    """任务进度状态"""
    task_id: str
    status: TaskStatus = TaskStatus.PENDING  # 🆕 使用枚举
    overall_progress: int = 0
    current_step: Optional[EvaluationStep] = None
    current_step_progress: float = 0.0
    message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    error_info: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    cancelled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,  # ✅ 正确使用
            "status_display": self.status.display_name,  # ✅ 正确使用
            "overall_progress": self.overall_progress,
            "current_step": {
                "name": self.current_step.display_name if self.current_step else None,
                "progress": self.current_step_progress
            } if self.current_step else None,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "cancelled": self.cancelled
        }

    def update_step_progress(self, step: EvaluationStep, step_progress: float, message: str = ""):
        """更新当前步骤进度"""
        self.current_step = step
        self.current_step_progress = max(0, min(100, step_progress))
        self.overall_progress = step.calculate_overall_progress(self.current_step_progress)

        if message:
            self.message = f"{step.display_name}: {message}"
        else:
            self.message = f"{step.display_name}: {self.current_step_progress:.1f}%"

        self.updated_at = datetime.now()

        # 🆕 使用枚举比较
        if self.status == TaskStatus.PENDING and step_progress > 0:
            self.status = TaskStatus.RUNNING

    def complete_step(self, step: EvaluationStep, message: str = ""):
        """完成步骤"""
        self.update_step_progress(step, 100.0, message or "完成")

    def mark_as_completed(self, result: Optional[Dict] = None):
        """标记为完成"""
        self.status = TaskStatus.COMPLETED
        self.overall_progress = 100
        self.message = "任务完成"
        self.result = result
        self.updated_at = datetime.now()

    def mark_as_failed(self, error: str, error_info: Optional[Dict] = None):
        """标记为失败"""
        self.status = TaskStatus.FAILED
        self.message = error
        self.error_info = error_info
        self.updated_at = datetime.now()

    def mark_as_cancelled(self):
        """标记为已取消"""
        self.status = TaskStatus.CANCELLED
        self.cancelled = True
        self.message = "任务已被取消"
        self.updated_at = datetime.now()

    def can_be_cancelled(self) -> bool:
        """判断是否可以被取消"""
        return self.status == TaskStatus.RUNNING

    def is_active(self) -> bool:
        """判断任务是否处于活跃状态"""
        return self.status in [TaskStatus.PENDING, TaskStatus.RUNNING]

    def is_finished(self) -> bool:
        """判断任务是否已结束"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]

