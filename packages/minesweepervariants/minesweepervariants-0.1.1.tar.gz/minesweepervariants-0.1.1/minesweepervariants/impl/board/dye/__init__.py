import pkgutil
import importlib
import pathlib
from abc import ABC, abstractmethod


class AbstractDye(ABC):
    name = None

    @abstractmethod
    def dye(self, board):
        """染色函数"""


# 动态递归导入当前目录所有模块和包
def _auto_import_modules():
    current_pkg = __name__
    current_path = pathlib.Path(__file__).parent

    for finder, name, ispkg in pkgutil.walk_packages([str(current_path)], prefix=current_pkg + "."):
        importlib.import_module(name)


_auto_import_modules()


def get_dye(name: str) -> type[AbstractDye] | None:
    name = name[1:] if name.startswith("@") else name
    for cls in AbstractDye.__subclasses__():
        if cls.name == name:
            return cls
    raise ValueError(f"未知的染色规则[@{name[1:] if name.startswith('@') else name}]")


def get_all_dye():
    result = {}
    for cls in AbstractDye.__subclasses__():
        result[cls.name] = cls.__doc__
    return result
