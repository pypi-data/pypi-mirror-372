#!/usr/bin/env python3
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class EvaluationServiceInputParams(BaseModel):
    task_id: str = Field(description="任务ID")
    input_path: str = Field(
        description="推理结果S3地址"
    )
    result_detail_path: str = Field(
        description="评估结果S3地址"
    )
    result_metric_path: str = Field(
        description="指标结果S3地址"
    )
    model_config = ConfigDict(extra="allow")


class BaseEvaluationServiceConfig(BaseModel):
    progress_log_dir: str = Field(default="./data/progress", description="进度日志目录")
    result_dir: str = Field(default="./data/results", description="评估结果本地目录")
    progress_file: str = Field(default="./data/results/task_progress.json", description="进度存储文件")
    batch_size: Optional[int] = Field(default=10, description="批量处理数据大小")


class BaseEvaluationRaw(BaseModel):
    data_id: int = Field(description="数据唯一ID")
    raw_data: Dict = Field(default_factory=dict, description="原始数据字典")
    inputs: Dict = Field(default_factory=dict, description="服务输入数据")
    outputs: Dict = Field(default_factory=dict, description="服务输出数据")


class EvaluationData(BaseModel):
    data_list: List[BaseEvaluationRaw] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    data_id: int = Field(description="数据唯一ID")
    metrics: Dict[str, float] = Field(default_factory=dict, description="单个结果的指标")
    outputs: Dict = Field(default_factory=dict, description="服务输出数据")


class EvaluationResults(BaseModel):
    results: List[EvaluationResult] = Field(default_factory=list)
    metrics: Dict = Field(default_factory=dict, description="性能指标")


class EvaluationSampleWithMetrics:
    """包含原始样本和评估指标的组合对象"""

    def __init__(self, sample: BaseEvaluationRaw, metrics: Dict[str, Any]):
        self.sample = sample
        self.metrics = metrics

    @property
    def data_id(self) -> int:
        return self.sample.data_id

    @property
    def raw_data(self) -> Dict[str, Any]:
        return self.sample.raw_data

    @property
    def inputs(self) -> Any:
        return self.sample.inputs

    @property
    def outputs(self) -> Any:
        return self.sample.outputs


class EvaluationContext(BaseModel):
    """评估上下文"""
    task_id: str = Field(description="任务ID")
    input_params: EvaluationServiceInputParams = Field(description="任务输入参数")
    temp_files: List[str] = Field(default_factory=list, description="临时文件列表")
    local_detail_path: Optional[str] = Field(default=None, description="本地详细结果路径")
    local_h5_detail_path: Optional[str] = Field(default=None, description="本地详细结果路径")

    def add_temp_file(self, file_path: str) -> None:
        """添加临时文件路径"""
        if file_path not in self.temp_files:
            self.temp_files.append(file_path)

    def set_local_detail_path(self, path: str) -> None:
        """设置本地详细结果路径"""
        self.local_detail_path = path
        self.add_temp_file(path)

    def set_local_h5_detail_path(self, path: str) -> None:
        """设置本地HDF5详细结果路径"""
        self.local_h5_detail_path = path
        self.add_temp_file(path)

    class Config:
        # 允许任意类型，因为我们有自定义方法
        arbitrary_types_allowed = True
        # 使用枚举值而不是名称
        use_enum_values = True
