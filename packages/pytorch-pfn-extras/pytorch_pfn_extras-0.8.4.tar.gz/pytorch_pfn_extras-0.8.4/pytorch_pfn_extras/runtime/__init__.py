from pytorch_pfn_extras.runtime._registry import _RuntimeRegistry  # NOQA
from pytorch_pfn_extras.runtime._runtime import BaseRuntime  # NOQA
from pytorch_pfn_extras.runtime._runtime import PyTorchRuntime  # NOQA

runtime_registry = _RuntimeRegistry(PyTorchRuntime)
