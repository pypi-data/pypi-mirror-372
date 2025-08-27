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


import warnings
import numpy as np
from collections import namedtuple

try:
    import Sponge
except ModuleNotFoundError:
    warnings.warn("Module Sponge not found!")

try:
    from jax import numpy as jnp
    from jax.dlpack import to_dlpack, from_dlpack
except ModuleNotFoundError:
    warnings.warn("Module jax not found!")

try:
    from cupy import fromDlpack as cufd
except ModuleNotFoundError:
    warnings.warn("Module cupy not found!")

try:
    from pysages.backends.snapshot import Snapshot, SnapshotMethods, HelperMethods, build_data_querier
except ModuleNotFoundError:
    warnings.warn("Module pysages not found!")

def build_sponge_snapshot_methods():
    def positions(snapshot):
        return snapshot.positions
    def indices(snapshot):
        return snapshot.ids
    return SnapshotMethods(positions, indices, None, None)

def build_sponge_snapshot(num_atoms):
    crd = jnp.array(np.random.random((num_atoms, 3)), jnp.float32)
    ids = jnp.arange(num_atoms)
    forces = jnp.zeros_like(crd)
    return Snapshot(crd, None, forces, ids, None, None, None)

def build_sponge_helper(dims=3):
    def get_dims():
        return dims
    return HelperMethods(build_data_querier(build_sponge_snapshot_methods(), {"positions", "indices"}), get_dims)

def build(method):
    pysages_extra = namedtuple('PysagesExtra', ['snap', 'state', 'update_func', 'bias_force', 'bias_potential'])
    num_atoms = Sponge.md_info.frc.shape[0]
    snap = build_sponge_snapshot(num_atoms)
    pysages_extra.snap = snap
    helper = build_sponge_helper()
    res = method.build(snap, helper)
    pysages_extra.state = res[1]()
    num_cvs = pysages_extra.state.xi.shape[-1]
    for i in range(num_cvs):
        Sponge.controller.Step_Print_Initial("CV_{}".format(i), "%2f")
    pysages_extra.update_func = res[2]
    pysages_extra.bias_potential = None
    return pysages_extra

def bias_force(pysages_extra):
    pysages_extra.snap = pysages_extra.snap._replace(positions=from_dlpack(Sponge.md_info.crd.toDlpack()))
    pysages_extra.state = pysages_extra.update_func(pysages_extra.snap, pysages_extra.state)
    pysages_extra.bias_force = cufd(to_dlpack(pysages_extra.state.bias))
    return pysages_extra

def force_wrapper(pysages_extra):
    def Calculate_Force(pysages_extra=pysages_extra):
        pysages_extra = bias_force(pysages_extra)
        Sponge.md_info.frc += pysages_extra.bias_force

    def Mdout_Print(pysages_extra=pysages_extra):
        state = pysages_extra.state
        num_cvs = state.xi.shape[-1]
        for i in range(num_cvs):
            Sponge.controller.Step_Print("CV_{}".format(i), state.xi[0][i])

    return Calculate_Force, Mdout_Print

def enhanced_sponge(method):
    pysages_extra = build(method)
    return force_wrapper(pysages_extra)
