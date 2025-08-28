from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

# ==================== 图表基础模型 ====================

class BaseChart(BaseModel):
    """图表基础模型"""
    chart_type: str = Field(description="图表类型标识")
    title: str = Field(description="图表标题")
    subtitle: Optional[str] = Field(default=None, description="副标题")
    description: Optional[str] = Field(default=None, description="图表说明/解读")
    id: Optional[str] = Field(default=None, description="图表唯一标识（可用于前端定位/锚点）")


class RadarChart(BaseChart):
    """雷达图模型"""
    chart_type: str = Field(default="radar", description="图表类型：雷达图")
    metrics: List[str] = Field(description="指标名称列表")
    legend: List[str] = Field(description="图例")
    data: List[Dict[str, Any]] = Field(description="数据，格式：[{name: '系列名', value: [数值列表]}]")
    max_values: List[float] = Field(default=None, description="每个指标的最大值，默认为100")

    # 前端渲染参数
    grid_lines: bool = Field(default=True, description="是否显示网格线")
    fill_area: bool = Field(default=True, description="是否填充区域")

    def __init__(self, **data):
        if data.get('max_values') is None:
            data['max_values'] = [100.0] * len(data.get('metrics', []))
        super().__init__(**data)


class BarChart(BaseChart):
    chart_type: str = Field(default="bar", description="图表类型：分组柱状图")
    categories: List[str] = Field(description="X轴类别名称（主分组）")
    legend: List[str] = Field(description="图例（子分组）")
    data: List[Dict[str, Any]] = Field(description="数据，格式：[{name: '图例名', values: [各类别数值]}]")
    y_axis_label: Optional[str] = Field(None, description="Y轴标签")
    x_axis_label: Optional[str] = Field(None, description="X轴标签")

    orientation: str = Field(default="vertical", description="方向：vertical(垂直) 或 horizontal(水平)")
    stacked: bool = Field(default=False, description="是否堆叠显示")
    show_values: bool = Field(default=True, description="是否显示数值标签")


class LineChart(BaseChart):
    """线图模型"""
    chart_type: str = Field(default="line", description="图表类型：线图")
    x_axis: List[str] = Field(description="X轴数据")
    legend: List[str] = Field(description="图例")
    data: List[Dict[str, Any]] = Field(description="数据，格式：[{name: '系列名', values: [数值列表]}]")
    y_axis_label: Optional[str] = Field(None, description="Y轴标签")
    x_axis_label: Optional[str] = Field(None, description="X轴标签")

    # 前端渲染参数
    smooth: bool = Field(default=True, description="是否平滑曲线")
    show_points: bool = Field(default=True, description="是否显示数据点")
    fill_area: bool = Field(default=False, description="是否填充区域")
    area_opacity: float = Field(default=0.25, description="面积填充透明度，0-1")


class TableChart(BaseChart):
    """表格模型"""
    chart_type: str = Field(default="table", description="图表类型：表格")
    columns:  List[Dict]= Field(description="列定义，格式：[{key: '字段名', label: '显示名', width?: '宽度'}]")
    data: List[Dict[str, Any]] = Field(description="表格数据")



class GaugeChart(BaseChart):
    """仪表盘模型"""
    chart_type: str = Field(default="gauge", description="图表类型：仪表盘")
    metrics: List[Dict[str, Any]] = Field(
        description="指标数据，格式：[{name: '指标名', value: 数值, max: 最大值, unit?: '单位'}]")

    # 前端渲染参数
    show_pointer: bool = Field(default=True, description="是否显示指针")
    color_ranges: Optional[List[Dict[str, Any]]] = Field(default=None, description="颜色范围设置")
    start_angle: Optional[int] = Field(default=None, description="起始角度")
    end_angle: Optional[int] = Field(default=None, description="结束角度")


class ScatterChart(BaseChart):
    """散点图模型"""
    chart_type: str = Field(default="scatter", description="图表类型：散点图")
    x_axis_label: str = Field(description="X轴标签")
    y_axis_label: str = Field(description="Y轴标签")
    legend: List[str] = Field(description="图例")
    data: List[Dict[str, Any]] = Field(
        description="数据，格式：[{name: '系列名', points: [{x: x值, y: y值, size?: 大小}]}]")

    # 前端渲染参数
    show_regression_line: bool = Field(default=False, description="是否显示回归线")
    point_size: int = Field(default=8, description="数据点大小")
    x_log: bool = Field(default=False, description="X轴对数刻度")
    y_log: bool = Field(default=False, description="Y轴对数刻度")


class PieChart(BaseChart):
    """饼图模型"""
    chart_type: str = Field(default="pie", description="图表类型：饼图")
    data: List[Dict[str, Any]] = Field(description="数据，格式：[{name: '名称', value: 数值, color?: '颜色'}]")

    # 前端渲染参数
    show_legend: bool = Field(default=True, description="是否显示图例")
    show_labels: bool = Field(default=True, description="是否显示标签")
    show_percentages: bool = Field(default=True, description="是否显示百分比")
    donut_mode: bool = Field(default=False, description="是否为环形图")
    inner_radius: Optional[float] = Field(default=None, description="环形图内半径比例 0-1")
    rose_type: Optional[str] = Field(default=None, description="南丁格尔图类型: area/radius")


