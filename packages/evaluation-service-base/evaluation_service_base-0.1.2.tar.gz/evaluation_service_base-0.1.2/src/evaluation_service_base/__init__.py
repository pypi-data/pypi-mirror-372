"""
Evaluation Service Base Framework

A comprehensive framework for building evaluation services with:
- Progress tracking and task management
- Flexible evaluation data handling
- S3/MinIO storage integration
- Rich chart and reporting capabilities
- Extensible base service architecture

"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core modules
from .core.base_service import BaseEvaluationService
from .core.exceptions import TaskCancelledException
from .core.common import (
    BaseEvaluationServiceConfig,
    EvaluationServiceInputParams,
    EvaluationContext,
    EvaluationData,
    EvaluationResult,
    EvaluationResults,
    BaseEvaluationRaw,
)
from .core.enum import TaskStatus, EvaluationStep
from .core.constants import ProgressConstants
from .core.models import TaskProgressState
from .core.managers import StepProgressManager
from .core.reporters import StepProgressReporter

# Utils modules
from .utils.minio_client import MinioClient, MinioConfig
from .utils.s3_handler import S3DataHandler

# Charts modules
from .charts.dtypes import (
    BaseChart, RadarChart, BarChart, LineChart, TableChart,
    GaugeChart, ScatterChart, PieChart, HeatmapChart,
    AreaChart, WaterfallChart, BoxplotChart, HistogramChart,
    SankeyChart, TimelineChart, KPICardChart, ChartFactory
)

__all__ = [
    # Core
    "BaseEvaluationService",
    "TaskCancelledException",
    "BaseEvaluationServiceConfig",
    "EvaluationServiceInputParams",
    "EvaluationContext",
    "EvaluationData",
    "EvaluationResult",
    "EvaluationResults",
    "BaseEvaluationRaw",
    "TaskStatus",
    "EvaluationStep",
    "ProgressConstants",
    "TaskProgressState",
    "StepProgressManager",
    "StepProgressReporter",

    # Utils
    "MinioClient",
    "MinioConfig",
    "S3DataHandler",

    # Charts
    "BaseChart",
    "RadarChart",
    "BarChart",
    "LineChart",
    "TableChart",
    "GaugeChart",
    "ScatterChart",
    "PieChart",
    "HeatmapChart",
    "AreaChart",
    "WaterfallChart",
    "BoxplotChart",
    "HistogramChart",
    "SankeyChart",
    "TimelineChart",
    "KPICardChart",
    "ChartFactory",
]