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


from functools import wraps
import mindspore as ms
from mindspore import numpy as msnp


_MINDSPORE_OPS = {}

def register_op(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    _MINDSPORE_OPS[func.__name__] = wrapper
    return wrapper

@register_op
def Sum(ipt, *args, **kwargs):
    return msnp.sum(ipt, *args, **kwargs)


@register_op
def where(ipt, *args, **kwargs):
    return msnp.where(ipt, *args, **kwargs)
