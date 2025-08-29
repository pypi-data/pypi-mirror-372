import io
import pickle

IMPORT_WHITELIST = (
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
    "rdkit",
    "spsspro_custom_script"
)


def check_white_module(module):
    for white_module in IMPORT_WHITELIST:
        if module == white_module or module.startswith(f"{white_module}."):
            return True
    return False


class SafeUnpickler(pickle.Unpickler):
    allowed = {
        ('builtins', 'object'),
        ('builtins', 'type'),
        ('builtins', 'dict'),
        ('builtins', 'list'),
        ('builtins', 'str'),
        ('builtins', 'int'),
        ('builtins', 'float'),
        ('builtins', 'slice'),
        ('builtins', 'tuple'),
        ('builtins', 'frozenset'),
        ('builtins', 'range'),
        ('builtins', 'bytes'),
        ('builtins', 'bytearray'),
        ('builtins', 'complex'),
        ('builtins', 'set'),
        ('types', 'SimpleNamespace'),
    }

    not_allowed = {
        "builtins": {"eval", "exec", "compile", "open", "input", "__import__"},
        "os": {"system", "popen"},
        "subprocess": {"Popen", "call", "check_output", "run"},
    }

    def __init__(self, file, is_allowed=True):
        """
        is_allowed: 采用是否允许模块的方式，是的话就是为只允许某些模块通过，否的话就为禁止某些模块不通过（不一定全因此稍微慎重一下）
        """
        super().__init__(file)

        self.is_allowed = is_allowed

    def check_module(self, module):
        if check_white_module(module):
            return True

        if module == "cloudpickle" or module.startswith("cloudpickle."):
            cloudpickle_bans = [
                "cloudpickle.load",
                "cloudpickle.loads",
                "cloudpickle.dumps",
                "cloudpickle.dump"
            ]
            for cloudpickle_ban in cloudpickle_bans:
                if module.startswith(cloudpickle_ban):
                    raise ValueError("检测到不安全的对象类型，禁止模型加载")
            return True

        return False

    def find_class(self, module, name):
        if self.is_allowed:
            if not self.check_module(module) and (module, name) not in self.allowed:
                raise ValueError(f"模型加载失败")
        else:
            if module in self.not_allowed and name in self.not_allowed[module]:
                raise pickle.UnpicklingError(f"检测到不安全的对象类型{module}.{name}，禁止模型加载")

        return super().find_class(module, name)


def safe_unpickler_loads(o: bytes, is_allowed: bool = True):
    return SafeUnpickler(io.BytesIO(o), is_allowed=is_allowed).load()
