
from enum import Enum

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def display_name(self) -> str:
        """获取显示名称"""
        display_names = {
            TaskStatus.PENDING: "等待中",
            TaskStatus.RUNNING: "运行中",
            TaskStatus.COMPLETED: "已完成",
            TaskStatus.FAILED: "失败",
            TaskStatus.CANCELLED: "已取消"
        }
        return display_names.get(self, self.value)

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_value(cls, value: str) -> 'TaskStatus':
        """从字符串值获取枚举"""
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"无效的任务状态: {value}")


class EvaluationStep(Enum):
    """评估步骤枚举"""
    DATA_LOADING = ("数据加载", 0, 10)
    EVALUATION = ("执行评估", 10, 90)
    CHART_GENERATION = ("图表生成", 90, 95)
    RESULT_UPLOAD = ("结果上传", 95, 100)

    def __init__(self, display_name: str, start_progress: int, end_progress: int):
        self.display_name = display_name
        self.start_progress = start_progress
        self.end_progress = end_progress

    def calculate_overall_progress(self, step_progress: float) -> int:
        """将步骤内进度转换为总体进度"""
        step_progress = max(0.0, min(100.0, step_progress))
        progress_range = self.end_progress - self.start_progress
        return int(self.start_progress + progress_range * step_progress / 100.0)
