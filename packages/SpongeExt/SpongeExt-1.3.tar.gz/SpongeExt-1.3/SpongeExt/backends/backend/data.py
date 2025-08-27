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
    import mindspore as ms

elif _BACKEND == "pytorch":
    from torch.utils.data import Dataset, TensorDataset, DataLoader
    from torch.utils.data import sampler

else:
    pass
