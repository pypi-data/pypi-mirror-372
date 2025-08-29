"""
custom_script_executor.py
========================
SPSSPRO 自定义脚本安全执行引擎
------------------------------------------------

本文件包含三部分：
1. **执行引擎实现** (`CustomScriptExecutor` 等)
2. **辅助安全 Hook / 工具函数**
3. **unittest 测试用例**

使用方式
~~~~~~~~
```bash
python -m unittest custom_script_executor.py  # 执行所有测试

executor = CustomScriptExecutor()
result, error = executor.execute_script()

```
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Python 标准库
# ---------------------------------------------------------------------------
import ast
import builtins
import io
import os
import pickle
import sys
import unittest
import uuid
from types import MappingProxyType
from typing import Any, Dict, Optional, Sequence, Tuple

import cloudpickle
# ---------------------------------------------------------------------------
# 第三方库
# ---------------------------------------------------------------------------
import matplotlib
import numpy as np
import pandas as pd
from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Eval import default_guarded_getitem, default_guarded_getiter
from RestrictedPython.Guards import _write_wrapper
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython.transformer import copy_locations, RestrictingNodeTransformer
from pandas import DataFrame, Series
from pandas.core.indexing import _LocIndexer, _iLocIndexer
from pandas.io.formats.excel import ExcelFormatter
from pandas.io.html import _read as html_read
from pandas.io.parsers import readers as readers_read, TextFileReader
from pandas.io.sql import SQLDatabase

from spsspro_custom_script.custom_script import (
    SpssproModel, ReportElement, Report, CustomScriptType, CustomScriptExecuteResult, Table
)
from spsspro_custom_script.spsspro_pickle import safe_unpickler_loads

# ---------------------------------------------------------------------------
# 常量 & 配置
# ---------------------------------------------------------------------------

CUSTOM_SCRIPT_FILE_NAME = "sp_custom_script"
MODULE_NAME = "spsspro_custom_script_module"

IMPORT_WHITELIST: Sequence[str] = (
    "random",
    "math",
    "re",
    "datetime",
    "numpy",
    "pandas",
    "sklearn",
    "statsmodels",
    "scipy",
    "symbol",
    "shap",
    "sko",
    "matplotlib",
    "rdkit"
)

IOPERATOR_TO_STR: MappingProxyType[str, str] = MappingProxyType(
    {
        ast.Add: "+=",
        ast.Sub: "-=",
        ast.Mult: "*=",
        ast.Div: "/=",
        ast.Mod: "%=",
        ast.Pow: "**=",
        ast.LShift: "<<=",
        ast.RShift: ">>=",
        ast.BitOr: "|=",
        ast.BitXor: "^=",
        ast.BitAnd: "&=",
        ast.FloorDiv: "//=",
        ast.MatMult: "@=",
    }
)


# ---------------------------------------------------------------------------
# Exception definitions
# ---------------------------------------------------------------------------

class CustomScriptError(RuntimeError):
    """Raised when user script explicitly calls a forbidden helper."""


# ---------------------------------------------------------------------------
# 安全 Hook 与 Guard
# ---------------------------------------------------------------------------


def _hook_import(name: str, *args, **kwargs):  # noqa: D401 – hook must match signature
    """限制 `import`，仅允许白名单中的顶级包。"""

    if name.split(".")[0] in IMPORT_WHITELIST:
        return __import__(name, *args, **kwargs)
    raise RuntimeError(f"cannot import {name}")


def _hook_import_docker(name: str, *args, **kwargs):
    return __import__(name, *args, **kwargs)


# Pandas IO、写文件等高风险函数黑名单
_PANDAS_IO_FUNCS = {
    pd.read_csv,
    pd.read_excel,
    pd.read_sql,
    pd.read_sql_query,
    pd.ExcelFile,
    pd.ExcelWriter,
    pd.read_clipboard,
    pd.read_feather,
    pd.read_gbq,
    pd.read_html,
    pd.read_json,
    pd.read_orc,
    pd.read_parquet,
    pd.read_fwf,
    pd.read_table,
    pd.read_pickle,
    pd.to_pickle,
    pd.read_hdf,
    pd.read_sas,
    pd.read_spss,
    pd.read_sql_query,
    pd.read_sql,
    pd.read_sql_table,
    pd.read_stata,
    pd.read_xml,
    readers_read,
    html_read,

    matplotlib.use,
}

_PANDAS_NDFrame_BLOCKLIST = {
    "to_excel",
    "to_json",
    "to_hdf",
    "to_sql",
    "to_pickle",
    "to_clipboard",
    "to_xarray",
    "to_latex",
    "to_csv",
}

_EXCEL_FORMATTER_BLOCKLIST = {"write"}
_SQL_DATABASE_BLOCKLIST = {"to_sql"}


def _hook_getattr(obj: Any, attr: str):  # noqa: D401 – RestrictedPython requires this name
    """
    Custom getattr guard that bans dangerous attributes/functions.
    此方法用于拦截类调用方法，因此obj可能会拿到的是一个实例化之后的对象，也可能是没有实例化的类，因此必须判断is
    """

    # Hard ban on raw modules that allow filesystem access
    if obj is os:
        raise RuntimeError('Restricted, cannot use os')
    if obj is io:
        raise RuntimeError('Restricted, cannot use io')
    if obj is pickle:
        raise RuntimeError('Restricted, cannot use pickle')
    if obj is cloudpickle:
        raise RuntimeError('Restricted, cannot use cloudpickle')

    # pandas sub‑modules
    if obj is pd and attr == "io":
        raise RuntimeError("Restricted, cannot use pandas io")
    if obj is pd.io:
        raise RuntimeError("Restricted, cannot use pandas io")

    if obj is DataFrame or isinstance(obj, DataFrame):
        if attr in _PANDAS_NDFrame_BLOCKLIST:
            raise RuntimeError(f'Restricted, cannot use pandas {attr}')
    if obj is ExcelFormatter or isinstance(obj, ExcelFormatter):
        if attr in _EXCEL_FORMATTER_BLOCKLIST:
            raise RuntimeError(f'Restricted, cannot use pandas {attr}')
    if obj is SQLDatabase or isinstance(obj, SQLDatabase):
        if attr in _SQL_DATABASE_BLOCKLIST:
            raise RuntimeError(f'Restricted, cannot use pandas {attr}')
    if obj is TextFileReader or isinstance(obj, TextFileReader):
        # 禁止所有涉及这个的
        raise RuntimeError('Restricted, cannot use TextFileReader')

    func = getattr(obj, attr)
    for ban_func in _PANDAS_IO_FUNCS:
        if func is ban_func:
            raise RuntimeError(f'Restricted, cannot use pandas {attr}')

    return func


# ---------------- In‑place operator helper --------------------------------------

def custom_inplacevar(op: str, x: Any, y: Any):
    """Execute a safe in‑place operation inside the restricted scope."""

    if op not in IOPERATOR_TO_STR.values():
        raise CustomScriptError(f"'{op}' is not a supported inplace operator")
    local_ctx = {"x": x, "y": y}
    exec(f"x{op}y", local_ctx)  # nosec – executed inside restricted env
    return local_ctx["x"]


# ---------------- Write guard ---------------------------------------------------

def _build_full_write_guard():
    """Factory for the complex write guard logic."""

    safetypes = {
        dict,
        list,
        DataFrame,
        Series,
        _iLocIndexer,
        _LocIndexer,
        np.ndarray,
        np.nditer,
        np.dtype,
    }
    Wrapper = _write_wrapper()

    def guard(ob):  # noqa: D401
        if ob.__class__.__module__ == MODULE_NAME:
            return ob
        if type(ob) in safetypes or hasattr(ob, "_guarded_writes"):
            return ob
        return Wrapper(ob)

    return guard


# ---------------------------------------------------------------------------
# Print collector (singleton to avoid leaking output buffers)
# ---------------------------------------------------------------------------

def singleton(cls):  # noqa: D401 – simple singleton decorator
    """Class‑based singleton decorator.
    """

    _instance: dict[type, Any] = {}

    def inner(*args, **kwargs):  # noqa: ANN001 – forward untyped args
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return inner


@singleton
class SafePrintCollector(PrintCollector):
    """PrintCollector that exposes a mutable txt list attribute."""

    txt: list[str]


# ---------------------------------------------------------------------------
# Safe built‑ins builder
# ---------------------------------------------------------------------------

def spsspro_io_bytes():
    buf = io.BytesIO()
    return buf


def spsspro_io_string():
    buf = io.StringIO()
    return buf


# deferred: functions rely on safe_builtins reference
def guarded_unpack_sequence(it, spec, _getiter_):  # noqa: D401 – internal helper
    ret = list(_getiter_(it))
    if len(ret) < spec["min_len"]:
        return ret
    for idx, child_spec in spec["childs"]:
        ret[idx] = guarded_unpack_sequence(ret[idx], child_spec, _getiter_)
    return ret


def guarded_iter_unpack_sequence(it, spec, _getiter_):  # noqa: D401 – internal helper
    for ob in _getiter_(it):
        yield guarded_unpack_sequence(ob, spec, _getiter_)


def build_safe_builtins(safe_import=True) -> dict[str, Any]:
    """返回隔离执行环境可用的内置函数映射。
    """

    allowed_builtins = {
        name: getattr(builtins, name)
        for name in (
            "dict",
            "enumerate",
            "filter",
            "getattr",
            "hasattr",
            "iter",
            "list",
            "map",
            "max",
            "min",
            "sum",
            "all",
            "any",
            "type",
            "set",
        )
    }

    _safe_builtins = safe_builtins.copy()
    _safe_builtins.update(allowed_builtins)

    # Remove potentially unsafe built‑ins
    _safe_builtins.pop("id", None)

    # Inject custom hooks / guards
    if safe_import:
        _safe_builtins["__import__"] = _hook_import
    else:
        _safe_builtins["__import__"] = _hook_import_docker

    _safe_builtins.update(
        {
            "_getattr_": _hook_getattr,
            "_getitem_": default_guarded_getitem,
            "_getiter_": default_guarded_getiter,
            "_print_": SafePrintCollector,
            "_setattr_": setattr,
            "setattr": setattr,
            "_write_": _build_full_write_guard(),
            "_inplacevar_": custom_inplacevar,
            "_unpack_sequence_": None,  # set below
            "_iter_unpack_sequence_": None,  # set below
            "CustomScriptError": CustomScriptError,
            Report.__name__: Report,
            '_apply_': lambda f, *a, **kw: f(*a, **kw),
            '**kwargs': lambda **x: x,  # 允许 **kwargs 语法
        }
    )

    _safe_builtins["spsspro_io_bytes"] = spsspro_io_bytes
    _safe_builtins["spsspro_io_string"] = spsspro_io_string

    # Add supported report elements
    for element in ReportElement._supported_elements:
        _safe_builtins[element.__name__] = element

    _safe_builtins["_unpack_sequence_"] = guarded_unpack_sequence
    _safe_builtins["_iter_unpack_sequence_"] = guarded_iter_unpack_sequence

    return _safe_builtins


class SpssproPredictModel:
    # 需要触发保存的模式
    def __init__(self, model_bytes: Optional[bytes] = None, pickle_is_allowed: bool = True):
        self.__model = None
        self.__model_oss_key = None
        self.__model_bytes = model_bytes
        self.__pickle_is_allowed = pickle_is_allowed

    def save_spsspro_model(self, model):
        if self.__model_oss_key or self.__model_bytes:
            raise CustomScriptError("当前算法仅允许保存一个模型")

        self.__model_oss_key = uuid.uuid4()
        self.__model = model

        return SpssproModel(model=model)

    def load_spsspro_model(self):
        # waring 不允许在此处加载模型
        if self.__model is None:
            if self.__model_bytes is None:
                raise CustomScriptError("当前报告没有模型，无法加载")
            self.__model = safe_unpickler_loads(self.__model_bytes, is_allowed=self.__pickle_is_allowed)
        return self.__model


# ---------------------------------------------------------------------------
# 自定义 AST Transformer —— 强化属性访问安全
# ---------------------------------------------------------------------------

class SpssproRestrictingNodeTransformer(RestrictingNodeTransformer):
    """Custom AST transformer tightening attribute / name rules."""

    def visit_Attribute(self, node):  # noqa: D401 – override RestrictedPython
        if node.attr.startswith("_") and node.attr not in {"_", "__init__"}:
            self.error(node, f'"{node.attr}" cannot start with "_"')
        if node.attr.endswith("__roles__"):
            self.error(node, f'"{node.attr}" cannot end with "__roles__"')

        # 读取属性时用 _getattr_ 包装
        if isinstance(node.ctx, ast.Load):
            node = self.node_contents_visit(node)
            new_node = ast.Call(
                func=ast.Name("_getattr_", ast.Load()),
                args=[node.value, ast.Str(node.attr)],
                keywords=[],
            )
            copy_locations(new_node, node)
            return new_node

        # # 写属性使用 _write_ Guard
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            node = self.node_contents_visit(node)
            new_value = ast.Call(
                func=ast.Name('_write_', ast.Load()),
                args=[node.value],
                keywords=[]
            )

            copy_locations(new_value, node.value)
            node.value = new_value
            return node

        raise NotImplementedError(f"Unknown ctx type: {type(node.ctx)}")


# ---------------------------------------------------------------------------
# Local proxy mapping locals → globals (sync on write)
# ---------------------------------------------------------------------------

class _LocalsProxy(dict):
    """Proxy mapping that synchronises writes into *globals* namespace."""

    def __init__(self, global_dict: dict[str, Any], initial: Dict[str, Any]):
        super().__init__(initial)
        self._globals = global_dict

    def __setitem__(self, key: str, value: Any):  # noqa: D401 – match dict API
        self._globals[key] = value
        super().__setitem__(key, value)


# ---------------------------------------------------------------------------
# Core service façade
# ---------------------------------------------------------------------------

class CustomScriptExecutor:
    """Service responsible for compiling & executing user scripts safely."""

    def __init__(self, language: str = 'python'):
        self.lang = language.lower()

    # Public API ------------------------------------------------------------------

    def execute_script(
            self, script: str, df: DataFrame, script_type: CustomScriptType, *,
            params_dict: Dict[str, Any] = None,
            model_plk_file_bytes: Optional[bytes] = None,
            safety_import: bool = True,
    ) -> Tuple[Optional[CustomScriptExecuteResult], Optional[str]]:
        """Compile & run *script* inside a restricted environment.

        Parameters
        ----------
        script
            User‑supplied Python code.
        script_type
            Distinguish between *data_process* (expects df mutation) and
            *data_analysis* (expects a Report object).
        df
            Original data frame passed to the script when *script_type* is
            *data_process*.
        params_dict
            其他算法执行需要的局部变量
        model_plk_file_bytes: 对应预测模型的文件
        safety_import: if True, `import xxxx` 的内容会受到限制
        """
        # Prepare execution context ------------------------------------------------
        safe_builtins_ctx = build_safe_builtins(safety_import)
        safe_globals: dict[str, Any] = {
            "__builtins__": safe_builtins_ctx,
            "__name__": MODULE_NAME,
            "__metaclass__": type,
            "__build_class__": __build_class__,
            "classmethod": classmethod,
            "staticmethod": staticmethod,
            "property": property,
            "super": super,
        }
        # 必须放入到全局变量上，否则后续模型加载会出现无法找到_getattr_等
        safe_globals.update(safe_builtins_ctx)

        _locals = locals().copy()

        # *locals* needs to expose param_dict AND funnel writes back to globals ----
        exec_locals = _LocalsProxy(safe_builtins_ctx, _locals)
        if params_dict:
            exec_locals.update(params_dict)

        # Inject initial df for data_process scripts
        if script_type.value == CustomScriptType.data_process:
            exec_locals["df"] = df

        # Compile & execute --------------------------------------------------------
        print_collector = SafePrintCollector()
        print_collector.txt = []  # type: ignore[attr-defined]

        try:
            code_obj = compile_restricted(
                script,
                filename=CUSTOM_SCRIPT_FILE_NAME,
                policy=SpssproRestrictingNodeTransformer,
            )

            for key in ["self", "script", "script_type"]:
                exec_locals.pop(key)

            sm = SpssproPredictModel(model_bytes=model_plk_file_bytes, pickle_is_allowed=safety_import)
            if script_type.value == CustomScriptType.data_analysis:
                # 数据处理没有此模型
                if not model_plk_file_bytes:
                    exec_locals['save_spsspro_model'] = sm.save_spsspro_model
                else:
                    exec_locals['load_spsspro_model'] = sm.load_spsspro_model
            elif script_type.value == CustomScriptType.data_analysis_predict:
                # 数据处理没有此模型
                # todo:考虑如何将数据放进去
                # 包装safe_unpickler_loads 转为懒加载
                # sm = SpssproPredictModel()
                exec_locals['load_spsspro_model'] = sm.load_spsspro_model

            exec(code_obj, safe_globals, exec_locals)  # nosec – compiled safe code

            if script_type.value == CustomScriptType.data_process:
                df_result = exec_locals.get("df")
                if isinstance(df_result, DataFrame):
                    return CustomScriptExecuteResult(
                        return_obj=df_result,
                        output=print_collector.txt,
                    ), None
            elif script_type.value == CustomScriptType.data_analysis:
                report = exec_locals.get("report")
                # todo:需要额外处理SpssproPredictModel，存储成对应的模型
                if isinstance(report, Report):
                    return CustomScriptExecuteResult(
                        return_obj=report,
                        output=print_collector.txt,
                    ), None
            elif script_type.value == CustomScriptType.data_analysis_predict:
                predict_df = exec_locals.get("predict_df")
                if isinstance(predict_df, DataFrame):
                    return CustomScriptExecuteResult(
                        return_obj=Report(elements=[Table(form=predict_df)]),
                        output=print_collector.txt,
                    ), None

            return CustomScriptExecuteResult(output=print_collector.txt), None

        except CustomScriptError as e:
            return self._wrap_error(e, print_collector)
        except Exception as e:  # noqa: BLE001 – broad except required by engine
            return self._wrap_error(e, print_collector)

    def _wrap_error(
            self,
            exc: Exception,
            collector: SafePrintCollector,
    ) -> Tuple[CustomScriptExecuteResult, None]:
        """Convert *exc* into a structured :class:`CustomScriptExecuteResult`."""

        err_msg, err_lineno = self._get_script_error_info()
        return CustomScriptExecuteResult(
            output=collector.txt,
            err_msg=err_msg,
            err_lineno=err_lineno,
            err_msg_info=str(exc),
        ), None

    @staticmethod
    def _get_script_error_info() -> Tuple[str | None, int | None]:
        """Extract user‑level error message & line number from traceback."""
        err_type, err, tb = sys.exc_info()
        while tb:
            if tb.tb_frame.f_code.co_filename == CUSTOM_SCRIPT_FILE_NAME:
                err_msg = (
                    f"Line {tb.tb_lineno}: {err.__class__.__name__}: {err.args[0]}"
                    if err
                    else ""
                )
                return err_msg, tb.tb_lineno
            tb = tb.tb_next

        if err_type is SyntaxError:  # type: ignore[comparison-overlap]
            # pyright: ignore[reportGeneralTypeIssues] – runtime branch
            return "\n".join(err.msg) if err and err.msg else "", None  # type: ignore[attr-defined]
        return str(err) if err else "", None


class TestCustomScriptExecutor(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = CustomScriptExecutor()

    def test_empty_script(self):
        script = ''
        df = pd.DataFrame()
        result, error = self.executor.execute_script(script, df, CustomScriptType.data_process)
        print(result, '\n', error)
        assert error

    def test_basic_execution(self):
        script = "result = a + b\nprint(f'计算结果: {result}')"
        variables_params = {"a": 3, "b": 5}
        df = pd.DataFrame()
        result, error = self.executor.execute_script(
            script, df, CustomScriptType.data_process,
            params_dict=variables_params
        )
        print(result, '\n', error)

    def test_syntax_error(self):
        script = "print('Hello'"  # 缺少右括号
        df = pd.DataFrame()
        result, error = self.executor.execute_script(script, df, CustomScriptType.data_process)
        print(result, '\n', error)

    def test_custom_import(self):
        script = 'import matplotlib as plt\n'
