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
    Optimizer = nn.Optimizer
    Adadelta = nn.Adadelta
    Adagrad = nn.Adagrad
    Adam = nn.Adam
    AdaMax = nn.AdaMax
    AdamWeightDecay = nn.AdamWeightDecay
    AdaSumByDeltaWeightWrapCell = nn.AdaSumByDeltaWeightWrapCell
    AdaSumByGradWrapCell = nn.AdaSumByGradWrapCell
    ASGD = nn.ASGD
    FTRL = nn.FTRL
    Lamb = nn.Lamb
    LARS = nn.LARS
    LazyAdam = nn.LazyAdam
    Momentum = nn.Momentum
    OptTFTWrapper = nn.OptTFTWrapper
    ProximalAdagrad = nn.ProximalAdagrad
    RMSProp = nn.RMSProp
    Rprop = nn.Rprop
    SGD = nn.SGD


else:
    from torch import optim
    from torch import tensor, float32
    # Adam = optim.Adam

    class Optimizer(optim.Optimizer):
        def __init__(self, params, defaults):
            super().__init__(params, defaults)
            self.pressure = None
            self.velocity = None
            self.kinetics = tensor([0], dtype=float32)
            self.temperature = None
        def construct(self, *args, **kwargs):
            return None
        def step(self, *args, **kwargs):
            return self.construct(*args, **kwargs)


    class Adam(optim.Adam):
        def __init__(self, params, defaults):
            super().__init__(params, defaults)
            self.pressure = None
            self.velocity = None
            self.kinetics = tensor([0], dtype=float32)
            self.temperature = None
