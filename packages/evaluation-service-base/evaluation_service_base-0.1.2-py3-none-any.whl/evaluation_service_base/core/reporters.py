from evaluation_service_base.core.enum import EvaluationStep
from evaluation_service_base.core.managers import StepProgressManager


class StepProgressReporter:
    """步骤进度报告器 - 传递给子类使用"""

    def __init__(self, manager: StepProgressManager, task_id: str, step: EvaluationStep):
        self.manager = manager
        self.task_id = task_id
        self.step = step

    def update(self, progress: float, message: str = ""):
        """更新当前步骤的进度 - 子类只需要关注这个方法"""
        self.manager.update_step_progress(self.task_id, self.step, progress, message)

