# SPDX-FileCopyrightText: Copyright (c) 2025 The Newton Developers
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import enum
from collections.abc import Sequence

import numpy as np
import warp as wp

from ..core.types import Devicelike, Vec2, Vec3, nparray, override


class GeoType(enum.IntEnum):
    PLANE = 0
    HFIELD = 1
    SPHERE = 2
    CAPSULE = 3
    ELLIPSOID = 4
    CYLINDER = 5
    BOX = 6
    MESH = 7
    SDF = 8
    CONE = 9
    NONE = 10


# Default maximum vertices for convex hull approximation
MESH_MAXHULLVERT = 64


class SDF:
    """Describes a signed distance field for simulation

    Attributes:

        volume (Volume): The volume defining the SDF
        I (Mat33): 3x3 inertia matrix of the SDF
        mass (float): The total mass of the SDF
        com (Vec3): The center of mass of the SDF
    """

    def __init__(self, volume: wp.Volume | None = None, I=None, mass=1.0, com=None):
        self.volume = volume
        self.I = I if I is not None else wp.mat33(np.eye(3))
        self.mass = mass
        self.com = com if com is not None else wp.vec3()

        # Need to specify these for now
        self.has_inertia = True
        self.is_solid = True

    def finalize(self) -> wp.uint64:
        """Returns the volume pointer of the SDF volume"""
        return self.volume.id

    @override
    def __hash__(self) -> int:
        return hash(self.volume.id)


