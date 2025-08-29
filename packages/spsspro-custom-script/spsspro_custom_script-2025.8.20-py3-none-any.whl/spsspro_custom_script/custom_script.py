from __future__ import unicode_literals

import base64
import io
from typing import Union, List, Optional, Any, Set, Type

import cloudpickle
import numpy as np
from matplotlib.figure import Figure
from pandas import DataFrame, Series
from pydantic import validator, Field
from rdkit import Chem

from spsspro_custom_script.custom_script_extra import NotebookViewExtra
from spsspro_custom_script.value_objects import BaseEnum, BaseValueObject


# copy from seal-algorithm
# from seal_algorithm.render.render.pro_drawing.draw_v2 import box_line_diagram, quantile_data
def quantile_data(data, quartile):
    """
    spss分位数公式
    """
    try:
        data = sorted(data)
        num = len(data)
        ly = (num + 1) * quartile
        ly_int, ly_decimal = int(ly), ly - int(ly)

        return data[ly_int - 1] + (data[ly_int] - data[ly_int - 1]) * ly_decimal
    except Exception:
        return np.quantile(data, quartile)


def box_line_diagram(data_x: Series, name: str = None):
    data_x = data_x.dropna().reset_index(drop=True)

    Q3 = quantile_data(data_x, quartile=0.75)
    Q2 = data_x.quantile(q=0.50)
    Q1 = quantile_data(data_x, quartile=0.25)

    IQR = Q3 - Q1

    upper_edge = Q3 + 1.5 * IQR
    lower_edge = Q1 - 1.5 * IQR
    outliers = data_x[(data_x < lower_edge) | (data_x > upper_edge)].tolist()

    if name is None:
        name = data_x.name

    dict_ = {
        "name": data_x.name,
        "column": name,
        "max_data": upper_edge,
        "min_data": lower_edge,
        "data_q3": Q3,
        "data_q2": Q2,
        "data_q1": Q1,
        "outliers": outliers
    }

    return dict_


class CustomScriptType(BaseEnum):
    data_process = 1
    data_analysis = 2
    data_analysis_predict = 3

    @property
    def cn_name(self) -> str:
        """中文名
        """
        return {
            1: '数据处理',
            2: '数据分析',
            3: '预测模型',
        }[self.value]

    @property
    def algorithm_id(self):
        """自定义算法的算法ID

        1-数据处理；2-数据分析；
        """
        # from seal.seedwork.domain.value_objects import AnalysisAlgorithm, ProcessingAlgorithm
        mapping = {
            self.data_process: 99,
            self.data_analysis: 999,
        }
        if self == self.data_process:
            # return ProcessingAlgorithm.custom_script.algo_id
            return mapping[self.data_process]
        if self == self.data_analysis:
            # return AnalysisAlgorithm.custom_algorithm.algo_id
            return mapping[self.data_analysis]


class ReportElement(BaseValueObject):
    font_size: int = 12
    name: Optional[str] = None
    description: Optional[str] = None
    _supported_elements: Set[Type["ReportElement"]] = set()

    def __init_subclass__(cls, **kwargs):
        ReportElement._supported_elements.add(cls)  # type: ignore

    def to_dict(self):
        d = super().to_dict()
        for k, v in d.items():
            if isinstance(v, list):
                d_k_list = []
                for vv in v:
                    if isinstance(vv, str):
                        d_k_list.append(vv)
                    else:
                        d_k_list.append(
                            {
                                'name': vv.name,
                                'data': vv.tolist()
                            }
                        )
                d[k] = d_k_list
            elif isinstance(v, Series):
                d[k] = {
                    'name': v.name,
                    'data': v.tolist()
                }
            elif isinstance(v, DataFrame):
                d[k] = list(zip(*[[k] + list(v.values()) for k, v in v.to_dict().items()]))
        return d


class ScatterPlot(ReportElement):
    """
    散点图
    x:x坐标 type:Series
    y:y坐标 type:Series
    group:分组坐标 type:Series
    txt_label:标签名称默认为空 Series
    """
    x: Series
    y: Series
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    group: Optional[Series] = None
    txt_label: Optional[Series] = None


class QuadrantPlot(ReportElement):
    """
    象限图
    x:x坐标 type:Series
    y:y坐标 type:Series
    txt_label:标签名称默认为空 Series
    """
    x: Series
    y: Series
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    txt_label: Optional[Series] = None


