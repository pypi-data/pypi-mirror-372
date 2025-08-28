import os
import threading
import json
import traceback
import pandas as pd
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable

from libentry.mcp import api
from libentry import logger

from evaluation_service_base.charts.dtypes import BaseChart
from evaluation_service_base.core.common import BaseEvaluationServiceConfig, EvaluationContext, \
    EvaluationServiceInputParams, EvaluationData, EvaluationResults, BaseEvaluationRaw, EvaluationSampleWithMetrics, \
    EvaluationResult
from evaluation_service_base.core.constants import ProgressConstants
from evaluation_service_base.core.enum import EvaluationStep, TaskStatus
from evaluation_service_base.core.exceptions import TaskCancelledException
from evaluation_service_base.core.managers import StepProgressManager
from evaluation_service_base.core.reporters import StepProgressReporter
from evaluation_service_base.utils.s3_handler import S3DataHandler


class BaseEvaluationService(ABC, S3DataHandler):
    """优化后的评估服务基类

    用户需要实现：
    1. 评估方法：evaluate_single_sample() 或 batch_evaluation()
    2. 统计方法：compute_overall_metrics() - 基于样本和指标计算整体统计
    3. 图表方法：generate_charts_from_overall_metrics() - 基于整体统计生成图表
    """

    def __init__(self, config: BaseEvaluationServiceConfig):
        super().__init__()
        self.config = config
        self.progress_manager = StepProgressManager(config)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """确保必要的目录存在"""
        directories = [self.config.result_dir, self.config.progress_log_dir]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    # ==================== 核心抽象方法 ====================

    def evaluate_single_sample(self, input_params: EvaluationServiceInputParams, sample: BaseEvaluationRaw) \
            -> Dict[str, Any]:
        """评估单个样本 (可选实现)

        Args:
            sample: 单个评估样本

        Returns:
            Dict[str, Any]: 该样本的评估指标字典
        """
        raise NotImplementedError(
            "必须实现 evaluate_single_sample() 或 batch_evaluation() 中的至少一个方法"
        )

    def batch_evaluation(self, input_params: EvaluationServiceInputParams, samples: List[BaseEvaluationRaw]) -> List[
        Dict[str, Any]]:
        """批量评估样本 (可选实现，优先使用)

        Args:
            samples: 样本列表

        Returns:
            List[Dict[str, Any]]: 每个样本对应的评估指标列表
        """
        # 默认实现：调用单样本评估
        return [self.evaluate_single_sample(input_params, sample) for sample in samples]

    @abstractmethod
    def compute_overall_metrics(
            self, samples_with_metrics: List[EvaluationSampleWithMetrics]
    ) -> Dict[str, Any]:
        """计算整体统计指标 (必须实现)

        Args:
            samples_with_metrics: 包含原始样本和对应指标的列表

        Returns:
            Dict[str, Any]: 整体统计指标

        示例:
            def compute_overall_metrics(self, context, samples_with_metrics, reporter):
                accuracies = [swm.metrics["accuracy"] for swm in samples_with_metrics]

                overall = {
                    "total_samples": len(samples_with_metrics),
                    "avg_accuracy": sum(accuracies) / len(accuracies),
                    "max_accuracy": max(accuracies),
                    "min_accuracy": min(accuracies),
                    "accuracy_distribution": self._compute_distribution(accuracies),
                    # 可以基于原始数据计算更复杂的统计
                    "avg_input_length": sum(len(str(swm.inputs)) for swm in samples_with_metrics) / len(samples_with_metrics)
                }

                return overall
        """
        pass

    @abstractmethod
    def generate_charts_from_overall_metrics(self, overall_metrics: Dict[str, Any]) -> List[BaseChart]:
        """基于整体统计指标生成图表 (必须实现)

        Args:
            overall_metrics: 整体统计指标

        Returns:
            List[BaseChart]: 生成的图表列表

        示例:
            def generate_charts_from_overall_metrics(self, overall_metrics):
                charts = []

                # 基于整体统计生成图表
                avg_accuracy = overall_metrics["avg_accuracy"]
                accuracy_dist = overall_metrics["accuracy_distribution"]

                # 生成准确率分布图
                dist_chart = create_distribution_chart(accuracy_dist)
                charts.append(dist_chart)

                # 生成概览图
                summary_chart = create_summary_chart({
                    "平均准确率": avg_accuracy,
                    "样本总数": overall_metrics["total_samples"]
                })
                charts.append(summary_chart)

                return charts
        """
        pass

    # ==================== 评估策略自动选择 ====================

    def _determine_evaluation_strategy(self) -> str:
        """智能确定评估策略"""
        has_custom_batch = self._has_custom_batch_evaluation()
        has_custom_single = self._has_custom_single_evaluation()

        if has_custom_batch:
            return "batch"
        elif has_custom_single:
            return "single"
        else:
            raise NotImplementedError(
                "必须实现 evaluate_single_sample() 或 batch_evaluation() 中的至少一个方法"
            )

    def _has_custom_batch_evaluation(self) -> bool:
        """检查是否实现了自定义批量评估"""
        return self.__class__.batch_evaluation != BaseEvaluationService.batch_evaluation

    def _has_custom_single_evaluation(self) -> bool:
        """检查是否实现了自定义单样本评估"""
        return self.__class__.evaluate_single_sample != BaseEvaluationService.evaluate_single_sample

    # ==================== 框架核心方法 ====================

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
                    logger.debug(f"已清理临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"清理文件失败: {file_path}, 错误: {e}")

    def _run_evaluation_pipeline(self, context: EvaluationContext, check_cancelled: Callable) -> Dict[str, Any]:
        """运行优化的评估管道"""
        # 数据加载
        input_data = self._execute_data_loading(context, check_cancelled)

        # 执行智能评估 - 返回样本和指标的组合
        samples_with_metrics = self._execute_smart_evaluation(context, input_data, check_cancelled)

        # 计算整体统计指标
        overall_metrics = self._execute_overall_metrics_computation(context, samples_with_metrics, check_cancelled)

        # 基于整体指标生成图表
        charts = self._execute_chart_generation_from_overall_metrics(context, overall_metrics, check_cancelled)

        # 构造评估结果用于保存
        evaluation_results = EvaluationResults(
            results=[
                EvaluationResult(metrics=swm.metrics, data_id=swm.data_id, outputs=swm.outputs)
                for swm in samples_with_metrics
            ]
        )

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

    def _execute_smart_evaluation(self, context: EvaluationContext, input_data: EvaluationData,
                                  check_cancelled: Callable) -> List[EvaluationSampleWithMetrics]:
        """执行智能评估步骤"""
        reporter = StepProgressReporter(self.progress_manager, context.task_id, EvaluationStep.EVALUATION)

        try:
            # 确定评估策略
            strategy = self._determine_evaluation_strategy()
            samples = input_data.data_list
            total_samples = len(samples)

            logger.info(f"总样本数: {total_samples}, 使用评估策略: {strategy}")
            reporter.update(0, f"开始执行评估 (策略: {strategy}, 样本数: {total_samples})")

            # 根据策略执行评估
            if strategy == "batch":
                all_metrics = self._run_batch_strategy(context.input_params, samples, reporter, check_cancelled)
            else:  # strategy == "single"
                all_metrics = self._run_single_strategy(context.input_params, samples, reporter, check_cancelled)

            # 组合原始样本和指标
            samples_with_metrics = [
                EvaluationSampleWithMetrics(sample, metrics)
                for sample, metrics in zip(samples, all_metrics)
            ]

            self.progress_manager.complete_step(context.task_id, EvaluationStep.EVALUATION)
            logger.info(f"评估完成，处理了 {len(samples_with_metrics)} 个样本")
            return samples_with_metrics

        except Exception as e:
            logger.error(f"评估执行失败: {e}")
            raise

    def _run_batch_strategy(
            self,
            input_params: EvaluationServiceInputParams,
            samples: List[BaseEvaluationRaw],
            reporter: StepProgressReporter,
            check_cancelled: Callable
    ) -> List[Dict[str, Any]]:
        """运行批量评估策略"""
        batch_size = getattr(self.config, 'batch_size', 100)
        all_metrics = []
        total_samples = len(samples)

        logger.info(f"使用批量评估策略，批量大小: {batch_size}")

        for i in range(0, total_samples, batch_size):
            check_cancelled()

            batch = samples[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_samples + batch_size - 1) // batch_size

            try:
                logger.debug(f"处理第 {batch_num}/{total_batches} 批，样本数: {len(batch)}")
                batch_metrics = self.batch_evaluation(input_params, batch)
                all_metrics.extend(batch_metrics)

                # 更新进度
                processed = min(i + len(batch), total_samples)
                progress = processed / total_samples * 100
                reporter.update(progress, f"批量处理进度 {processed}/{total_samples} ({batch_num}/{total_batches} 批)")

            except Exception as e:
                logger.error(f"批量评估第 {batch_num} 批失败: {e}")
                raise

        logger.info(f"批量评估完成，总计处理 {len(all_metrics)} 个样本")
        return all_metrics

    def _run_single_strategy(self, input_params: EvaluationServiceInputParams, samples: List[BaseEvaluationRaw],
                             reporter: StepProgressReporter,
                             check_cancelled: Callable) -> List[Dict[str, Any]]:
        """运行单样本评估策略"""
        all_metrics = []
        total_samples = len(samples)

        logger.info(f"使用单样本评估策略")

        for idx, sample in enumerate(samples):
            check_cancelled()

            try:
                metrics = self.evaluate_single_sample(input_params, sample)
                all_metrics.append(metrics)

                # 批量更新进度
                if idx % ProgressConstants.BATCH_UPDATE_SIZE == 0 or idx == total_samples - 1:
                    progress = (idx + 1) / total_samples * 100
                    reporter.update(progress, f"单样本处理进度 {idx + 1}/{total_samples}")

            except Exception as e:
                logger.error(f"单样本评估第 {idx + 1} 个样本失败 (data_id: {sample.data_id}): {e}")
                raise

        logger.info(f"单样本评估完成，总计处理 {len(all_metrics)} 个样本")
        return all_metrics

    def _execute_overall_metrics_computation(self, context: EvaluationContext,
                                             samples_with_metrics: List[EvaluationSampleWithMetrics],
                                             check_cancelled: Callable) -> Dict[str, Any]:
        """执行整体指标计算步骤"""
        reporter = StepProgressReporter(self.progress_manager, context.task_id, EvaluationStep.CHART_GENERATION)
        reporter.update(0, f"开始计算整体统计指标 (基于 {len(samples_with_metrics)} 个样本)")

        overall_metrics = self.compute_overall_metrics(samples_with_metrics)
        check_cancelled()

        logger.info(f"整体指标计算完成，指标数量: {len(list(overall_metrics.keys()))}")
        reporter.update(50, "整体统计指标计算完成")
        return overall_metrics

    def _execute_chart_generation_from_overall_metrics(self, context: EvaluationContext,
                                                       overall_metrics: Dict[str, Any],
                                                       check_cancelled: Callable) -> List[BaseChart]:
        """基于整体指标执行图表生成步骤"""
        reporter = StepProgressReporter(self.progress_manager, context.task_id, EvaluationStep.CHART_GENERATION)
        reporter.update(50, "开始基于整体指标生成图表")

        charts = self.generate_charts_from_overall_metrics(overall_metrics)
        check_cancelled()

        logger.info(f"图表生成完成，生成了 {len(charts)} 个图表")
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
        reporter.update(ProgressConstants.UPLOAD_S3_DETAIL, "上传详细结果到S3")
        self._put_detail_to_s3(detail_path, context.input_params.result_detail_path)
        check_cancelled()

        # 上传图表结果到S3
        reporter.update(ProgressConstants.UPLOAD_S3_CHARTS, "上传图表结果到S3")
        chart_data = [chart.dict() for chart in charts]
        self._put_json_to_s3(chart_data, context.input_params.result_metric_path)

        self.progress_manager.complete_step(context.task_id, EvaluationStep.RESULT_UPLOAD)

        return {
            "detail_s3_path": context.input_params.result_detail_path,
            "stat_s3_path": context.input_params.result_metric_path,
            "task_id": context.task_id
        }

    def load_input_data(self, context: EvaluationContext, reporter: StepProgressReporter) -> EvaluationData:
        """加载输入数据"""
        data_list = []
        chunk_count = 0

        try:
            for chunk_num, df in enumerate(self.read_hdf5_chunks_from_s3(context.input_params.input_path)):
                chunk_count += 1
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

                # 更新进度
                reporter.update(50, f"已加载 {chunk_count} 个数据块，共 {len(data_list)} 个样本")

            reporter.update(100, f"数据加载完成，总计 {len(data_list)} 个样本")
            logger.info(f"数据加载完成: {len(data_list)} 个样本，{chunk_count} 个数据块")

        except Exception as e:
            error_msg = f"数据加载失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            reporter.update(0, error_msg)
            raise

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

    @staticmethod
    def _convert_results_to_records(results: List[Any], reporter: StepProgressReporter) -> List[Dict]:
        """转换结果为记录列表"""
        records = []
        total_count = len(results)

        for idx, result in enumerate(results):
            try:
                record = result.model_dump() if hasattr(result, 'model_dump') else (
                    result.dict() if hasattr(result, 'dict') else result
                )
                records.append(record)
            except Exception as e:
                logger.warning(f"转换结果记录 {idx} 失败: {e}")
                # 使用原始数据
                records.append(result if isinstance(result, dict) else {"data": str(result)})

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

    # ==================== API 接口方法 ====================

    @api.post()
    def progress(self, task_id: str) -> Dict[str, Any]:
        """获取任务进度"""
        state = self.progress_manager.get_task_state(task_id)
        if not state:
            return {
                "progress": 0,
                "status": TaskStatus.PENDING.value,
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
                "status": TaskStatus.CANCELLED.value,
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
        """获取任务状态详情"""
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
