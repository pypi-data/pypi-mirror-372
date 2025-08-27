# Copyright Dechin CHEN 2025

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import importlib
import warnings
from .backend import optim, nn, cuda, data

def detect_hardware():
    import os
    if "ASCEND_HOME_PATH" in os.environ:
        return "ascend"
    if "CUDA_HOME" not in os.environ and "CUDA_PATH" not in os.environ:
        return "cpu"
    return "gpu"

_DEVICE_TARGET = detect_hardware()

# 深度学习后端配置系统
if _DEVICE_TARGET == "ascend":
    _BACKEND = os.environ.get("DEEP_LEARNING_BACKEND", "mindspore")
else:
    _BACKEND = os.environ.get("DEEP_LEARNING_BACKEND", "pytorch")


_BK_DICT = {'mindspore_ascend': 'mindspore_ascend', 
            'mindspore_gpu': 'mindspore_gpu', 
            'pytorch_gpu': 'pytorch_gpu', 
            'pytorch_ascend': 'pytorch_ascend'}


_BACKEND = _BK_DICT[_BACKEND+"_{}".format(_DEVICE_TARGET)]
_SUPPORTED_BACKENDS = ["pytorch", "mindspore", "jax"]

# 自动选择后端实现
try:
    backend_module = importlib.import_module(f".backend.{_BACKEND}_ops", package=__name__)
except ImportError:
    warnings.warn(f"Backend {_BACKEND} not found, falling back to PyTorch")
    backend_module = importlib.import_module(".backend.pytorch_ops", package=__name__)

# 算子转发机制
def __getattr__(name):
    """动态转发算子到指定后端"""
    if hasattr(backend_module, name):
        return getattr(backend_module, name)
    raise AttributeError(f"Module 'ext' has no attribute '{name}'")

# 后端管理接口
def set_backend(backend: str):
    """切换深度学习后端"""
    global backend_module, _BACKEND
    if backend not in _SUPPORTED_BACKENDS:
        raise ValueError(f"Unsupported backend: {backend}. Supported: {_SUPPORTED_BACKENDS}")
    
    try:
        backend_module = importlib.import_module(f".backend.{backend}_ops", package=__name__)
        _BACKEND = backend
    except ImportError:
        raise RuntimeError(f"Backend {backend} implementation not found")

def get_backend() -> str:
    """获取当前后端名称"""
    return _BACKEND

# 初始化时自动加载PyTorch实现
__all__ = ['set_backend', 'get_backend'] + dir(backend_module)