class XYLinePlot(ReportElement):
    """
    xy折线图
    x:x坐标
    y:y坐标
    txt_label:txt_label
    """
    x: Series
    y: Series
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    txt_label: Optional[Series] = None


class XYPlots(ReportElement):
    """
    基于XY坐标的组合图

    elements:绘制其他组件
    """
    elements: List[Any]

    x_label: Optional[str] = None
    y_label: Optional[str] = None

    @validator('elements')
    def validate_elements_property(cls, elements):
        for element in elements:
            if not isinstance(element, (XYLinePlot, ScatterPlot)):
                raise TypeError("elements List的属性必须是XYLinePlot和ScatterPlot")
        return elements

    def to_dict(self):
        return {
            'name': self.name,
            'font_size': self.font_size,
            'description': self.description,
            'x_label': self.x_label,
            'y_label': self.y_label,
            'elements': [{'type': element.__class__.__name__, 'data': element.to_dict()} for element in self.elements]
        }


class SubPlots(ReportElement):
    """
    subplot子图

    shape：是多个图的形状，【3，4】就是三行四列,最多可以画3×4=12个图
    elements：是之前用其它组件绘制的图，按行的顺序一个一个排列下去，不能超过size=3*4=12个图，不然就忽略超过size的图
    subname：是子图的名称（可不填）展现在子图的正上方
    全部都不填的时候就None（默认值）

    """
    shape: List[int]
    elements: List[Any]
    subname: Optional[List[str]] = None

    @validator('elements')
    def validate_elements_property(cls, elements):
        for element in elements:
            if not isinstance(element, ReportElement):
                raise TypeError("elements List的属性必须是组件")

        return elements

    @validator('shape')
    def validate_shape_property(cls, shape):
        if len(shape) != 2:
            raise ValueError("shape 必须是[int,int]")
        if shape[0] <= 0:
            raise ValueError("shape 数值必须是正整数")
        if shape[1] <= 0:
            raise ValueError("shape 数值必须是正整数")

        return shape

    def to_dict(self):
        return {
            'subname': self.subname,
            'shape': self.shape,
            'name': self.name,
            'font_size': self.font_size,
            'description': self.description,
            'elements': [{'type': element.__class__.__name__, 'data': element.to_dict()} for element in self.elements]
        }


class OverlapXYPlot(ReportElement):
    """
    叠图（纵向叠图）

    x:x坐标
    y:y坐标
    scatter:bool 默认为 False
    """
    x: Series
    y: Union[Series, List[Series]]

    x_label: Optional[str] = None
    y_label: Optional[Union[str, List[str]]] = None

    subname: Optional[List[str]] = None
    scatter: bool = False

    def to_dict(self):
        d = super().to_dict()
        if not isinstance(d['y'], list):
            d['y'] = [d['y']]

        if not isinstance(d['y_label'], list):
            d['y_label'] = [d['y_label']]

        return d


class BoxPlot(ReportElement):
    """
    箱线图
    """
    x: Union[Series, List[Series]]
    x_label: Optional[str] = None
    y_label: Optional[str] = None

    def to_dict(self):
        series_list = self.x if isinstance(self.x, list) else [self.x]
        return {
            'name': self.name,
            'font_size': self.font_size,
            'description': self.description,
            'data': [box_line_diagram(series) for series in series_list],
            'x_label': self.x_label,
            'y_label': self.y_label
        }


class LinePlot(ReportElement):
    """
    折线图
    """
    index: Series
    y: Union[Series, List[Series]]

    x_label: Optional[str] = None
    y_label: Optional[str] = None

    def to_dict(self):
        d = super().to_dict()
        if not isinstance(d['y'], list):
            d['y'] = [d['y']]
        return d


class BarPlot(ReportElement):
    """
    柱状图
    """
    x: Series
    y: Union[Series, List[Series]]

    x_label: Optional[str] = None
    y_label: Optional[str] = None

    data_labels: bool = True
    type: str = "axis0"  # 其中axis0为默认，横向柱状图，axis1为竖向柱状图
    percent: bool = False  # 是否为百分比数值
    percent_label: bool = False  # 是否为带百分比标签

    def to_dict(self):
        d = super().to_dict()
        if not isinstance(d['y'], list):
            d['y'] = [d['y']]
        return d


