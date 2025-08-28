from .func01.func01 import factorial
from .func02.func02 import fib
from .cext.fastsum import fast_sum  # noqa: F401
from .call_numpy.call_numpy import call_numpy
from .call_pandas.call_pandas import call_pandas

try:
    from ._version import version as __version__
except Exception:  # 後備（理論上不太會用到）
    __version__ = "0.0.0"

__all__ = ["factorial", "fib", "fast_sum", "call_numpy", "call_pandas"]