class HeatmapChart(BaseChart):
    """热力图模型"""
    chart_type: str = Field(default="heatmap", description="图表类型：热力图")
    x_axis: List[str] = Field(description="X轴标签")
    y_axis: List[str] = Field(description="Y轴标签")
    data: List[List[float]] = Field(description="数据矩阵")

    # 前端渲染参数
    color_scheme: str = Field(default="viridis", description="颜色方案")
    show_values: bool = Field(default=True, description="是否显示数值")
    value_format: Optional[str] = Field(default=None, description="数值格式，如 '0.0%' or '.2f'")


# ==================== 新增图表类型 ====================

class AreaChart(BaseChart):
    """堆叠面积图/面积图"""
    chart_type: str = Field(default="area", description="图表类型：面积图")
    x_axis: List[str] = Field(description="X轴数据")
    legend: List[str] = Field(description="图例")
    data: List[Dict[str, Any]] = Field(description="数据，格式：[{name: '系列名', values: [数值列表]}]")
    y_axis_label: Optional[str] = Field(None, description="Y轴标签")
    x_axis_label: Optional[str] = Field(None, description="X轴标签")
    stacked: bool = Field(default=True, description="是否堆叠")
    area_opacity: float = Field(default=0.25, description="面积透明度")


class WaterfallChart(BaseChart):
    """瀑布图，用于展示增减变化"""
    chart_type: str = Field(default="waterfall", description="图表类型：瀑布图")
    categories: List[str] = Field(description="类别/阶段名称")
    values: List[float] = Field(description="对应数值，正负表示增减")
    total_label: Optional[str] = Field(default="总计", description="总计标签")


class BoxplotChart(BaseChart):
    """箱线图，用于展示分布"""
    chart_type: str = Field(default="boxplot", description="图表类型：箱线图")
    categories: List[str] = Field(description="类别名称")
    data: List[Dict[str, Any]] = Field(description="数据: [{name: 类别, values: [min, q1, median, q3, max], outliers?: [[x,y], ...]}]")
    y_axis_label: Optional[str] = Field(default=None, description="Y轴标签")


class HistogramChart(BaseChart):
    """直方图"""
    chart_type: str = Field(default="histogram", description="图表类型：直方图")
    bins: List[str] = Field(description="区间标签，如 '0-10', '10-20'")
    counts: List[int] = Field(description="每个区间的数量")
    density: bool = Field(default=False, description="是否显示概率密度")


class SankeyChart(BaseChart):
    """桑基图，展示流向关系"""
    chart_type: str = Field(default="sankey", description="图表类型：桑基图")
    nodes: List[Dict[str, Any]] = Field(description="节点列表，如 [{name: 'A'}, {name: 'B'}]")
    links: List[Dict[str, Any]] = Field(description="边列表，如 [{source: 0, target: 1, value: 10}]")


class TimelineChart(BaseChart):
    """时间轴/甘特图"""
    chart_type: str = Field(default="timeline", description="图表类型：时间轴/甘特图")
    items: List[Dict[str, Any]] = Field(description="条目: [{label, start, end, group?, color?}]")
    groups: Optional[List[str]] = Field(default=None, description="分组，可选")


class KPICardChart(BaseChart):
    """KPI卡片，用于展示核心指标数值"""
    chart_type: str = Field(default="kpi_card", description="图表类型：KPI卡片")
    items: List[Dict[str, Any]] = Field(description="KPI列表: [{label, value, unit?, delta?, trend?}]")


# ==================== 图表工厂类 ====================

class ChartFactory:
    """图表工厂类，用于创建不同类型的图表"""

    CHART_TYPES = {
        "radar": RadarChart,
        "bar": BarChart,
        "line": LineChart,
        "table": TableChart,
        "gauge": GaugeChart,
        "scatter": ScatterChart,
        "pie": PieChart,
        "heatmap": HeatmapChart,
        "area": AreaChart,
        "waterfall": WaterfallChart,
        "boxplot": BoxplotChart,
        "histogram": HistogramChart,
        "sankey": SankeyChart,
        "timeline": TimelineChart,
        "kpi_card": KPICardChart
    }

    @classmethod
    def create_chart(cls, chart_type: str, **kwargs) -> BaseChart:
        """根据类型创建图表"""
        if chart_type not in cls.CHART_TYPES:
            raise ValueError(f"不支持的图表类型: {chart_type}")

        chart_class = cls.CHART_TYPES[chart_type]
        return chart_class(**kwargs)

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """获取支持的图表类型"""
        return list(cls.CHART_TYPES.keys())