class PieChart(ReportElement):
    """
    饼状图
    x:分组名
    y:数值
    name:标题名
    description：文本说明
    """
    x: Series
    y: Optional[Series] = None
    data_labels: bool = True
    percent: bool = True  # 是否为百分比数值
    percent_label: bool = False  # 是否为带百分比标签

    def to_dict(self):
        if self.y is None:
            x_count = self.x.value_counts()
            self.x = Series(data=x_count.index, name=self.x.name)
            self.y = Series(data=x_count.values, name=str(self.x.name) + "_频数")
        d = super().to_dict()
        return d


class CloudWord(ReportElement):
    """
    词云图
    x:分组名
    y:频数数值
    name:标题名
    description：文本说明
    """
    x: Series
    y: Optional[Series] = None

    def to_dict(self):
        if self.y is None:
            x_count = self.x.value_counts()
            self.x = Series(data=x_count.index, name=self.x.name)
            self.y = Series(data=x_count.values, name=str(self.x.name) + "_频数")
        d = super().to_dict()
        return d


class StackColumnChart(ReportElement):
    """
    堆叠柱状图
    x:分组名
    y:List<数值>
    name:标题名
    description：文本说明
    """
    x: Series
    y: Union[Series, List[Series]]

    x_label: Optional[str] = None
    y_label: Optional[str] = None

    data_labels: bool = True
    percent: bool = False  # 是否为百分比数值
    percent_label: bool = False  # 是否为带百分比标签

    def to_dict(self):
        d = super().to_dict()
        if not isinstance(d['y'], list):
            d['y'] = [d['y']]
        return d


class MapPlot(ReportElement):
    """
    中国地图热力图
    area：地区
    number:数值
    name:标题名
    description：文本说明
    data_label：是否展现点的数值情况 默认为False
    """
    area: Series
    number: Series
    data_label: bool = False
    vmin: Optional[float] = None
    vmax: Optional[float] = None


class Table(ReportElement):
    form: DataFrame
    limit: Optional[int] = Field(None, ge=1)
    oss_key: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)

    def set_oss_key(self, oss_key):
        self.oss_key = oss_key

    def to_dict(self):
        if self.limit is not None:
            form = self.form.iloc[:self.limit]
            d = super().dict(exclude={"form"})

            fff = list(zip(*[[k] + list(v.values()) for k, v in form.to_dict().items()]))
            d["form"] = fff
            d["oss_key"] = self.oss_key
        else:
            d = super().to_dict()

        return d


class Text(ReportElement):
    pass


class PngBase64View(ReportElement):
    data: str


class DataFrameView(ReportElement):
    data: object
    height: Optional[float] = None
    width: Optional[float] = None

    @validator('data')
    def validate_elements_property(cls, obj):
        __notebook_results = []
        if isinstance(obj, DataFrame):
            # return NotebookViewExtra.dataframe_to_html(obj)
            return obj
        elif isinstance(obj, Series):
            # return NotebookViewExtra.dataframe_to_html(obj)
            return obj

        raise TypeError("当前data对象不支持DataFrameView方式,data必须要DataFrame")

    def to_dict(self):
        d = super().to_dict()
        data = d["data"]
        if isinstance(data, DataFrame):
            d["data"] = NotebookViewExtra.dataframe_to_html(data)
        elif isinstance(data, Series):
            d["data"] = NotebookViewExtra.dataframe_to_html(data)
        else:
            raise TypeError("当前data对象不支持DataFrameView方式,data必须要DataFrame")
        return d


class FigureView(ReportElement):
    data: Figure

    def to_dict(self):
        d = super().to_dict()
        fig = d["data"]
        if isinstance(fig, Figure):
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            d["data"] = img_base64
            buf.close()
        else:
            raise TypeError("当前data对象不支持FigureView方式,data必须要Figure类型")

        return d


class PngBytesIOView(ReportElement):
    data: object

    def to_dict(self):
        d = super().to_dict()
        buf = d["data"]
        if isinstance(buf, io.BytesIO):
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            d["data"] = img_base64
        else:
            raise TypeError("当前data对象不支持PngView方式,data必须要Figure类型")
        return d


class SvgBytesIOView(ReportElement):
    data: object

    def to_dict(self):
        d = super().to_dict()
        buf = d["data"]
        if isinstance(buf, io.BytesIO):
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            d["data"] = img_base64
        else:
            raise TypeError("当前data对象不支持PngView方式,data必须要Figure类型")
        return d


