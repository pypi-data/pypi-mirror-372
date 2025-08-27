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


import jax.numpy as jnp
from pysages import Grid
from pysages.methods.core import GriddedSamplingMethod
from pysages.typing import NamedTuple, JaxArray, Optional
from pysages.methods.core import generalize


class SinkMetadynamicsState(NamedTuple):
    xi: JaxArray
    bias: JaxArray
    idx: int
    ncalls: int
    stride: int

    def __repr__(self):
        return repr("PySAGES" + type(self).__name__)


class SinkMetaDynamics(GriddedSamplingMethod):
    def __init__(
        self,
        cv,
        grid: Grid,
        height: float = 1,
        E_depth: float = 25.0,  # 下沉深度 (kJ/mol)
        sigma: float = 0.1,      # 高斯核宽度
        gamma: float = 10.0,     # Well-Tempered因子
        deltaT: float = 2000.0, # 有效温度
        stride: int = 100,       # 添加高斯间隔
        cv_bounds: list = None   # CV边界限制
    ):
        super().__init__(cv, grid)
        self.E_depth = E_depth
        self.cv_bounds = cv_bounds  # 预设CV边界
        self.stride = stride
        self.height = height
        # 初始化网格权重和下沉参数
        self.k = jnp.zeros(self.grid.shape)  # 网格点权重
        self.v_shift = 0.0              # 势能偏移量
        self.sigma_prime = sigma / jnp.sqrt(2)  # 卷积高斯宽度
        self.dV = self.sigma_prime * jnp.sqrt(2*jnp.pi)
        # self.dS = self.grid.size / self.grid.shape
        self.dS = (self.cv_bounds[0][1] - self.cv_bounds[0][0]) / self.grid.shape
        self.centers = jnp.tile(jnp.arange(self.grid.shape[0]), (self.grid.shape.shape[0], 1)).T * self.dS + self.cv_bounds[0][0]
        
    def _compute_convolution_weights(self, s):
        # 计算网格点的高斯基函数权重 (公式5)
        distances = jnp.linalg.norm((self.centers - s) / self.sigma_prime, axis=1)
        f = jnp.exp(-0.5 * distances**2)
        return f / jnp.sum(f)  # 归一化
    
    def _update_bias(self, s):
        # 更新网格权重 (公式9)
        f = self._compute_convolution_weights(s)
        # delta_k = self.height * f / self.C
        delta_k = self.height * f
        self.k += delta_k
        
        # 计算势能偏移 (公式13)
        V_max = jnp.max(self.k * self.dV)
        self.v_shift = (V_max + self.E_depth) / self.dV.prod()
        
        # 应用下沉操作 (公式12)
        self.k = jnp.clip(self.k - self.v_shift, a_min=0.0)  # 防止负权重
        
    def _get_bias(self, s):
        # 计算当前CV点的偏置势能 (公式8)
        f = self._compute_convolution_weights(s)
        bias = jnp.dot(f, self.k) * self.dV
        return bias

    def _compute_derivative(self, s):
        # 计算偏置力的梯度 (公式19)
        grad = jnp.zeros_like(s)
        centers = self.centers
        for i in range(len(centers)):
            s_i = centers[i]
            dist = (s - s_i) / self.sigma_prime**2
            # print (s.shape, s_i.shape, self.k.shape, dist.shape)
            # (1, 2) (2,) (50, 50) (1, 2)
            grad += self.k[i] * jnp.exp(-0.5 * jnp.linalg.norm(dist)**2) * dist
        return grad * self.dV
    
    def build(self, snapshot, helpers, *args, **kwargs):
        cv = self.cv
        xi, _ = cv(helpers.query(snapshot))
        natoms = jnp.size(snapshot.positions, 0)
        bias = jnp.zeros((natoms, helpers.dimensionality()))

        def _initialize():
            return SinkMetadynamicsState(xi, bias, 0, 0, self.stride)

        def _update_func(snapshot, sinkstate):
            sinkstate=sinkstate._replace(ncalls=sinkstate.ncalls+1)
            xi, _ = cv(helpers.query(snapshot))
            sinkstate = sinkstate._replace(xi=xi)
            bias = self._get_bias(xi)
            if (sinkstate.ncalls + 1) % sinkstate.stride == 0:
                self._update_bias(xi)
                sinkstate = sinkstate._replace(bias=-self._compute_derivative(xi))
            return sinkstate

        return snapshot, _initialize, _update_func


def w(t):...
def C(ds, ft, D=1):
    return jnp.sum(ds*ft)/jnp.sqrt(2)**D

def _f(si, st, sigmab):
    return jnp.exp(-0.5*((si-st)/sigmab)**2)

def _g(si, sr, sigmab):
    return jnp.exp(-0.5*((sr-si)/sigmab)**2)

def G(si, sr, st, t, sigmab, ds):
    gauss_g = _g(si, sr, sigmab)
    gauss_f = _f(si, st, sigmab)
    sum_term = jnp.sum(ds*gauss_f*gauss_g)
    return w(t) * sum_term / C(ds, gauss_f)

def V(xi, t):
    return G(xi, t)