class Mesh:
    """Describes a triangle collision mesh for simulation

    Example mesh creation from a triangle OBJ mesh file:
    ====================================================

    See :func:`load_mesh` which is provided as a utility function.

    .. code-block:: python

        import numpy as np
        import warp as wp
        import newton
        import openmesh

        m = openmesh.read_trimesh("mesh.obj")
        mesh_points = np.array(m.points())
        mesh_indices = np.array(m.face_vertex_indices(), dtype=np.int32).flatten()
        mesh = newton.Mesh(mesh_points, mesh_indices)

    Attributes:

        vertices (List[Vec3]): Mesh 3D vertices points
        indices (List[int]): Mesh indices as a flattened list of vertex indices describing triangles
        I (Mat33): 3x3 inertia matrix of the mesh assuming density of 1.0 (around the center of mass)
        mass (float): The total mass of the body assuming density of 1.0
        com (Vec3): The center of mass of the body
        maxhullvert (int): Maximum number of vertices for convex hull approximation (used by MuJoCo solver)
        convex_hull (Mesh): Pre-computed convex hull of the mesh (optional)
    """

    def __init__(
        self,
        vertices: Sequence[Vec3] | nparray,
        indices: Sequence[int] | nparray,
        normals: Sequence[Vec3] | nparray | None = None,
        uvs: Sequence[Vec2] | nparray | None = None,
        compute_inertia: bool = True,
        is_solid: bool = True,
        maxhullvert: int = MESH_MAXHULLVERT,
        color: Vec3 | None = None,
    ):
        """Construct a Mesh object from a triangle mesh

        The mesh center of mass and inertia tensor will automatically be
        calculated using a density of 1.0. This computation is only valid
        if the mesh is closed (two-manifold).

        Args:
            vertices: List of vertices in the mesh
            indices: List of triangle indices, 3 per-element
            normals: Optional per-vertex normals (len == len(vertices)), shape (N, 3)
            uvs: Optional per-vertex texture coordinates (len == len(vertices)), shape (N, 2)
            compute_inertia: If True, the mass, inertia tensor and center of mass will be computed assuming density of 1.0
            is_solid: If True, the mesh is assumed to be a solid during inertia computation, otherwise it is assumed to be a hollow surface
            maxhullvert: Maximum number of vertices for convex hull approximation (default: 64)
            color: Optional per-mesh base color (Vec3 in [0, 1])
        """

        from .inertia import compute_mesh_inertia  # noqa: PLC0415

        self._vertices = np.array(vertices).reshape(-1, 3)
        self._indices = np.array(indices, dtype=np.int32).flatten()
        self._normals = np.array(normals).reshape(-1, 3) if normals is not None else None
        self._uvs = np.array(uvs).reshape(-1, 2) if uvs is not None else None
        self._color = color
        self.is_solid = is_solid
        self.has_inertia = compute_inertia
        self.mesh = None
        self.maxhullvert = maxhullvert
        self._cached_hash = None

        if compute_inertia:
            self.mass, self.com, self.I, _ = compute_mesh_inertia(1.0, vertices, indices, is_solid=is_solid)
        else:
            self.I = wp.mat33(np.eye(3))
            self.mass = 1.0
            self.com = wp.vec3()

    def copy(
        self,
        vertices: Sequence[Vec3] | nparray | None = None,
        indices: Sequence[int] | nparray | None = None,
        recompute_inertia: bool = False,
    ):
        if vertices is None:
            vertices = self.vertices
        if indices is None:
            indices = self.indices
        m = Mesh(
            vertices, indices, compute_inertia=recompute_inertia, is_solid=self.is_solid, maxhullvert=self.maxhullvert
        )
        if not recompute_inertia:
            m.I = self.I
            m.mass = self.mass
            m.com = self.com
            m.has_inertia = self.has_inertia
        return m

    @property
    def vertices(self):
        return self._vertices

    @vertices.setter
    def vertices(self, value):
        self._vertices = np.array(value, dtype=np.float32).reshape(-1, 3)
        self._cached_hash = None

    @property
    def indices(self):
        return self._indices

    @indices.setter
    def indices(self, value):
        self._indices = np.array(value, dtype=np.int32).flatten()
        self._cached_hash = None

    # construct simulation ready buffers from points
    def finalize(self, device: Devicelike = None, requires_grad: bool = False) -> wp.uint64:
        """
        Constructs a simulation-ready :class:`Mesh` object from the mesh data and returns its ID.

        Args:
            device: The device on which to allocate the mesh buffers
            requires_grad: If True, the mesh points and velocity arrays will be allocated with gradient tracking enabled

        Returns:
            The ID of the simulation-ready :class:`Mesh`"""
        with wp.ScopedDevice(device):
            pos = wp.array(self.vertices, requires_grad=requires_grad, dtype=wp.vec3)
            vel = wp.zeros_like(pos)
            indices = wp.array(self.indices, dtype=wp.int32)

            self.mesh = wp.Mesh(points=pos, velocities=vel, indices=indices)
            return self.mesh.id

    def compute_convex_hull(self, replace: bool = False) -> "Mesh":
        """
        Computes and returns the convex hull of this mesh.

        Returns:
            A new Mesh object representing the convex hull
        """
        from .utils import remesh_convex_hull  # noqa: PLC0415

        hull_vertices, hull_faces = remesh_convex_hull(self.vertices, maxhullvert=self.maxhullvert)
        if replace:
            self.vertices = hull_vertices
            self.indices = hull_faces
            return self
        else:
            # create a new mesh for the convex hull
            hull_mesh = Mesh(hull_vertices, hull_faces, compute_inertia=False)
            hull_mesh.maxhullvert = self.maxhullvert  # preserve maxhullvert setting
            hull_mesh.is_solid = self.is_solid
            hull_mesh.has_inertia = self.has_inertia
            hull_mesh.mass = self.mass
            hull_mesh.com = self.com
            hull_mesh.I = self.I
            return hull_mesh

    @override
    def __hash__(self) -> int:
        """
        Computes a hash of the mesh data for use in caching. The hash considers the mesh vertices, indices, and whether the mesh is solid or not.
        Uses cached hash if available, otherwise computes and caches the hash.
        """
        if self._cached_hash is None:
            self._cached_hash = hash(
                (tuple(np.array(self.vertices).flatten()), tuple(np.array(self.indices).flatten()), self.is_solid)
            )
        return self._cached_hash