class RdkitSmiles2dMol(ReportElement):
    data: Chem.Mol
    height: float = Field(500, le=5000)
    width: float = Field(500, le=5000)

    def to_dict(self):
        d = super().to_dict()
        rd = d["data"]
        if isinstance(rd, Chem.Mol):
            from rdkit.Chem import Draw
            fig = Draw.MolToImage(rd, size=(self.width, self.height))
            buf = io.BytesIO()

            fig.save(buf, format='PNG')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
            d["data"] = img_base64
        else:
            raise TypeError("当前data对象不支持RdkitSmiles2dMol方式,data必须要rdkit.Chem.Mol类型")
        return d


class RdkitSmiles3dMol(ReportElement):
    data: Chem.Mol
    height: float = Field(500, le=5000)
    width: float = Field(500, le=5000)

    def to_dict(self):
        d = super().to_dict()
        mol = d["data"]
        if isinstance(mol, Chem.Mol):
            mol_block = Chem.MolToMolBlock(mol)
            d["data"] = mol_block
        else:
            raise TypeError("当前data对象不支持RdkitSmiles3dMol方式,data必须要rdkit.Chem.Mol类型")
        return d


class SpssproModel(ReportElement):
    model_key: str = ""
    model_plk_bytes: Optional[bytes] = None

    def __init__(self, model, **data):
        super().__init__(**data)
        model_plk_bytes = cloudpickle.dumps(model)
        del model
        super().__setattr__("model_plk_bytes", model_plk_bytes)

    def save_model_plk(self):
        return self.model_plk_bytes

    def __setattr__(self, key, value):
        raise AttributeError("不允许修改变量")

    def __repr__(self):
        return "<class> SpssproModel 存储模型"

    def __str__(self):
        return "<class> SpssproModel 存储模型"

    def to_dict(self):
        d = super().to_dict()
        if d.get("model_plk_bytes") is not None:
            del d["model_plk_bytes"]
        if not self.model_key:
            d["oss_key"] = self.model_key
        return d

    def set_model_key(self, model_key, key_code: str = ""):
        if key_code != "spsspro_custom_script_model_key_bcd":
            raise ValueError("无法调用set_model_key")
        super().__setattr__("model_key", model_key)


class NotebookView(ReportElement):
    data: object
    height: Optional[float] = None
    width: Optional[float] = None

    @validator('data')
    def validate_elements_property(cls, obj):
        import hiplot as hip
        import py3Dmol

        __notebook_results = []
        if isinstance(obj, DataFrame):
            __notebook_results.append(NotebookViewExtra.dataframe_to_html(obj))
        elif isinstance(obj, Figure):
            __notebook_results.append(NotebookViewExtra.figure_to_html(obj))
        elif isinstance(obj, Chem.Mol):
            __notebook_results.append(NotebookViewExtra.smiles_to_2d_html(obj))
        elif isinstance(obj, hip.Experiment):
            __notebook_results.append(NotebookViewExtra.hiplot_to_html(obj))
        elif isinstance(obj, py3Dmol.view):
            __notebook_results.append(NotebookViewExtra.py3Dmol_to_html(obj))
        else:
            if hasattr(obj, '_repr_html_'):
                __notebook_results.append(obj._repr_html_())
            # if hasattr(obj, '_repr_svg_'):
            #     __notebook_results.append(obj._repr_html_())
            # if hasattr(obj, '_repr_latex_'):
            #     __notebook_results.append(obj._repr_html_())
            # if hasattr(obj, '_repr_png_'):
            #     __notebook_results.append(obj._repr_html_())
            # if hasattr(obj, '__str__'):
            #     __notebook_results.append(obj._repr_html_())
            # if hasattr(obj, '__repr__'):
            #     __notebook_results.append(obj._repr_html_())
        if not __notebook_results:
            raise TypeError("当前对象不支持，notebook调用方式")

        return __notebook_results


class Report(BaseValueObject):
    elements: List[ReportElement]

    def to_dict(self):
        # 需要额外针对性处理，SpssproModel将其放到其他地方去
        return {
            'elements': [{'type': ele.__class__.__name__, 'data': ele.to_dict()} for ele in self.elements]
        }


class CustomScriptExecuteResult(BaseValueObject):
    return_obj: Any = None
    output: Optional[List[str]] = None
    err_msg: Optional[str] = None
    err_lineno: Optional[int] = None
    err_msg_info: Optional[str] = None

    def to_dict(self):
        return {
            'result': self.return_obj.to_dict() if self.return_obj is not None else None,
            'output': ''.join(self.output) if self.output else '',
            'err_msg': self.err_msg,
            'err_lineno': self.err_lineno,
            'err_msg_info': self.err_msg_info
        }
