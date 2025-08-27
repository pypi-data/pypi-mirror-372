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


class MetaState(NamedTuple):
    xi: JaxArray
    bias: JaxArray
    idx: int
    ncalls: int
    stride: int

    def __repr__(self):
        return repr("PySAGES" + type(self).__name__)
    

class MetaDynamics(GriddedSamplingMethod):
    def __init__(
        self,
        cv,
        grid: Grid,
        height: float = 1,
        sigma: float = 0.1,      # 高斯核宽度
        gamma: float = 10.0,     # Well-Tempered因子
        stride: int = 100,       # 添加高斯间隔
        cv_bounds: list = None   # CV边界限制
    ):
        super().__init__(cv, grid)
        self.cv_bounds = cv_bounds  # 预设CV边界
        self.k = jnp.ones(self.grid.shape)
        self.stride = stride
        self.height = height
        self.sigma = sigma
        self.gamma = gamma
        self.dS = (self.cv_bounds[0][1] - self.cv_bounds[0][0]) / self.grid.shape
        self.centers = jnp.tile(jnp.arange(self.grid.shape[0]), (self.grid.shape.shape[0], 1)).T * self.dS + self.cv_bounds[0][0]

    def _compute_convolution_weights(self, s):
        # 计算网格点的高斯基函数权重 (公式5)
        distances = jnp.linalg.norm((self.centers - s) / self.sigma, axis=1)
        f = jnp.exp(-0.5 * distances**2)
        return f / jnp.sum(f)  # 归一化

    def _get_bias(self, s):
        # 计算当前CV点的偏置势能 (公式8)
        f = self._compute_convolution_weights(s)
        bias = jnp.dot(f, self.k) * self.height
        return bias
    
    def _compute_derivative(self, s):
        # 计算偏置力的梯度 (公式19)
        grad = jnp.zeros_like(s)
        centers = self.centers
        for i in range(len(centers)):
            s_i = centers[i]
            dist = (s - s_i) / self.sigma**2
            grad += self.k[i] * jnp.exp(-0.5 * jnp.linalg.norm(dist)**2) * dist
        return grad * self.height
    
    def build(self, snapshot, helpers, *args, **kwargs):
        cv = self.cv
        xi, _ = cv(helpers.query(snapshot))
        natoms = jnp.size(snapshot.positions, 0)
        bias = jnp.zeros((natoms, helpers.dimensionality()))

        def _initialize():
            return MetaState(xi, bias, 0, 0, self.stride)

        def _update_func(snapshot, state):
            state=state._replace(ncalls=state.ncalls+1)
            xi, _ = cv(helpers.query(snapshot))
            state = state._replace(xi=xi)
            bias = self._get_bias(xi)
            if (state.ncalls + 1) % state.stride == 0:
                # print (state.xi, bias)
                # self._update_bias(xi)
                # pass
                state = state._replace(bias=-self._compute_derivative(xi))
            return state

        return snapshot, _initialize, _update_func