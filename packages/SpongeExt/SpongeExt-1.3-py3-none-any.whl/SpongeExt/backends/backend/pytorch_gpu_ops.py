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
import torch
from .base import OpsNamespace
from torchmetrics import Metric


int32 = torch.int32
int64 = torch.int64
float16 = torch.float16
float32 = torch.float32
float64 = torch.float64
bool_ = torch.bool
Tensor = torch.Tensor
long = torch.long
_Metric = Metric


class PyTorchAutograd(OpsNamespace):
    @property
    def __name__(self):
        return "autograd"
    @property
    def grad(self):
        import torch.autograd
        return torch.autograd.grad


autograd = PyTorchAutograd()


def _combine_seeds(seed: int, seed2: int) -> int:
    combined = (seed * 31 + seed2) % 2**32
    return combined


def set_seed(seed1, seed2=None):
    if seed2 is not None:
        seed = _combine_seeds(seed1, seed2)
    else:
        seed = seed1
    torch.manual_seed(seed)


_TORCH_OPS = {}

def register_op(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    _TORCH_OPS[func.__name__] = wrapper
    return wrapper


@register_op
def get_parameters(model):
    return model.parameters()


@register_op
def Sum(input, *args, **kwargs):
    """ Sum function of pytorch"""
    return torch.sum(input, *args, **kwargs)


def _convert_paddings_to_pad(paddings):
    """将MindSpore的paddings格式转换为PyTorch的pad格式"""
    # 示例：paddings = ((0, 0), (0, 0), (2, 2), (1, 1)) → pad = (1, 1, 2, 2)
    flat_pads = []
    for dim in reversed(paddings):  # 从最后一维开始逆序处理
        flat_pads.extend(dim)       # 展开为 (左, 右, 上, 下, ...)
    return tuple(flat_pads)


@register_op
def pad(arr, ints, **kwargs):
    """ Pad function."""
    if 'constant_value' in kwargs:
        kwargs['value'] = kwargs['constant_value']
        kwargs.pop('constant_value')
    return torch.nn.functional.pad(arr, _convert_paddings_to_pad(ints), **kwargs)


@register_op
def reduce_sum(input, dim):
    """ Sum function of pytorch"""
    return torch.sum(input, dim=dim, keepdim=False)


@register_op
def reduce_max(input, dim=None, keepdim=False):
    """ Sum function of pytorch"""
    if dim is None:
        return torch.max(input)
    return torch.max(input, dim, keepdim=keepdim)[0]


@register_op
def reduce_min(input, dim=None, keepdim=False):
    """ Sum function of pytorch"""
    if dim is None:
        return torch.min(input)
    return torch.min(input, dim, keepdim=keepdim)[0]


@register_op
def is_tensor(input, *args, **kwargs):
    return torch.is_tensor(input, *args, **kwargs)


@register_op
def is_storage(input, *args, **kwargs):
    return torch.is_storage(input, *args, **kwargs)


@register_op
def stop_gradient(arr):
    arr.requires_grad_(False)
    return arr


@register_op
def depend(input, *args, **kwargs):
    return input


@register_op
def is_complex(input, *args, **kwargs):
    return torch.is_complex(input, *args, **kwargs)


@register_op
def is_conj(input, *args, **kwargs):
    return torch.is_conj(input, *args, **kwargs)


@register_op
def is_floating_point(input, *args, **kwargs):
    return torch.is_floating_point(input, *args, **kwargs)


@register_op
def is_nonzero(input, *args, **kwargs):
    return torch.is_nonzero(input, *args, **kwargs)


@register_op
def set_default_dtype(input, *args, **kwargs):
    return torch.set_default_dtype(input, *args, **kwargs)


@register_op
def get_default_dtype():
    return torch.get_default_dtype()


@register_op
def set_default_device(input, *args, **kwargs):
    return torch.set_default_device(input, *args, **kwargs)


@register_op
def get_default_device():
    return torch.get_default_device()


@register_op
def set_default_tensor_type(input, *args, **kwargs):
    return torch.set_default_tensor_type(input, *args, **kwargs)


@register_op
def numel(input, *args, **kwargs):
    return torch.numel(input, *args, **kwargs)


@register_op
def set_printoptions(input, *args, **kwargs):
    return torch.set_printoptions(input, *args, **kwargs)


@register_op
def set_flush_denormal(input, *args, **kwargs):
    return torch.set_flush_denormal(input, *args, **kwargs)


@register_op
def tensor(input, *args, **kwargs):
    if isinstance(input, Tensor):
        return input.detach()
    arr = torch.tensor(input, *args, **kwargs)
    arr.requires_grad_(False)
    return arr


@register_op
def to_numpy(input, *args, **kwargs):
    return input.detach().numpy()


@register_op
def sparse_coo_tensor(input, *args, **kwargs):
    return torch.sparse_coo_tensor(input, *args, **kwargs)


@register_op
def sparse_csr_tensor(input, *args, **kwargs):
    return torch.sparse_csr_tensor(input, *args, **kwargs)


@register_op
def sparse_csc_tensor(input, *args, **kwargs):
    return torch.sparse_csc_tensor(input, *args, **kwargs)


@register_op
def sparse_bsr_tensor(input, *args, **kwargs):
    return torch.sparse_bsr_tensor(input, *args, **kwargs)


@register_op
def sparse_bsc_tensor(input, *args, **kwargs):
    return torch.sparse_bsc_tensor(input, *args, **kwargs)

@register_op
def asarray(input, *args, **kwargs):
    return torch.asarray(input, *args, **kwargs)


@register_op
def as_tensor(input, *args, **kwargs):
    return torch.as_tensor(input, *args, **kwargs)


@register_op
def as_strided(input, *args, **kwargs):
    return torch.as_strided(input, *args, **kwargs)


@register_op
def from_file(input, *args, **kwargs):
    return torch.from_file(input, *args, **kwargs)


@register_op
def from_numpy(input, *args, **kwargs):
    return torch.from_numpy(input, *args, **kwargs)


@register_op
def from_dlpack(input, *args, **kwargs):
    return torch.from_dlpack(input, *args, **kwargs)


@register_op
def frombuffer(input, *args, **kwargs):
    return torch.frombuffer(input, *args, **kwargs)


@register_op
def zeros(input, *args, **kwargs):
    return torch.zeros(input, *args, **kwargs)


@register_op
def zeros_like(input, *args, **kwargs):
    return torch.zeros_like(input, *args, **kwargs)


@register_op
def ones(input, *args, **kwargs):
    return torch.ones(input, *args, **kwargs)


@register_op
def ones_like(input, *args, **kwargs):
    return torch.ones_like(input, *args, **kwargs)


@register_op
def arange(input, *args, **kwargs):
    return torch.arange(input, *args, **kwargs)


@register_op
def Range(input, *args, **kwargs):
    return torch.range(input, *args, **kwargs)


@register_op
def linspace(input, *args, **kwargs):
    return torch.linspace(input, *args, **kwargs)


@register_op
def logspace(input, *args, **kwargs):
    return torch.logspace(input, *args, **kwargs)


@register_op
def eye(input, *args, **kwargs):
    return torch.eye(input, *args, **kwargs)


@register_op
def empty(input, *args, **kwargs):
    return torch.empty(input, *args, **kwargs)


@register_op
def empty_like(input, *args, **kwargs):
    return torch.empty_like(input, *args, **kwargs)


@register_op
def empty_strided(input, *args, **kwargs):
    return torch.empty_strided(input, *args, **kwargs)


@register_op
def full(input, *args, **kwargs):
    return torch.full(input, *args, **kwargs)


@register_op
def fill(dtype, shape, value):
    return torch.full(shape, value, dtype=dtype)


@register_op
def full_like(input, *args, **kwargs):
    return torch.full_like(input, *args, **kwargs)


@register_op
def quantize_per_tensor(input, *args, **kwargs):
    return torch.quantize_per_tensor(input, *args, **kwargs)


@register_op
def quantize_per_channel(input, *args, **kwargs):
    return torch.quantize_per_channel(input, *args, **kwargs)


@register_op
def dequantize(input, *args, **kwargs):
    return torch.dequantize(input, *args, **kwargs)


@register_op
def Complex(input, *args, **kwargs):
    return torch.complex(input, *args, **kwargs)


@register_op
def polar(input, *args, **kwargs):
    return torch.polar(input, *args, **kwargs)


@register_op
def heaviside(input, *args, **kwargs):
    return torch.heaviside(input, *args, **kwargs)


@register_op
def adjoint(input, *args, **kwargs):
    return torch.adjoint(input, *args, **kwargs)


@register_op
def argwhere(input, *args, **kwargs):
    return torch.argwhere(input, *args, **kwargs)


@register_op
def cat(input, *args, **kwargs):
    return torch.cat(input, *args, **kwargs)


@register_op
def concat(input, *args, **kwargs):
    return torch.concat(input, *args, **kwargs)


@register_op
def concatenate(input, *args, **kwargs):
    return torch.concatenate(input, *args, **kwargs)


@register_op
def conj(input, *args, **kwargs):
    return torch.conj(input, *args, **kwargs)



@register_op
def chunk(input, *args, **kwargs):
    return torch.chunk(input, *args, **kwargs)



@register_op
def dsplit(input, *args, **kwargs):
    return torch.dsplit(input, *args, **kwargs)



@register_op
def column_stack(input, *args, **kwargs):
    return torch.column_stack(input, *args, **kwargs)



@register_op
def dstack(input, *args, **kwargs):
    return torch.dstack(input, *args, **kwargs)



@register_op
def gather(arr, idx, dim=0, batched=True, axis=None):
    if axis is not None:
        dim = axis
    if idx.ndim > 1:
        shape = idx.shape
        if batched:
            return torch.gather(arr, dim, idx.reshape((1, -1))).reshape(shape)
        else:
            return torch.gather(arr, dim, idx.reshape((-1, ))).reshape(shape)
    return torch.gather(arr, dim, idx)


@register_op
def gather_dim1(input_tensor, index):
    """
    在 dim=1 (A维度) 上收集数据
    输入: 
        input_tensor: 形状 (B, A, D)
        index: 形状 (A,), 值范围 [0, A-1]
    输出: 形状 (B, A, D)
    """
    B, A, D = input_tensor.shape
    # 扩展索引维度并广播至与输入匹配
    index_expanded = index.view(1, A, 1).expand(B, A, D)
    return torch.gather(input_tensor, dim=1, index=index_expanded)


@register_op
def gather_nd(params, indices):
    # 将索引最后一维作为坐标维度（此处为2）
    idx_shape = indices.shape
    params_dim = params.dim()
    
    # 计算线性索引（将多维坐标展平为一维）
    idx = indices.view(-1, idx_shape[-1]).t()  # 转置为 [2, 16]
    linear_idx = idx[0] * params.size(1) + idx[1]  # 计算一维偏移：行索引 * 列数 + 列索引
    
    # 从展平后的张量取值并还原形状
    return params.view(-1)[linear_idx].view(idx_shape[:-1])


@register_op
def hsplit(input, *args, **kwargs):
    return torch.hsplit(input, *args, **kwargs)



@register_op
def hstack(input, *args, **kwargs):
    return torch.hstack(input, *args, **kwargs)



@register_op
def index_add(input, *args, **kwargs):
    return torch.index_add(input, *args, **kwargs)



@register_op
def index_copy(input, *args, **kwargs):
    return torch.index_copy(input, *args, **kwargs)



@register_op
def index_reduce(input, *args, **kwargs):
    return torch.index_reduce(input, *args, **kwargs)



@register_op
def index_select(input, *args, **kwargs):
    return torch.index_select(input, *args, **kwargs)



@register_op
def masked_select(input, *args, **kwargs):
    return torch.masked_select(input, *args, **kwargs)



@register_op
def movedim(input, *args, **kwargs):
    return torch.movedim(input, *args, **kwargs)



@register_op
def moveaxis(input, *args, **kwargs):
    return torch.moveaxis(input, *args, **kwargs)



@register_op
def narrow(input, *args, **kwargs):
    return torch.narrow(input, *args, **kwargs)



@register_op
def narrow_copy(input, *args, **kwargs):
    return torch.narrow_copy(input, *args, **kwargs)



@register_op
def nonzero(input, *args, **kwargs):
    return torch.nonzero(input, *args, **kwargs)



@register_op
def permute(input, *args, **kwargs):
    return torch.permute(input, *args, **kwargs)



@register_op
def reshape(input, *args, **kwargs):
    return torch.reshape(input, *args, **kwargs)



@register_op
def row_stack(input, *args, **kwargs):
    return torch.row_stack(input, *args, **kwargs)



@register_op
def select(input, *args, **kwargs):
    return torch.select(input, *args, **kwargs)



@register_op
def scatter(input, *args, **kwargs):
    return torch.scatter(input, *args, **kwargs)



@register_op
def diagonal_scatter(input, *args, **kwargs):
    return torch.diagonal_scatter(input, *args, **kwargs)



@register_op
def select_scatter(input, *args, **kwargs):
    return torch.select_scatter(input, *args, **kwargs)



@register_op
def slice_scatter(input, *args, **kwargs):
    return torch.slice_scatter(input, *args, **kwargs)



@register_op
def scatter_add(input, *args, **kwargs):
    return torch.scatter_add(input, *args, **kwargs)


@register_op
def tensor_scatter_add(arr, idx, src):
    if arr.ndim != idx.shape[-1]:
        raise IndexError("The index dimension {} is not equal to arr dims {}.".format(idx.shape[-1], arr.ndim))
    if src.ndim != 1 or src.shape[0] != idx.shape[0]:
        raise IndexError("The src tensor shape {} is wrong.".format(src.shape))
    if arr.ndim == 1:
        arr[idx] += src
    elif arr.ndim == 2:
        arr[idx[:, 0], idx[:, 1]] += src
    elif arr.ndim == 3:
        arr[idx[:, 0], idx[:, 1], idx[:, 2]] += src
    elif arr.ndim == 4:
        arr[idx[:, 0], idx[:, 1], idx[:, 2], idx[:, 3]] += src
    else:
        raise IndexError("The dimension {} is not supported for now!".format(arr.ndim))
    return arr


@register_op
def scatter_reduce(input, *args, **kwargs):
    return torch.scatter_reduce(input, *args, **kwargs)



@register_op
def split(input, *args, **kwargs):
    return torch.split(input, *args, **kwargs)



@register_op
def squeeze(input, *args, **kwargs):
    return torch.squeeze(input, *args, **kwargs)



@register_op
def stack(input, *args, **kwargs):
    return torch.stack(input, *args, **kwargs)



@register_op
def swapaxes(input, *args, **kwargs):
    return torch.swapaxes(input, *args, **kwargs)



@register_op
def swapdims(input, *args, **kwargs):
    return torch.swapdims(input, *args, **kwargs)



@register_op
def t(input, *args, **kwargs):
    return torch.t(input, *args, **kwargs)


@register_op
def take(input, *args, **kwargs):
    return torch.take(input, *args, **kwargs)


@register_op
def take_along_dim(input, indices, dim=None, **kwargs):
    return torch.take_along_dim(input, indices.to(long), dim=dim, **kwargs)


@register_op
def take_along_axis(input, indices, axis=None, **kwargs):
    return torch.take_along_dim(input, indices.to(long), dim=axis, **kwargs)


@register_op
def tensor_split(input, *args, **kwargs):
    return torch.tensor_split(input, *args, **kwargs)



@register_op
def tile(input, *args, **kwargs):
    return torch.tile(input, *args, **kwargs)



@register_op
def transpose(input, *args, **kwargs):
    return torch.transpose(input, *args, **kwargs)



@register_op
def unbind(input, *args, **kwargs):
    return torch.unbind(input, *args, **kwargs)



@register_op
def unravel_index(input, *args, **kwargs):
    return torch.unravel_index(input, *args, **kwargs)



@register_op
def unsqueeze(input, *args, **kwargs):
    return torch.unsqueeze(input, *args, **kwargs)



@register_op
def vsplit(input, *args, **kwargs):
    return torch.vsplit(input, *args, **kwargs)



@register_op
def vstack(input, *args, **kwargs):
    return torch.vstack(input, *args, **kwargs)



@register_op
def where(input, *args, **kwargs):
    return torch.where(input, *args, **kwargs)


@register_op
def Stream(input, *args, **kwargs):
    return torch.Stream(input, *args, **kwargs)



@register_op
def Event(input, *args, **kwargs):
    return torch.Event(input, *args, **kwargs)



@register_op
def Generator(input, *args, **kwargs):
    return torch.Generator(input, *args, **kwargs)



@register_op
def seed(input, *args, **kwargs):
    return torch.seed(input, *args, **kwargs)



@register_op
def manual_seed(input, *args, **kwargs):
    return torch.manual_seed(input, *args, **kwargs)



@register_op
def initial_seed(input, *args, **kwargs):
    return torch.initial_seed(input, *args, **kwargs)



@register_op
def get_rng_state(input, *args, **kwargs):
    return torch.get_rng_state(input, *args, **kwargs)



@register_op
def set_rng_state(input, *args, **kwargs):
    return torch.set_rng_state(input, *args, **kwargs)



@register_op
def bernoulli(input, *args, **kwargs):
    return torch.bernoulli(input, *args, **kwargs)



@register_op
def multinomial(input, *args, **kwargs):
    return torch.multinomial(input, *args, **kwargs)



@register_op
def normal(input, *args, **kwargs):
    return torch.normal(input, *args, **kwargs)



@register_op
def poisson(input, *args, **kwargs):
    return torch.poisson(input, *args, **kwargs)


@register_op
def rand(input, *args, **kwargs):
    return torch.rand(input, *args, **kwargs)


@register_op
def rand_like(input, *args, **kwargs):
    return torch.rand_like(input, *args, **kwargs)


@register_op
def randint(input, *args, **kwargs):
    return torch.randint(input, *args, **kwargs)


@register_op
def randint_like(input, *args, **kwargs):
    return torch.randint_like(input, *args, **kwargs)


@register_op
def randn(input, *args, **kwargs):
    return torch.randn(input, *args, **kwargs)


@register_op
def randn_like(input, *args, **kwargs):
    return torch.randn_like(input, *args, **kwargs)


@register_op
def randperm(input, *args, **kwargs):
    return torch.randperm(input, *args, **kwargs)


@register_op
def save(input, *args, **kwargs):
    return torch.save(input, *args, **kwargs)


@register_op
def load(input, *args, **kwargs):
    return torch.load(input, *args, **kwargs)


@register_op
def get_num_threads(input, *args, **kwargs):
    return torch.get_num_threads(input, *args, **kwargs)


@register_op
def set_num_threads(input, *args, **kwargs):
    return torch.set_num_threads(input, *args, **kwargs)


@register_op
def get_num_interop_threads(input, *args, **kwargs):
    return torch.get_num_interop_threads(input, *args, **kwargs)


@register_op
def set_num_interop_threads(input, *args, **kwargs):
    return torch.set_num_interop_threads(input, *args, **kwargs)


@register_op
def no_grad(*args, **kwargs):
    return torch.no_grad(*args, **kwargs)


@register_op
def enable_grad(input, *args, **kwargs):
    return torch.enable_grad(input, *args, **kwargs)


@register_op
def is_grad_enabled(input, *args, **kwargs):
    return torch.is_grad_enabled(input, *args, **kwargs)


@register_op
def is_inference_mode_enabled(input, *args, **kwargs):
    return torch.is_inference_mode_enabled(input, *args, **kwargs)


@register_op
def Abs(input, *args, **kwargs):
    return torch.abs(input, *args, **kwargs)


@register_op
def cbrt(input):
    return torch.sign(input) * input ** (1/3)


@register_op
def absolute(input, *args, **kwargs):
    return torch.absolute(input, *args, **kwargs)


@register_op
def acos(input, *args, **kwargs):
    return torch.acos(input, *args, **kwargs)


@register_op
def arccos(input, *args, **kwargs):
    return torch.arccos(input, *args, **kwargs)


@register_op
def acosh(input, *args, **kwargs):
    return torch.acosh(input, *args, **kwargs)


@register_op
def arccosh(input, *args, **kwargs):
    return torch.arccosh(input, *args, **kwargs)


@register_op
def add(input, *args, **kwargs):
    return torch.add(input, *args, **kwargs)


@register_op
def addcdiv(input, *args, **kwargs):
    return torch.addcdiv(input, *args, **kwargs)


@register_op
def addcmul(input, *args, **kwargs):
    return torch.addcmul(input, *args, **kwargs)


@register_op
def angle(input, *args, **kwargs):
    return torch.angle(input, *args, **kwargs)


@register_op
def asin(input, *args, **kwargs):
    return torch.asin(input, *args, **kwargs)


@register_op
def arcsin(input, *args, **kwargs):
    return torch.arcsin(input, *args, **kwargs)


@register_op
def asinh(input, *args, **kwargs):
    return torch.asinh(input, *args, **kwargs)


@register_op
def arcsinh(input, *args, **kwargs):
    return torch.arcsinh(input, *args, **kwargs)


@register_op
def atan(input, *args, **kwargs):
    return torch.atan(input, *args, **kwargs)


@register_op
def arctan(input, *args, **kwargs):
    return torch.arctan(input, *args, **kwargs)


@register_op
def atanh(input, *args, **kwargs):
    return torch.atanh(input, *args, **kwargs)


@register_op
def arctanh(input, *args, **kwargs):
    return torch.arctanh(input, *args, **kwargs)


@register_op
def atan2(input, *args, **kwargs):
    return torch.atan2(input, *args, **kwargs)


@register_op
def arctan2(input, *args, **kwargs):
    return torch.arctan2(input, *args, **kwargs)


@register_op
def bitwise_not(input, *args, **kwargs):
    return torch.bitwise_not(input, *args, **kwargs)


@register_op
def bitwise_and(input, *args, **kwargs):
    return torch.bitwise_and(input, *args, **kwargs)


@register_op
def bitwise_or(input, *args, **kwargs):
    return torch.bitwise_or(input, *args, **kwargs)


@register_op
def bitwise_xor(input, *args, **kwargs):
    return torch.bitwise_xor(input, *args, **kwargs)


@register_op
def bitwise_left_shift(input, *args, **kwargs):
    return torch.bitwise_left_shift(input, *args, **kwargs)


@register_op
def bitwise_right_shift(input, *args, **kwargs):
    return torch.bitwise_right_shift(input, *args, **kwargs)


@register_op
def ceil(input, *args, **kwargs):
    return torch.ceil(input, *args, **kwargs)


@register_op
def clamp(input, *args, **kwargs):
    return torch.clamp(input, *args, **kwargs)


@register_op
def clip(input, *args, **kwargs):
    return torch.clip(input, *args, **kwargs)


@register_op
def conj_physical(input, *args, **kwargs):
    return torch.conj_physical(input, *args, **kwargs)


@register_op
def copysign(input, *args, **kwargs):
    return torch.copysign(input, *args, **kwargs)


@register_op
def cos(input, *args, **kwargs):
    return torch.cos(input, *args, **kwargs)


@register_op
def cosh(input, *args, **kwargs):
    return torch.cosh(input, *args, **kwargs)


@register_op
def deg2rad(input, *args, **kwargs):
    return torch.deg2rad(input, *args, **kwargs)


@register_op
def div(input, *args, **kwargs):
    return torch.div(input, *args, **kwargs)


@register_op
def divide(input, *args, **kwargs):
    return torch.divide(input, *args, **kwargs)


@register_op
def digamma(input, *args, **kwargs):
    return torch.digamma(input, *args, **kwargs)


@register_op
def erf(input, *args, **kwargs):
    return torch.erf(input, *args, **kwargs)


@register_op
def erfc(input, *args, **kwargs):
    return torch.erfc(input, *args, **kwargs)


@register_op
def erfinv(input, *args, **kwargs):
    return torch.erfinv(input, *args, **kwargs)


@register_op
def exp(input, *args, **kwargs):
    return torch.exp(input, *args, **kwargs)


@register_op
def exp2(input, *args, **kwargs):
    return torch.exp2(input, *args, **kwargs)


@register_op
def expm1(input, *args, **kwargs):
    return torch.expm1(input, *args, **kwargs)


@register_op
def fake_quantize_per_channel_affine(input, *args, **kwargs):
    return torch.fake_quantize_per_channel_affine(input, *args, **kwargs)


@register_op
def fake_quantize_per_tensor_affine(input, *args, **kwargs):
    return torch.fake_quantize_per_tensor_affine(input, *args, **kwargs)


@register_op
def fix(input, *args, **kwargs):
    return torch.fix(input, *args, **kwargs)


@register_op
def float_power(input, *args, **kwargs):
    return torch.float_power(input, *args, **kwargs)


@register_op
def floor(input, *args, **kwargs):
    return torch.floor(input, *args, **kwargs)


@register_op
def floor_divide(A, B, rounding_mode='floor'):
    return torch.div(A, B, rounding_mode=rounding_mode)


@register_op
def fmod(input, *args, **kwargs):
    return torch.fmod(input, *args, **kwargs)


@register_op
def frac(input, *args, **kwargs):
    return torch.frac(input, *args, **kwargs)


@register_op
def frexp(input, *args, **kwargs):
    return torch.frexp(input, *args, **kwargs)


@register_op
def imag(input, *args, **kwargs):
    return torch.imag(input, *args, **kwargs)


@register_op
def ldexp(input, *args, **kwargs):
    return torch.ldexp(input, *args, **kwargs)


@register_op
def lerp(input, *args, **kwargs):
    return torch.lerp(input, *args, **kwargs)


@register_op
def lgamma(input, *args, **kwargs):
    return torch.lgamma(input, *args, **kwargs)


@register_op
def log(input, *args, **kwargs):
    return torch.log(input, *args, **kwargs)


@register_op
def log10(input, *args, **kwargs):
    return torch.log10(input, *args, **kwargs)


@register_op
def log1p(input, *args, **kwargs):
    return torch.log1p(input, *args, **kwargs)


@register_op
def log2(input, *args, **kwargs):
    return torch.log2(input, *args, **kwargs)


@register_op
def logaddexp(input, *args, **kwargs):
    return torch.logaddexp(input, *args, **kwargs)


@register_op
def logaddexp2(input, *args, **kwargs):
    return torch.logaddexp2(input, *args, **kwargs)


@register_op
def logical_and(input, *args, **kwargs):
    return torch.logical_and(input, *args, **kwargs)


@register_op
def logical_not(input, *args, **kwargs):
    return torch.logical_not(input, *args, **kwargs)


@register_op
def logical_or(input, *args, **kwargs):
    return torch.logical_or(input, *args, **kwargs)


@register_op
def logical_xor(input, *args, **kwargs):
    return torch.logical_xor(input, *args, **kwargs)


@register_op
def logit(input, *args, **kwargs):
    return torch.logit(input, *args, **kwargs)


@register_op
def hypot(input, *args, **kwargs):
    return torch.hypot(input, *args, **kwargs)


@register_op
def i0(input, *args, **kwargs):
    return torch.i0(input, *args, **kwargs)


@register_op
def igamma(input, *args, **kwargs):
    return torch.igamma(input, *args, **kwargs)


@register_op
def igammac(input, *args, **kwargs):
    return torch.igammac(input, *args, **kwargs)


@register_op
def mul(input, *args, **kwargs):
    return torch.mul(input, *args, **kwargs)


@register_op
def multiply(input, *args, **kwargs):
    return torch.multiply(input, *args, **kwargs)


@register_op
def mvlgamma(input, *args, **kwargs):
    return torch.mvlgamma(input, *args, **kwargs)


@register_op
def nan_to_num(input, *args, **kwargs):
    return torch.nan_to_num(input, *args, **kwargs)


@register_op
def neg(input, *args, **kwargs):
    return torch.neg(input, *args, **kwargs)


@register_op
def negative(input, *args, **kwargs):
    return torch.negative(input, *args, **kwargs)


@register_op
def nextafter(input, *args, **kwargs):
    return torch.nextafter(input, *args, **kwargs)


@register_op
def polygamma(input, *args, **kwargs):
    return torch.polygamma(input, *args, **kwargs)


@register_op
def positive(input, *args, **kwargs):
    return torch.positive(input, *args, **kwargs)


@register_op
def Pow(input, exponent, out=None):
    return torch.pow(input, exponent, out=out)


@register_op
def quantized_batch_norm(input, *args, **kwargs):
    return torch.quantized_batch_norm(input, *args, **kwargs)


@register_op
def quantized_max_pool1d(input, *args, **kwargs):
    return torch.quantized_max_pool1d(input, *args, **kwargs)


@register_op
def quantized_max_pool2d(input, *args, **kwargs):
    return torch.quantized_max_pool2d(input, *args, **kwargs)


@register_op
def rad2deg(input, *args, **kwargs):
    return torch.rad2deg(input, *args, **kwargs)


@register_op
def real(input, *args, **kwargs):
    return torch.real(input, *args, **kwargs)


@register_op
def reciprocal(input, *args, **kwargs):
    return torch.reciprocal(input, *args, **kwargs)


@register_op
def remainder(input, *args, **kwargs):
    return torch.remainder(input, *args, **kwargs)


@register_op
def round(input, *args, **kwargs):
    return torch.round(input, *args, **kwargs)


@register_op
def rsqrt(input, *args, **kwargs):
    return torch.rsqrt(input, *args, **kwargs)


@register_op
def sigmoid(input, *args, **kwargs):
    return torch.sigmoid(input, *args, **kwargs)


@register_op
def sign(input, *args, **kwargs):
    return torch.sign(input, *args, **kwargs)


@register_op
def sgn(input, *args, **kwargs):
    return torch.sgn(input, *args, **kwargs)


@register_op
def signbit(input, *args, **kwargs):
    return torch.signbit(input, *args, **kwargs)


@register_op
def sin(input, *args, **kwargs):
    return torch.sin(input, *args, **kwargs)


@register_op
def sinc(input, *args, **kwargs):
    return torch.sinc(input, *args, **kwargs)


@register_op
def sinh(input, *args, **kwargs):
    return torch.sinh(input, *args, **kwargs)


@register_op
def softmax(input, *args, **kwargs):
    return torch.softmax(input, *args, **kwargs)


@register_op
def sqrt(input, *args, **kwargs):
    return torch.sqrt(input, *args, **kwargs)


@register_op
def square(input, *args, **kwargs):
    return torch.square(input, *args, **kwargs)


@register_op
def sub(input, *args, **kwargs):
    return torch.sub(input, *args, **kwargs)


@register_op
def subtract(input, *args, **kwargs):
    return torch.subtract(input, *args, **kwargs)


@register_op
def tan(input, *args, **kwargs):
    return torch.tan(input, *args, **kwargs)


@register_op
def tanh(input, *args, **kwargs):
    return torch.tanh(input, *args, **kwargs)


@register_op
def true_divide(input, *args, **kwargs):
    return torch.true_divide(input, *args, **kwargs)


@register_op
def trunc(input, *args, **kwargs):
    return torch.trunc(input, *args, **kwargs)


@register_op
def xlogy(input, *args, **kwargs):
    return torch.xlogy(input, *args, **kwargs)


@register_op
def argmax(input, *args, **kwargs):
    return torch.argmax(input, *args, **kwargs)


@register_op
def argmin(input, *args, **kwargs):
    return torch.argmin(input, *args, **kwargs)


@register_op
def amax(input, *args, **kwargs):
    return torch.amax(input, *args, **kwargs)


@register_op
def amin(input, *args, **kwargs):
    return torch.amin(input, *args, **kwargs)


@register_op
def aminmax(input, *args, **kwargs):
    return torch.aminmax(input, *args, **kwargs)


@register_op
def All(input, *args, **kwargs):
    return torch.all(input, *args, **kwargs)


@register_op
def Any(input, *args, **kwargs):
    return torch.any(input, *args, **kwargs)


@register_op
def Max(input, *args, **kwargs):
    return torch.max(input, *args, **kwargs)


@register_op
def Min(input, *args, **kwargs):
    return torch.min(input, *args, **kwargs)


@register_op
def dist(input, *args, **kwargs):
    return torch.dist(input, *args, **kwargs)


@register_op
def logsumexp(input, *args, **kwargs):
    return torch.logsumexp(input, *args, **kwargs)


@register_op
def mean(input, *args, **kwargs):
    return torch.mean(input, *args, **kwargs)


@register_op
def nanmean(input, *args, **kwargs):
    return torch.nanmean(input, *args, **kwargs)


@register_op
def median(input, *args, **kwargs):
    return torch.median(input, *args, **kwargs)


@register_op
def nanmedian(input, *args, **kwargs):
    return torch.nanmedian(input, *args, **kwargs)


@register_op
def mode(input, *args, **kwargs):
    return torch.mode(input, *args, **kwargs)


@register_op
def norm(input, *args, **kwargs):
    return torch.norm(input, *args, **kwargs)


@register_op
def nansum(input, *args, **kwargs):
    return torch.nansum(input, *args, **kwargs)


@register_op
def prod(input, *args, **kwargs):
    return torch.prod(input, *args, **kwargs)


@register_op
def quantile(input, *args, **kwargs):
    return torch.quantile(input, *args, **kwargs)


@register_op
def nanquantile(input, *args, **kwargs):
    return torch.nanquantile(input, *args, **kwargs)


@register_op
def std(input, *args, **kwargs):
    return torch.std(input, *args, **kwargs)


@register_op
def std_mean(input, *args, **kwargs):
    return torch.std_mean(input, *args, **kwargs)



@register_op
def unique(input, *args, **kwargs):
    return torch.unique(input, *args, **kwargs)


@register_op
def unique_consecutive(input, *args, **kwargs):
    return torch.unique_consecutive(input, *args, **kwargs)


@register_op
def var(input, *args, **kwargs):
    return torch.var(input, *args, **kwargs)


@register_op
def var_mean(input, *args, **kwargs):
    return torch.var_mean(input, *args, **kwargs)


@register_op
def count_nonzero(input, *args, **kwargs):
    return torch.count_nonzero(input, *args, **kwargs)


@register_op
def allclose(input, *args, **kwargs):
    return torch.allclose(input, *args, **kwargs)


@register_op
def argsort(input, *args, **kwargs):
    return torch.argsort(input, *args, **kwargs)


@register_op
def eq(input, *args, **kwargs):
    return torch.eq(input, *args, **kwargs)


@register_op
def equal(input, *args, **kwargs):
    return torch.equal(input, *args, **kwargs)


@register_op
def ge(input, *args, **kwargs):
    return torch.ge(input, *args, **kwargs)


@register_op
def greater_equal(input, *args, **kwargs):
    return torch.greater_equal(input, *args, **kwargs)


@register_op
def gt(input, *args, **kwargs):
    return torch.gt(input, *args, **kwargs)


@register_op
def greater(input, *args, **kwargs):
    return torch.greater(input, *args, **kwargs)


@register_op
def isclose(input, *args, **kwargs):
    return torch.isclose(input, *args, **kwargs)


@register_op
def isfinite(input, *args, **kwargs):
    return torch.isfinite(input, *args, **kwargs)


@register_op
def isin(input, *args, **kwargs):
    return torch.isin(input, *args, **kwargs)


@register_op
def isinf(input, *args, **kwargs):
    return torch.isinf(input, *args, **kwargs)


@register_op
def isposinf(input, *args, **kwargs):
    return torch.isposinf(input, *args, **kwargs)


@register_op
def isneginf(input, *args, **kwargs):
    return torch.isneginf(input, *args, **kwargs)


@register_op
def isnan(input, *args, **kwargs):
    return torch.isnan(input, *args, **kwargs)


@register_op
def isreal(input, *args, **kwargs):
    return torch.isreal(input, *args, **kwargs)


@register_op
def kthvalue(input, *args, **kwargs):
    return torch.kthvalue(input, *args, **kwargs)


@register_op
def le(input, *args, **kwargs):
    return torch.le(input, *args, **kwargs)


@register_op
def less_equal(input, *args, **kwargs):
    return torch.less_equal(input, *args, **kwargs)


@register_op
def lt(input, *args, **kwargs):
    return torch.lt(input, *args, **kwargs)


@register_op
def less(input, *args, **kwargs):
    return torch.less(input, *args, **kwargs)


@register_op
def maximum(input, *args, **kwargs):
    return torch.maximum(input, *args, **kwargs)


@register_op
def minimum(input, *args, **kwargs):
    return torch.minimum(input, *args, **kwargs)


@register_op
def fmax(input, *args, **kwargs):
    return torch.fmax(input, *args, **kwargs)


@register_op
def fmin(input, *args, **kwargs):
    return torch.fmin(input, *args, **kwargs)


@register_op
def ne(input, *args, **kwargs):
    return torch.ne(input, *args, **kwargs)


@register_op
def not_equal(input, *args, **kwargs):
    return torch.not_equal(input, *args, **kwargs)


@register_op
def sort(input, *args, **kwargs):
    return torch.sort(input, *args, **kwargs)


@register_op
def topk(input, *args, **kwargs):
    return torch.topk(input, *args, **kwargs)


@register_op
def cast(arr, dtype):
    if dtype==int64:
        return arr.long()
    arr.to(dtype)
    return arr


@register_op
def msort(input, *args, **kwargs):
    return torch.msort(input, *args, **kwargs)


@register_op
def stft(input, *args, **kwargs):
    return torch.stft(input, *args, **kwargs)


@register_op
def istft(input, *args, **kwargs):
    return torch.istft(input, *args, **kwargs)


@register_op
def bartlett_window(input, *args, **kwargs):
    return torch.bartlett_window(input, *args, **kwargs)


@register_op
def blackman_window(input, *args, **kwargs):
    return torch.blackman_window(input, *args, **kwargs)


@register_op
def hamming_window(input, *args, **kwargs):
    return torch.hamming_window(input, *args, **kwargs)


@register_op
def hann_window(input, *args, **kwargs):
    return torch.hann_window(input, *args, **kwargs)


@register_op
def kaiser_window(input, *args, **kwargs):
    return torch.kaiser_window(input, *args, **kwargs)


@register_op
def atleast_1d(input, *args, **kwargs):
    return torch.atleast_1d(input, *args, **kwargs)


@register_op
def atleast_2d(input, *args, **kwargs):
    return torch.atleast_2d(input, *args, **kwargs)


@register_op
def atleast_3d(input, *args, **kwargs):
    return torch.atleast_3d(input, *args, **kwargs)


@register_op
def bincount(input, *args, **kwargs):
    return torch.bincount(input, *args, **kwargs)


@register_op
def block_diag(input, *args, **kwargs):
    return torch.block_diag(input, *args, **kwargs)


@register_op
def broadcast_tensors(input, *args, **kwargs):
    return torch.broadcast_tensors(input, *args, **kwargs)


@register_op
def broadcast_to(input, *args, **kwargs):
    return torch.broadcast_to(input, *args, **kwargs)


@register_op
def broadcast_shapes(input, *args, **kwargs):
    return torch.broadcast_shapes(input, *args, **kwargs)


@register_op
def bucketize(input, *args, **kwargs):
    return torch.bucketize(input, *args, **kwargs)


@register_op
def cartesian_prod(input, *args, **kwargs):
    return torch.cartesian_prod(input, *args, **kwargs)


@register_op
def cdist(input, *args, **kwargs):
    return torch.cdist(input, *args, **kwargs)


@register_op
def clone(input, *args, **kwargs):
    return torch.clone(input, *args, **kwargs)


@register_op
def combinations(input, *args, **kwargs):
    return torch.combinations(input, *args, **kwargs)


@register_op
def r(input, *args, **kwargs):
    return torch.r(input, *args, **kwargs)


@register_op
def corrcoef(input, *args, **kwargs):
    return torch.corrcoef(input, *args, **kwargs)


@register_op
def cov(input, *args, **kwargs):
    return torch.cov(input, *args, **kwargs)


@register_op
def cross(input, *args, **kwargs):
    return torch.linalg.cross(input, *args, **kwargs)


@register_op
def cummax(input, *args, **kwargs):
    return torch.cummax(input, *args, **kwargs)


@register_op
def cummin(input, *args, **kwargs):
    return torch.cummin(input, *args, **kwargs)


@register_op
def cumprod(input, *args, **kwargs):
    return torch.cumprod(input, *args, **kwargs)


@register_op
def cumsum(input, *args, **kwargs):
    return torch.cumsum(input, *args, **kwargs)


@register_op
def diag(input, *args, **kwargs):
    return torch.diag(input, *args, **kwargs)


@register_op
def diag_embed(input, *args, **kwargs):
    return torch.diag_embed(input, *args, **kwargs)


@register_op
def diagflat(input, *args, **kwargs):
    return torch.diagflat(input, *args, **kwargs)


@register_op
def diagonal(input, *args, **kwargs):
    return torch.diagonal(input, *args, **kwargs)


@register_op
def diff(input, *args, **kwargs):
    return torch.diff(input, *args, **kwargs)


@register_op
def einsum(input, *args, **kwargs):
    return torch.einsum(input, *args, **kwargs)


@register_op
def flatten(input, *args, **kwargs):
    return torch.flatten(input, *args, **kwargs)


@register_op
def flip(input, *args, **kwargs):
    return torch.flip(input, *args, **kwargs)


@register_op
def fliplr(input, *args, **kwargs):
    return torch.fliplr(input, *args, **kwargs)


@register_op
def flipud(input, *args, **kwargs):
    return torch.flipud(input, *args, **kwargs)


@register_op
def kron(input, *args, **kwargs):
    return torch.kron(input, *args, **kwargs)


@register_op
def rot90(input, *args, **kwargs):
    return torch.rot90(input, *args, **kwargs)


@register_op
def gcd(input, *args, **kwargs):
    return torch.gcd(input, *args, **kwargs)


@register_op
def histc(input, *args, **kwargs):
    return torch.histc(input, *args, **kwargs)


@register_op
def histogram(input, *args, **kwargs):
    return torch.histogram(input, *args, **kwargs)


@register_op
def histogramdd(input, *args, **kwargs):
    return torch.histogramdd(input, *args, **kwargs)


@register_op
def meshgrid(input, *args, **kwargs):
    return torch.meshgrid(input, *args, **kwargs)


@register_op
def lcm(input, *args, **kwargs):
    return torch.lcm(input, *args, **kwargs)


@register_op
def logcumsumexp(input, *args, **kwargs):
    return torch.logcumsumexp(input, *args, **kwargs)


@register_op
def ravel(input, *args, **kwargs):
    return torch.ravel(input, *args, **kwargs)


@register_op
def renorm(input, *args, **kwargs):
    return torch.renorm(input, *args, **kwargs)


@register_op
def repeat_interleave(input, *args, **kwargs):
    return torch.repeat_interleave(input, *args, **kwargs)


@register_op
def roll(input, *args, **kwargs):
    return torch.roll(input, *args, **kwargs)


@register_op
def searchsorted(input, *args, **kwargs):
    return torch.searchsorted(input, *args, **kwargs)


@register_op
def tensordot(input, *args, **kwargs):
    return torch.tensordot(input, *args, **kwargs)


@register_op
def trace(input, *args, **kwargs):
    return torch.trace(input, *args, **kwargs)


@register_op
def tril(input, *args, **kwargs):
    return torch.tril(input, *args, **kwargs)


@register_op
def tril_indices(input, *args, **kwargs):
    return torch.tril_indices(input, *args, **kwargs)


@register_op
def triu(input, *args, **kwargs):
    return torch.triu(input, *args, **kwargs)


@register_op
def triu_indices(input, *args, **kwargs):
    return torch.triu_indices(input, *args, **kwargs)


@register_op
def unflatten(input, *args, **kwargs):
    return torch.unflatten(input, *args, **kwargs)


@register_op
def vander(input, *args, **kwargs):
    return torch.vander(input, *args, **kwargs)


@register_op
def view_as_real(input, *args, **kwargs):
    return torch.view_as_real(input, *args, **kwargs)


@register_op
def view_as_complex(input, *args, **kwargs):
    return torch.view_as_complex(input, *args, **kwargs)


@register_op
def resolve_conj(input, *args, **kwargs):
    return torch.resolve_conj(input, *args, **kwargs)


@register_op
def resolve_neg(input, *args, **kwargs):
    return torch.resolve_neg(input, *args, **kwargs)


@register_op
def addbmm(input, *args, **kwargs):
    return torch.addbmm(input, *args, **kwargs)


@register_op
def addmm(input, *args, **kwargs):
    return torch.addmm(input, *args, **kwargs)


@register_op
def addmv(input, *args, **kwargs):
    return torch.addmv(input, *args, **kwargs)


@register_op
def addr(input, *args, **kwargs):
    return torch.addr(input, *args, **kwargs)


@register_op
def baddbmm(input, *args, **kwargs):
    return torch.baddbmm(input, *args, **kwargs)


@register_op
def bmm(input, *args, **kwargs):
    return torch.bmm(input, *args, **kwargs)


@register_op
def chain_matmul(input, *args, **kwargs):
    return torch.chain_matmul(input, *args, **kwargs)


@register_op
def cholesky(input, *args, **kwargs):
    return torch.cholesky(input, *args, **kwargs)


@register_op
def cholesky_inverse(input, *args, **kwargs):
    return torch.cholesky_inverse(input, *args, **kwargs)


@register_op
def cholesky_solve(input, *args, **kwargs):
    return torch.cholesky_solve(input, *args, **kwargs)


@register_op
def dot(input, *args, **kwargs):
    return torch.dot(input, *args, **kwargs)


@register_op
def geqrf(input, *args, **kwargs):
    return torch.geqrf(input, *args, **kwargs)


@register_op
def ger(input, *args, **kwargs):
    return torch.ger(input, *args, **kwargs)


@register_op
def inner(input, *args, **kwargs):
    return torch.inner(input, *args, **kwargs)


@register_op
def inverse(input, *args, **kwargs):
    return torch.inverse(input, *args, **kwargs)


@register_op
def pinv(input, *args, **kwargs):
    return torch.linalg.pinv(input, *args, **kwargs)


@register_op
def det(input, *args, **kwargs):
    return torch.det(input, *args, **kwargs)


@register_op
def logdet(input, *args, **kwargs):
    return torch.logdet(input, *args, **kwargs)


@register_op
def slogdet(input, *args, **kwargs):
    return torch.slogdet(input, *args, **kwargs)


@register_op
def lu(input, *args, **kwargs):
    return torch.lu(input, *args, **kwargs)


@register_op
def lu_solve(input, *args, **kwargs):
    return torch.lu_solve(input, *args, **kwargs)


@register_op
def lu_unpack(input, *args, **kwargs):
    return torch.lu_unpack(input, *args, **kwargs)


@register_op
def matmul(input, *args, **kwargs):
    return torch.matmul(input, *args, **kwargs)


@register_op
def matrix_power(input, *args, **kwargs):
    return torch.matrix_power(input, *args, **kwargs)


@register_op
def matrix_exp(input, *args, **kwargs):
    return torch.matrix_exp(input, *args, **kwargs)


@register_op
def mm(input, *args, **kwargs):
    return torch.mm(input, *args, **kwargs)


@register_op
def mv(input, *args, **kwargs):
    return torch.mv(input, *args, **kwargs)


@register_op
def orgqr(input, *args, **kwargs):
    return torch.orgqr(input, *args, **kwargs)


@register_op
def ormqr(input, *args, **kwargs):
    return torch.ormqr(input, *args, **kwargs)


@register_op
def outer(input, *args, **kwargs):
    return torch.outer(input, *args, **kwargs)


@register_op
def pinverse(input, *args, **kwargs):
    return torch.pinverse(input, *args, **kwargs)


@register_op
def qr(input, *args, **kwargs):
    return torch.qr(input, *args, **kwargs)


@register_op
def svd(input, *args, **kwargs):
    return torch.svd(input, *args, **kwargs)


@register_op
def svd_lowrank(input, *args, **kwargs):
    return torch.svd_lowrank(input, *args, **kwargs)


@register_op
def pca_lowrank(input, *args, **kwargs):
    return torch.pca_lowrank(input, *args, **kwargs)


@register_op
def lobpcg(input, *args, **kwargs):
    return torch.lobpcg(input, *args, **kwargs)


@register_op
def trapz(input, *args, **kwargs):
    return torch.trapz(input, *args, **kwargs)


@register_op
def trapezoid(input, *args, **kwargs):
    return torch.trapezoid(input, *args, **kwargs)


@register_op
def cumulative_trapezoid(input, *args, **kwargs):
    return torch.cumulative_trapezoid(input, *args, **kwargs)


@register_op
def triangular_solve(input, *args, **kwargs):
    return torch.triangular_solve(input, *args, **kwargs)


@register_op
def vdot(input, *args, **kwargs):
    return torch.vdot(input, *args, **kwargs)


@register_op
def compiled_with_cxx11_abi(input, *args, **kwargs):
    return torch.compiled_with_cxx11_abi(input, *args, **kwargs)

@register_op
def result_type(input, *args, **kwargs):
    return torch.result_type(input, *args, **kwargs)


@register_op
def can_cast(input, *args, **kwargs):
    return torch.can_cast(input, *args, **kwargs)


@register_op
def promote_types(input, *args, **kwargs):
    return torch.promote_types(input, *args, **kwargs)


@register_op
def use_deterministic_algorithms(input, *args, **kwargs):
    return torch.use_deterministic_algorithms(input, *args, **kwargs)


@register_op
def are_deterministic_algorithms_enabled(input, *args, **kwargs):
    return torch.are_deterministic_algorithms_enabled(input, *args, **kwargs)


@register_op
def is_deterministic_algorithms_warn_only_enabled(input, *args, **kwargs):
    return torch.is_deterministic_algorithms_warn_only_enabled(input, *args, **kwargs)


@register_op
def set_deterministic_debug_mode(input, *args, **kwargs):
    return torch.set_deterministic_debug_mode(input, *args, **kwargs)


@register_op
def get_deterministic_debug_mode(input, *args, **kwargs):
    return torch.get_deterministic_debug_mode(input, *args, **kwargs)


@register_op
def set_float32_matmul_precision(input, *args, **kwargs):
    return torch.set_float32_matmul_precision(input, *args, **kwargs)


@register_op
def get_float32_matmul_precision(input, *args, **kwargs):
    return torch.get_float32_matmul_precision(input, *args, **kwargs)


@register_op
def set_warn_always(input, *args, **kwargs):
    return torch.set_warn_always(input, *args, **kwargs)


@register_op
def get_device_module(input, *args, **kwargs):
    return torch.get_device_module(input, *args, **kwargs)


@register_op
def is_warn_always_enabled(input, *args, **kwargs):
    return torch.is_warn_always_enabled(input, *args, **kwargs)


@register_op
def vmap(input, *args, **kwargs):
    if 'in_axes' in kwargs:
        kwargs['in_dims'] = kwargs['in_axes']
        kwargs.pop('in_axes')
    if 'out_axes' in kwargs:
        kwargs['out_dims'] = kwargs['out_axes']
        kwargs.pop('out_axes')
    return torch.vmap(input, *args, **kwargs)


@register_op
def _assert(input, *args, **kwargs):
    return torch._assert(input, *args, **kwargs)


@register_op
def assign(variable, value):
    with torch.no_grad():
        variable.copy_(value)
    return variable


@register_op
def tensor_scatter_update(arr, index, src, dim=0, axis=None):
    if axis is not None:
        dim = axis
    return arr.scatter_(dim, index, src)


@register_op
def fft3d(input, *args, **kwargs):
    return torch.fft.fftn(input, dim=(-3, -2, -1))


@register_op
def ifft3d(input, *args, **kwargs):
    return torch.fft.ifftn(input, dim=(-3, -2, -1))


@register_op
def rfftn(input, *args, **kwargs):
    return torch.fft.rfftn(input, *args, **kwargs)


@register_op
def irfftn(input, *args, **kwargs):
    return torch.fft.irfftn(input, *args, **kwargs)


@register_op
def scatter_update(original, indices, updates):
    _, H, W, C = original.shape  # H=20, W=20, C=12
    i, j, k = indices[:, 1], indices[:, 2], indices[:, 3]
    
    # 计算线性索引 (确保为整数类型)
    linear_indices = (i * (W * C) + j * C + k).long()
    
    # 处理更新值维度
    updates_1d = updates.squeeze(1)  # 从 [n,1] -> [n]
    
    # 创建聚合缓冲区
    aggregated = torch.zeros(
        H * W * C, 
        dtype=updates.dtype, 
        device=updates.device
    )
    
    # 方案1: 统一维度后使用 scatter_add_
    linear_indices = linear_indices.view(-1)  # 确保1D
    updates_1d = updates_1d.view(-1)          # 确保1D
    aggregated.scatter_add_(0, linear_indices, updates_1d)
    
    # 方案2: 更推荐直接用 index_add_
    # aggregated.index_add_(0, linear_indices, updates_1d)
    
    # 更新原始张量
    original_flat = original.view(-1)
    original_flat += aggregated
    return original_flat.view(1, H, W, C)
