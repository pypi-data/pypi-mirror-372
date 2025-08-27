import os
import threading
import json
import traceback
import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional

from libentry.mcp import api
from libentry import logger

from evaluation_service_base.charts.dtypes import BaseChart
from evaluation_service_base.core.common import BaseEvaluationServiceConfig, EvaluationContext, \
    EvaluationServiceInputParams, EvaluationData, EvaluationResults, BaseEvaluationRaw
from evaluation_service_base.core.constants import ProgressConstants
from evaluation_service_base.core.enum import EvaluationStep, TaskStatus
from evaluation_service_base.core.exceptions import TaskCancelledException
from evaluation_service_base.core.managers import StepProgressManager
from evaluation_service_base.core.reporters import StepProgressReporter
from evaluation_service_base.utils.minio_client import MinioClient, MinioConfig
from evaluation_service_base.utils.s3_handler import S3DataHandler


class BaseEvaluationService(ABC, S3DataHandler):
    """评估服务基类"""

    def __init__(self, config: BaseEvaluationServiceConfig, minio_config: MinioConfig):
        self.config = config
        self.minio_client = MinioClient(minio_config)
        super().__init__(self.minio_client)
        self.progress_manager = StepProgressManager(config)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        directories = [self.config.result_dir, self.config.progress_log_dir]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def _setup_evaluation_context(self, task_id: str, input_params: EvaluationServiceInputParams) -> EvaluationContext:
        """设置评估上下文"""
        context = EvaluationContext(task_id=task_id, input_params=input_params)
        self._setup_local_detail_path(context)
        return context

    def _setup_local_detail_path(self, context: EvaluationContext):
        """设置本地详细结果路径"""
        os.makedirs(self.config.result_dir, exist_ok=True)

        base_filename = f"{context.task_id}_detail"
        json_path = f"{self.config.result_dir}/{base_filename}.json"
        h5_path = f"{self.config.result_dir}/{base_filename}.h5"

        context.set_local_detail_path(json_path)
        context.set_local_h5_detail_path(h5_path)

        logger.info(f"设置本地详细结果路径: {json_path}")
        return

    @api.post()
    def evaluate(self, input_param: EvaluationServiceInputParams) -> Dict[str, Any]:
        """启动评估任务"""
        task_id = input_param.task_id

        if not self.progress_manager.create_task(task_id):
            return self._create_response("already_running", "任务已在运行", task_id)

        threading.Thread(
            target=self._execute_evaluation,
            args=(task_id, input_param),
            daemon=True,
            name=f"eval-{task_id}"
        ).start()

        return self._create_response("started", "任务已启动", task_id)

    def _create_response(self, status: str, message: str, task_id: str) -> Dict[str, Any]:
        """创建统一的响应格式"""
        return {
            "status": status,
            "message": message,
            "task_id": task_id
        }

    def _execute_evaluation(self, task_id: str, input_param: EvaluationServiceInputParams) -> None:
        """执行评估流水线"""
        context = self._setup_evaluation_context(task_id, input_param)

        try:
            cancellation_checker = self._create_cancellation_checker(task_id)
            result = self._run_evaluation_pipeline(context, cancellation_checker)
            self.progress_manager.complete_task(task_id, result)

        except TaskCancelledException:
            logger.info(f"任务 {task_id} 已被取消")
        except Exception as e:
            self._handle_evaluation_error(task_id, e)
        finally:
            self._cleanup_files(context.temp_files)

    def _create_cancellation_checker(self, task_id: str) -> Callable[[], None]:
        """创建取消检查函数"""

        def check_cancelled():
            state = self.progress_manager.get_task_state(task_id)
            if state and state.cancelled:
                raise TaskCancelledException()

        return check_cancelled

    def _handle_evaluation_error(self, task_id: str, error: Exception) -> None:
        """处理评估错误"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }
        self.progress_manager.fail_task(task_id, str(error), error_info)
        logger.error(f"任务 {task_id} 失败: {error}", exc_info=True)

    def _cleanup_files(self, file_paths: List[str]):
        """清理临时文件"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"清理文件失败: {file_path}, 错误: {e}")

    def _run_evaluation_pipeline(self, context: EvaluationContext, check_cancelled: Callable) -> Dict[str, Any]:
        """运行评估管道"""
        # 数据加载
        input_data = self._execute_data_loading(context, check_cancelled)

        # 执行评估
        evaluation_results = self._execute_evaluation_step(context, input_data, check_cancelled)

        # 生成图表
        charts = self._execute_chart_generation(context, evaluation_results, check_cancelled)

        # 上传结果
        return self._execute_result_upload(context, evaluation_results, charts, check_cancelled)

    def _execute_data_loading(self, context: EvaluationContext, check_cancelled: Callable) -> EvaluationData:
        """执行数据加载步骤"""
        reporter = StepProgressReporter(self.progress_manager, context.task_id, EvaluationStep.DATA_LOADING)
        reporter.update(0, "开始数据加载")

        input_data = self.load_input_data(context, reporter)
        check_cancelled()

        self.progress_manager.complete_step(context.task_id, EvaluationStep.DATA_LOADING)
        return input_data

    def _execute_evaluation_step(self, context: EvaluationContext, input_data: EvaluationData,
                                 check_cancelled: Callable) -> EvaluationResults:
        """执行评估步骤"""
        reporter = StepProgressReporter(self.progress_manager, context.task_id, EvaluationStep.EVALUATION)
        reporter.update(0, "开始执行评估")

        results = self.run_evaluation(context, input_data, reporter, check_cancelled)
        self.progress_manager.complete_step(context.task_id, EvaluationStep.EVALUATION)
        return results

    def _execute_chart_generation(self, context: EvaluationContext, results: EvaluationResults,
                                  check_cancelled: Callable) -> List[BaseChart]:
        """执行图表生成步骤"""
        reporter = StepProgressReporter(self.progress_manager, context.task_id, EvaluationStep.CHART_GENERATION)
        reporter.update(0, "开始生成图表")

        charts = self.generate_charts(context, results, reporter)
        check_cancelled()

        self.progress_manager.complete_step(context.task_id, EvaluationStep.CHART_GENERATION)
        return charts

    def _execute_result_upload(self, context: EvaluationContext, results: EvaluationResults,
                               charts: List[BaseChart], check_cancelled: Callable) -> Dict[str, Any]:
        """执行结果上传步骤"""
        reporter = StepProgressReporter(self.progress_manager, context.task_id, EvaluationStep.RESULT_UPLOAD)
        reporter.update(0, "开始上传结果")

        # 保存详细结果
        reporter.update(ProgressConstants.UPLOAD_SAVE_DETAIL, "保存详细结果")
        detail_path = self.save_detail_results(context, results, reporter)
        context.add_temp_file(detail_path)
        check_cancelled()

        # 上传详细结果到S3
        reporter.update(ProgressConstants.UPLOAD_S3_DETAIL, "上传详细结果")
        self._put_detail_to_s3(detail_path, context.input_params.result_detail_path)
        check_cancelled()

        # 上传图表结果到S3
        reporter.update(ProgressConstants.UPLOAD_S3_CHARTS, "上传图表结果")
        chart_data = [chart.dict() for chart in charts]
        self._put_json_to_s3(chart_data, context.input_params.result_metric_path)

        self.progress_manager.complete_step(context.task_id, EvaluationStep.RESULT_UPLOAD)

        return {
            "detail_s3_path": context.input_params.result_detail_path,
            "stat_s3_path": context.input_params.result_metric_path,
            "task_id": context.task_id
        }

    def load_input_data(self, context: EvaluationContext, reporter: StepProgressReporter) -> EvaluationData:
        data_list = []

        for chunk_num, df in enumerate(self.read_hdf5_chunks_from_s3(context.input_params.input_path)):
            chunk_list = [
                BaseEvaluationRaw(
                    data_id=row['data_id'],
                    raw_data=json.loads(json.loads(row['_RawData_'])),
                    inputs=json.loads(json.loads(row['inputs'])).get('inputs'),
                    outputs=json.loads(json.loads(row['outputs']))
                )
                for _, row in df.iterrows()
            ]
            data_list.extend(chunk_list)

        return EvaluationData(data_list=data_list)

    def save_detail_results(self, context: EvaluationContext, results: EvaluationResults,
                            reporter: StepProgressReporter) -> str:
        """保存详细评估结果到H5文件"""
        try:
            reporter.update(0, "开始保存详细结果")

            # 确保路径已设置
            if not context.local_detail_path:
                self._setup_local_detail_path(context)

            # 转换数据
            results_data = self._convert_results_to_records(results.results, reporter)

            # 保存到H5文件
            h5_path = self._save_results_to_h5(results_data, context, reporter)

            reporter.update(100, f"详细结果已保存到: {h5_path}")
            logger.info(f"详细结果保存完成: {h5_path}, 记录数: {len(results.results)}")

            return h5_path

        except Exception as e:
            error_msg = f"保存详细结果失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            reporter.update(0, error_msg)
            raise

    def _convert_results_to_records(self, results: List[Any], reporter: StepProgressReporter) -> List[Dict]:
        """转换结果为记录列表"""
        records = []
        total_count = len(results)

        for idx, result in enumerate(results):
            record = result.model_dump() if hasattr(result, 'model_dump') else result.dict()
            records.append(record)

            # 批量更新进度
            if idx % ProgressConstants.BATCH_UPDATE_SIZE == 0:
                progress = (idx / total_count) * 70  # 70%用于数据转换
                reporter.update(progress, f"处理数据 {idx}/{total_count}")

        reporter.update(70, "数据转换完成")
        return records

    def _save_results_to_h5(self, records: List[Dict], context: EvaluationContext,
                            reporter: StepProgressReporter) -> str:
        """保存记录到H5文件"""
        reporter.update(75, "创建DataFrame")
        df = pd.DataFrame(records)

        reporter.update(85, "保存到H5文件")
        h5_path = context.local_h5_detail_path
        self.append_to_hdf5(df, h5_path, key='df')

        return h5_path

    @api.post()
    def progress(self, task_id: str) -> Dict[str, Any]:
        """获取任务进度"""
        state = self.progress_manager.get_task_state(task_id)
        if not state:
            return {
                "progress": 0,
                "status": TaskStatus.PENDING.value,  # 🆕 使用枚举值
                "status_display": "任务不存在",
                "message": "任务不存在"
            }

        result = state.to_dict()

        # 根据状态添加额外信息
        if state.status == TaskStatus.COMPLETED and state.result:
            result["result"] = state.result
        elif state.status == TaskStatus.FAILED and state.error_info:
            result["error_detail"] = state.error_info

        return result

    @api.post()
    def cancel(self, task_id: str) -> Dict[str, Any]:
        """取消任务"""
        state = self.progress_manager.get_task_state(task_id)

        if not state:
            return {
                "status": "not_found",
                "message": "任务不存在",
                "task_id": task_id
            }

        if self.progress_manager.cancel_task(task_id):
            return {
                "status": TaskStatus.CANCELLED.value,  # 🆕 使用枚举值
                "message": "任务已成功取消",
                "task_id": task_id
            }

        # 检查当前状态
        current_status = state.status
        if current_status == TaskStatus.CANCELLED:
            return {
                "status": "already_cancelled",
                "message": f"任务已经被取消 (状态: {current_status.display_name})",
                "task_id": task_id
            }
        elif current_status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return {
                "status": "cannot_cancel",
                "message": f"任务已结束，无法取消 (状态: {current_status.display_name})",
                "task_id": task_id
            }
        else:
            return {
                "status": "not_running",
                "message": f"任务未在运行中 (状态: {current_status.display_name})",
                "task_id": task_id
            }

    @api.post()
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """🆕 获取任务状态详情（新增接口）"""
        state = self.progress_manager.get_task_state(task_id)
        if not state:
            return {"error": "任务不存在"}

        return {
            "task_id": task_id,
            "status": {
                "value": state.status.value,
                "display_name": state.status.display_name,
                "is_active": state.is_active(),
                "is_finished": state.is_finished(),
                "can_be_cancelled": state.can_be_cancelled()
            },
            "progress": state.overall_progress,
            "message": state.message,
            "created_at": state.created_at.isoformat(),
            "updated_at": state.updated_at.isoformat()
        }

    @abstractmethod
    def run_evaluation(self, context: EvaluationContext, data: EvaluationData,
                       reporter: StepProgressReporter, check_cancelled: Callable) -> EvaluationResults:
        """执行评估 - 子类通过reporter.update(progress, message)更新进度"""
        pass

    @abstractmethod
    def generate_charts(self, context: EvaluationContext, result: Any, reporter: StepProgressReporter) -> List[
        BaseChart]:
        """生成图表 - 子类通过reporter.update(progress, message)更新进度"""
        pass
