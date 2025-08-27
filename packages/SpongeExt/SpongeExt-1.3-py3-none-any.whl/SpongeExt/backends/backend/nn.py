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

def detect_hardware():
    import os
    if "ASCEND_HOME_PATH" in os.environ:
        return "ascend"
    if "CUDA_PATH" in os.environ:
        return "gpu"
    return "cpu"

_DEVICE_TARGET = detect_hardware()

# 深度学习后端配置系统
if _DEVICE_TARGET == "ascend":
    _BACKEND = os.environ.get("DEEP_LEARNING_BACKEND", "mindspore")
else:
    _BACKEND = os.environ.get("DEEP_LEARNING_BACKEND", "pytorch")

_SUPPORTED_BACKENDS = ["pytorch", "mindspore", "jax"]


if _BACKEND == "mindspore":
    from mindspore import nn

    class Module(nn.Cell):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__()
        def forward(self, *args, **kwargs):
            return self.construct(*args, **kwargs)
        def construct(self, *args, **kwargs):
            return None
    

    class ModuleList(nn.CellList):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__()
        def forward(self, *args, **kwargs):
            return self.construct(*args, **kwargs)
        def construct(self, *args, **kwargs):
            return None
    

elif _BACKEND == "pytorch":
    from torch import nn

    class Module(nn.Module):
        def __init__(self, *args, **kwargs) -> None:
            super(Module, self).__init__(*args, **kwargs)
        def forward(self, *args, **kwargs):
            return self.construct(*args, **kwargs)
        def construct(self, *args, **kwargs):
            return None
        
    class ModuleList(nn.ModuleList):
        def __init__(self, *args, **kwargs) -> None:
            super(ModuleList, self).__init__(*args, **kwargs)
        def forward(self, *args, **kwargs):
            return self.construct(*args, **kwargs)
        def construct(self, *args, **kwargs):
            return None

    Identity = nn.Identity
    Parameter = nn.Parameter
    Conv2d = nn.Conv2d
    Linear = nn.Linear
    functional = nn.functional
    ReLU = nn.ReLU

else:
    pass
