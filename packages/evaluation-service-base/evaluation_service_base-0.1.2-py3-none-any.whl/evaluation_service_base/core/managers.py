
import os
import threading
from typing import Dict, Any, Optional, List
from libentry import logger

from evaluation_service_base.core.enum import TaskStatus, EvaluationStep
from evaluation_service_base.core.models import TaskProgressState


class StepProgressManager:
    """步骤进度管理器"""

    def __init__(self, config):
        self.config = config
        self.task_states: Dict[str, TaskProgressState] = {}
        self.lock = threading.RLock()
        self._ensure_directory()

    def _ensure_directory(self):
        os.makedirs(os.path.dirname(self.config.progress_file), exist_ok=True)

    def create_task(self, task_id: str) -> bool:
        """创建任务"""
        with self.lock:
            if task_id in self.task_states:
                current_state = self.task_states[task_id]
                # 🆕 使用枚举比较
                if current_state.status == TaskStatus.RUNNING:
                    return False

            self.task_states[task_id] = TaskProgressState(task_id=task_id)
            logger.info(f"创建任务: {task_id}, 状态: {TaskStatus.PENDING.display_name}")
            return True

    def update_step_progress(self, task_id: str, step: EvaluationStep, progress: float, message: str = ""):
        """更新步骤进度"""
        with self.lock:
            if task_id not in self.task_states:
                logger.warning(f"任务 {task_id} 不存在，无法更新进度")
                return
            self.task_states[task_id].update_step_progress(step, progress, message)

    def complete_step(self, task_id: str, step: EvaluationStep, message: str = ""):
        """完成步骤"""
        with self.lock:
            if task_id not in self.task_states:
                logger.warning(f"任务 {task_id} 不存在，无法完成步骤")
                return
            self.task_states[task_id].complete_step(step, message)

    def complete_task(self, task_id: str, result: Optional[Dict] = None):
        """完成任务"""
        with self.lock:
            if task_id not in self.task_states:
                logger.warning(f"任务 {task_id} 不存在，无法标记完成")
                return

            state = self.task_states[task_id]
            state.mark_as_completed(result)
            logger.info(f"任务 {task_id} 已完成")

    def fail_task(self, task_id: str, error: str, error_info: Optional[Dict] = None):
        """任务失败"""
        with self.lock:
            if task_id not in self.task_states:
                logger.warning(f"任务 {task_id} 不存在，无法标记失败")
                return

            state = self.task_states[task_id]
            state.mark_as_failed(error, error_info)
            logger.error(f"任务 {task_id} 失败: {error}")

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        with self.lock:
            if task_id not in self.task_states:
                logger.warning(f"任务 {task_id} 不存在，无法取消")
                return False

            state = self.task_states[task_id]
            if not state.can_be_cancelled():
                logger.info(f"任务 {task_id} 状态为 {state.status.display_name}，无法取消")
                return False

            state.mark_as_cancelled()
            logger.info(f"任务 {task_id} 已被取消")
            return True

    def get_task_state(self, task_id: str) -> Optional[TaskProgressState]:
        """获取任务状态"""
        with self.lock:
            return self.task_states.get(task_id)

    def get_active_tasks(self) -> List[TaskProgressState]:
        """获取所有活跃任务"""
        with self.lock:
            return [state for state in self.task_states.values() if state.is_active()]

    def cleanup_finished_tasks(self, max_finished_tasks: int = 100) -> int:
        """清理已完成的任务，保留最近的一定数量"""
        with self.lock:
            finished_tasks = [
                (task_id, state) for task_id, state in self.task_states.items()
                if state.is_finished()
            ]

            if len(finished_tasks) <= max_finished_tasks:
                return 0

            # 按更新时间排序，保留最新的
            finished_tasks.sort(key=lambda x: x[1].updated_at, reverse=True)
            tasks_to_remove = finished_tasks[max_finished_tasks:]

            removed_count = 0
            for task_id, _ in tasks_to_remove:
                del self.task_states[task_id]
                removed_count += 1

            logger.info(f"清理了 {removed_count} 个已完成的任务")
            return removed_count
