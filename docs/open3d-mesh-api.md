Help on class TriangleMesh in module open3d.cuda.pybind.geometry:

class TriangleMesh(MeshBase)
 |  TriangleMesh class. Triangle mesh contains vertices and triangles represented by the indices to the vertices. Optionally, the mesh may also contain triangle normals, vertex normals and vertex colors.
 |
 |  Method resolution order:
 |      TriangleMesh
 |      MeshBase
 |      Geometry3D
 |      Geometry
 |      pybind11_builtins.pybind11_object
 |      builtins.object
 |
 |  Methods defined here:
 |
 |  __add__(...)
 |      __add__(self: open3d.cuda.pybind.geometry.TriangleMesh, arg0: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  __copy__(...)
 |      __copy__(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  __deepcopy__(...)
 |      __deepcopy__(self: open3d.cuda.pybind.geometry.TriangleMesh, arg0: dict) -> open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  __iadd__(...)
 |      __iadd__(self: open3d.cuda.pybind.geometry.TriangleMesh, arg0: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  __init__(...)
 |      __init__(*args, **kwargs)
 |      Overloaded function.
 |
 |      1. __init__(self: open3d.cuda.pybind.geometry.TriangleMesh) -> None
 |
 |      Default constructor
 |
 |      2. __init__(self: open3d.cuda.pybind.geometry.TriangleMesh, arg0: open3d.cuda.pybind.geometry.TriangleMesh) -> None
 |
 |      Copy constructor
 |
 |      3. __init__(self: open3d.cuda.pybind.geometry.TriangleMesh, vertices: open3d.cuda.pybind.utility.Vector3dVector, triangles: open3d.cuda.pybind.utility.Vector3iVector) -> None
 |
 |      Create a triangle mesh from vertices and triangle indices
 |
 |  __repr__(...)
 |      __repr__(self: open3d.cuda.pybind.geometry.TriangleMesh) -> str
 |
 |  cluster_connected_triangles(...)
 |      cluster_connected_triangles(self: open3d.cuda.pybind.geometry.TriangleMesh) -> tuple[open3d.cuda.pybind.utility.IntVector, list[int], open3d.cuda.pybind.utility.DoubleVector]
 |      Function that clusters connected triangles, i.e., triangles that are connected via edges are assigned the same cluster index. This function returns an array that contains the cluster index per triangle, a second array contains the number of triangles per cluster, and a third vector contains the surface area per cluster.
 |
 |      Returns:
 |          tuple[open3d.cuda.pybind.utility.IntVector, list[int], open3d.cuda.pybind.utility.DoubleVector]
 |
 |  compute_adjacency_list(...)
 |      compute_adjacency_list(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to compute adjacency list, call before adjacency list is needed
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  compute_convex_hull(...)
 |      compute_convex_hull(self: open3d.cuda.pybind.geometry.TriangleMesh) -> tuple[open3d.cuda.pybind.geometry.TriangleMesh, list[int]]
 |      Computes the convex hull of the triangle mesh.
 |
 |      Returns:
 |          tuple[open3d.cuda.pybind.geometry.TriangleMesh, list[int]]
 |
 |  compute_triangle_normals(...)
 |      compute_triangle_normals(self: open3d.cuda.pybind.geometry.TriangleMesh, normalized: bool = True) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to compute triangle normals, usually called before rendering
 |
 |      Args:
 |          normalized (bool, optional, default=True)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  compute_vertex_normals(...)
 |      compute_vertex_normals(self: open3d.cuda.pybind.geometry.TriangleMesh, normalized: bool = True) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to compute vertex normals, usually called before rendering
 |
 |      Args:
 |          normalized (bool, optional, default=True)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  crop(...)
 |      crop(*args, **kwargs)
 |      Overloaded function.
 |
 |
 |      1. crop(self: open3d.cuda.pybind.geometry.TriangleMesh, bounding_box: open3d.cuda.pybind.geometry.AxisAlignedBoundingBox) -> open3d.cuda.pybind.geometry.TriangleMesh
 |          Function to crop input TriangleMesh into output TriangleMesh
 |
 |      Args:
 |          bounding_box (open3d.cuda.pybind.geometry.AxisAlignedBoundingBox): AxisAlignedBoundingBox to crop points
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |      2. crop(self: open3d.cuda.pybind.geometry.TriangleMesh, bounding_box: open3d.cuda.pybind.geometry.OrientedBoundingBox) -> open3d.cuda.pybind.geometry.TriangleMesh
 |          Function to crop input TriangleMesh into output TriangleMesh
 |
 |      Args:
 |          bounding_box (open3d.cuda.pybind.geometry.OrientedBoundingBox): AxisAlignedBoundingBox to crop points
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  deform_as_rigid_as_possible(...)
 |      deform_as_rigid_as_possible(self: open3d.cuda.pybind.geometry.TriangleMesh, constraint_vertex_indices: open3d.cuda.pybind.utility.IntVector, constraint_vertex_positions: open3d.cuda.pybind.utility.Vector3dVector, max_iter: int, energy: open3d.cuda.pybind.geometry.DeformAsRigidAsPossibleEnergy = DeformAsRigidAsPossibleEnergy.Spokes, smoothed_alpha: float = 0.01) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      This function deforms the mesh using the method by Sorkine and Alexa, 'As-Rigid-As-Possible Surface Modeling', 2007
 |
 |      Args:
 |          constraint_vertex_indices (open3d.cuda.pybind.utility.IntVector): Indices of the triangle vertices that should be constrained by the vertex positions in constraint_vertex_positions.
 |          constraint_vertex_positions (open3d.cuda.pybind.utility.Vector3dVector): Vertex positions used for the constraints.
 |          max_iter (int): Maximum number of iterations to minimize energy functional.
 |          energy (open3d.cuda.pybind.geometry.DeformAsRigidAsPossibleEnergy, optional, default=DeformAsRigidAsPossibleEnergy.Spokes): Energy model that is minimized in the deformation process
 |          smoothed_alpha (float, optional, default=0.01): trade-off parameter for the smoothed energy functional for the regularization term.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  euler_poincare_characteristic(...)
 |      euler_poincare_characteristic(self: open3d.cuda.pybind.geometry.TriangleMesh) -> int
 |      Function that computes the Euler-Poincaré characteristic, i.e., V + F - E, where V is the number of vertices, F is the number of triangles, and E is the number of edges.
 |
 |      Returns:
 |          int
 |
 |  filter_sharpen(...)
 |      filter_sharpen(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_iterations: int = 1, strength: float = 1, filter_scope: open3d.cuda.pybind.geometry.FilterScope = FilterScope.All) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to sharpen triangle mesh. The output value (:math:`v_o`) is the input value (:math:`v_i`) plus strength times the input value minus he sum of he adjacent values. :math:`v_o = v_i x strength (v_i * |N| - \sum_{n \in N} v_n)`
 |
 |      Args:
 |          number_of_iterations (int, optional, default=1):  Number of repetitions of this operation
 |          strength (float, optional, default=1): Filter parameter.
 |          filter_scope (open3d.cuda.pybind.geometry.FilterScope, optional, default=FilterScope.All)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  filter_smooth_laplacian(...)
 |      filter_smooth_laplacian(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_iterations: int = 1, lambda_filter: float = 0.5, filter_scope: open3d.cuda.pybind.geometry.FilterScope = FilterScope.All) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to smooth triangle mesh using Laplacian. :math:`v_o = v_i \cdot \lambda (sum_{n \in N} w_n v_n - v_i)`, with :math:`v_i` being the input value, :math:`v_o` the output value, :math:`N` is the  set of adjacent neighbours, :math:`w_n` is the weighting of the neighbour based on the inverse distance (closer neighbours have higher weight), and lambda_filter is the smoothing parameter.
 |
 |      Args:
 |          number_of_iterations (int, optional, default=1):  Number of repetitions of this operation
 |          lambda_filter (float, optional, default=0.5): Filter parameter.
 |          filter_scope (open3d.cuda.pybind.geometry.FilterScope, optional, default=FilterScope.All)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  filter_smooth_simple(...)
 |      filter_smooth_simple(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_iterations: int = 1, filter_scope: open3d.cuda.pybind.geometry.FilterScope = FilterScope.All) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to smooth triangle mesh with simple neighbour average. :math:`v_o = \frac{v_i + \sum_{n \in N} v_n)}{|N| + 1}`, with :math:`v_i` being the input value, :math:`v_o` the output value, and :math:`N` is the set of adjacent neighbours.
 |
 |      Args:
 |          number_of_iterations (int, optional, default=1):  Number of repetitions of this operation
 |          filter_scope (open3d.cuda.pybind.geometry.FilterScope, optional, default=FilterScope.All)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  filter_smooth_taubin(...)
 |      filter_smooth_taubin(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_iterations: int = 1, lambda_filter: float = 0.5, mu: float = -0.53, filter_scope: open3d.cuda.pybind.geometry.FilterScope = FilterScope.All) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to smooth triangle mesh using method of Taubin, "Curve and Surface Smoothing Without Shrinkage", 1995. Applies in each iteration two times filter_smooth_laplacian, first with filter parameter lambda_filter and second with filter parameter mu as smoothing parameter. This method avoids shrinkage of the triangle mesh.
 |
 |      Args:
 |          number_of_iterations (int, optional, default=1):  Number of repetitions of this operation
 |          lambda_filter (float, optional, default=0.5): Filter parameter.
 |          mu (float, optional, default=-0.53): Filter parameter.
 |          filter_scope (open3d.cuda.pybind.geometry.FilterScope, optional, default=FilterScope.All)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  get_non_manifold_edges(...)
 |      get_non_manifold_edges(self: open3d.cuda.pybind.geometry.TriangleMesh, allow_boundary_edges: bool = True) -> open3d.cuda.pybind.utility.Vector2iVector
 |      Get list of non-manifold edges.
 |
 |      Args:
 |          allow_boundary_edges (bool, optional, default=True): If true, than non-manifold edges are defined as edges with more than two adjacent triangles, otherwise each edge that is not adjacent to two triangles is defined as non-manifold.
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.Vector2iVector
 |
 |  get_non_manifold_vertices(...)
 |      get_non_manifold_vertices(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.utility.IntVector
 |      Returns a list of indices to non-manifold vertices.
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.IntVector
 |
 |  get_self_intersecting_triangles(...)
 |      get_self_intersecting_triangles(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.utility.Vector2iVector
 |      Returns a list of indices to triangles that intersect the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.Vector2iVector
 |
 |  get_surface_area(...)
 |      get_surface_area(self: open3d.cuda.pybind.geometry.TriangleMesh) -> float
 |
 |      Function that computes the surface area of the mesh, i.e. the sum of the individual triangle surfaces.
 |
 |  get_volume(...)
 |      get_volume(self: open3d.cuda.pybind.geometry.TriangleMesh) -> float
 |
 |      Function that computes the volume of the mesh, under the condition that it is watertight and orientable.
 |
 |  has_adjacency_list(...)
 |      has_adjacency_list(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains adjacency normals.
 |
 |      Returns:
 |          bool
 |
 |  has_textures(...)
 |      has_textures(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains a texture image.
 |
 |      Returns:
 |          bool
 |
 |  has_triangle_material_ids(...)
 |      has_triangle_material_ids(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains material ids.
 |
 |      Returns:
 |          bool
 |
 |  has_triangle_normals(...)
 |      has_triangle_normals(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains triangle normals.
 |
 |      Returns:
 |          bool
 |
 |  has_triangle_uvs(...)
 |      has_triangle_uvs(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains uv coordinates.
 |
 |      Returns:
 |          bool
 |
 |  has_triangles(...)
 |      has_triangles(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains triangles.
 |
 |      Returns:
 |          bool
 |
 |  has_vertex_colors(...)
 |      has_vertex_colors(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains vertex colors.
 |
 |      Returns:
 |          bool
 |
 |  has_vertex_normals(...)
 |      has_vertex_normals(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains vertex normals.
 |
 |      Returns:
 |          bool
 |
 |  has_vertices(...)
 |      has_vertices(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Returns ``True`` if the mesh contains vertices.
 |
 |      Returns:
 |          bool
 |
 |  is_edge_manifold(...)
 |      is_edge_manifold(self: open3d.cuda.pybind.geometry.TriangleMesh, allow_boundary_edges: bool = True) -> bool
 |      Tests if the triangle mesh is edge manifold.
 |
 |      Args:
 |          allow_boundary_edges (bool, optional, default=True): If true, than non-manifold edges are defined as edges with more than two adjacent triangles, otherwise each edge that is not adjacent to two triangles is defined as non-manifold.
 |
 |      Returns:
 |          bool
 |
 |  is_intersecting(...)
 |      is_intersecting(self: open3d.cuda.pybind.geometry.TriangleMesh, arg0: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Tests if the triangle mesh is intersecting the other triangle mesh.
 |
 |      Args:
 |          arg0 (open3d.cuda.pybind.geometry.TriangleMesh)
 |
 |      Returns:
 |          bool
 |
 |  is_orientable(...)
 |      is_orientable(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Tests if the triangle mesh is orientable.
 |
 |      Returns:
 |          bool
 |
 |  is_self_intersecting(...)
 |      is_self_intersecting(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Tests if the triangle mesh is self-intersecting.
 |
 |      Returns:
 |          bool
 |
 |  is_vertex_manifold(...)
 |      is_vertex_manifold(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Tests if all vertices of the triangle mesh are manifold.
 |
 |      Returns:
 |          bool
 |
 |  is_watertight(...)
 |      is_watertight(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      Tests if the triangle mesh is watertight.
 |
 |      Returns:
 |          bool
 |
 |  merge_close_vertices(...)
 |      merge_close_vertices(self: open3d.cuda.pybind.geometry.TriangleMesh, eps: float) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function that will merge close by vertices to a single one. The vertex position, normal and color will be the average of the vertices. The parameter eps defines the maximum distance of close by vertices.  This function might help to close triangle soups.
 |
 |      Args:
 |          eps (float): Parameter that defines the distance between close vertices.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  normalize_normals(...)
 |      normalize_normals(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Normalize both triangle normals and vertex normals to length 1.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  orient_triangles(...)
 |      orient_triangles(self: open3d.cuda.pybind.geometry.TriangleMesh) -> bool
 |      If the mesh is orientable this function orients all triangles such that all normals point towards the same direction.
 |
 |      Returns:
 |          bool
 |
 |  paint_uniform_color(...)
 |      paint_uniform_color(self: open3d.cuda.pybind.geometry.TriangleMesh, arg0: numpy.ndarray[numpy.float64[3, 1]]) -> open3d.cuda.pybind.geometry.MeshBase
 |      Assigns each vertex in the TriangleMesh the same color.
 |
 |      Args:
 |          arg0 (numpy.ndarray[numpy.float64[3, 1]])
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.MeshBase
 |
 |  remove_degenerate_triangles(...)
 |      remove_degenerate_triangles(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function that removes degenerate triangles, i.e., triangles that references a single vertex multiple times in a single triangle. They are usually the product of removing duplicated vertices.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  remove_duplicated_triangles(...)
 |      remove_duplicated_triangles(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function that removes duplicated triangles, i.e., removes triangles that reference the same three vertices and have the same orientation.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  remove_duplicated_vertices(...)
 |      remove_duplicated_vertices(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function that removes duplicated vertices, i.e., vertices that have identical coordinates.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  remove_non_manifold_edges(...)
 |      remove_non_manifold_edges(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function that removes all non-manifold edges, by successively deleting  triangles with the smallest surface area adjacent to the non-manifold edge until the number of adjacent triangles to the edge is `<= 2`.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  remove_triangles_by_index(...)
 |      remove_triangles_by_index(self: open3d.cuda.pybind.geometry.TriangleMesh, triangle_indices: list[int]) -> None
 |      This function removes the triangles with index in triangle_indices.  Call remove_unreferenced_vertices to clean up vertices afterwards.
 |
 |      Args:
 |          triangle_indices (list[int]): 1D array of triangle indices that should be removed from the TriangleMesh.
 |
 |      Returns:
 |          None
 |
 |  remove_triangles_by_mask(...)
 |      remove_triangles_by_mask(self: open3d.cuda.pybind.geometry.TriangleMesh, triangle_mask: list[bool]) -> None
 |      This function removes the triangles where triangle_mask is set to true.  Call remove_unreferenced_vertices to clean up vertices afterwards.
 |
 |      Args:
 |          triangle_mask (list[bool]): 1D bool array, True values indicate triangles that should be removed.
 |
 |      Returns:
 |          None
 |
 |  remove_unreferenced_vertices(...)
 |      remove_unreferenced_vertices(self: open3d.cuda.pybind.geometry.TriangleMesh) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      This function removes vertices from the triangle mesh that are not referenced in any triangle of the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  remove_vertices_by_index(...)
 |      remove_vertices_by_index(self: open3d.cuda.pybind.geometry.TriangleMesh, vertex_indices: list[int]) -> None
 |      This function removes the vertices with index in vertex_indices. Note that also all triangles associated with the vertices are removed.
 |
 |      Args:
 |          vertex_indices (list[int]): 1D array of vertex indices that should be removed from the TriangleMesh.
 |
 |      Returns:
 |          None
 |
 |  remove_vertices_by_mask(...)
 |      remove_vertices_by_mask(self: open3d.cuda.pybind.geometry.TriangleMesh, vertex_mask: list[bool]) -> None
 |      This function removes the vertices that are masked in vertex_mask. Note that also all triangles associated with the vertices are removed.
 |
 |      Args:
 |          vertex_mask (list[bool]): 1D bool array, True values indicate vertices that should be removed.
 |
 |      Returns:
 |          None
 |
 |  sample_points_poisson_disk(...)
 |      sample_points_poisson_disk(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_points: int, init_factor: float = 5, pcl: open3d.cuda.pybind.geometry.PointCloud = None, use_triangle_normal: bool = False) -> open3d.cuda.pybind.geometry.PointCloud
 |      Function to sample points from the mesh, where each point has approximately the same distance to the neighbouring points (blue noise). Method is based on Yuksel, "Sample Elimination for Generating Poisson Disk Sample Sets", EUROGRAPHICS, 2015.
 |
 |      Args:
 |          number_of_points (int): Number of points that should be sampled.
 |          init_factor (float, optional, default=5): Factor for the initial uniformly sampled PointCloud. This init PointCloud is used for sample elimination.
 |          pcl (open3d.cuda.pybind.geometry.PointCloud, optional, default=None): Initial PointCloud that is used for sample elimination. If this parameter is provided the init_factor is ignored.
 |          use_triangle_normal (bool, optional, default=False): If True assigns the triangle normals instead of the interpolated vertex normals to the returned points. The triangle normals will be computed and added to the mesh if necessary.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  sample_points_uniformly(...)
 |      sample_points_uniformly(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_points: int = 100, use_triangle_normal: bool = False) -> open3d.cuda.pybind.geometry.PointCloud
 |      Function to uniformly sample points from the mesh.
 |
 |      Args:
 |          number_of_points (int, optional, default=100): Number of points that should be uniformly sampled.
 |          use_triangle_normal (bool, optional, default=False): If True assigns the triangle normals instead of the interpolated vertex normals to the returned points. The triangle normals will be computed and added to the mesh if necessary.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  select_by_index(...)
 |      select_by_index(self: open3d.cuda.pybind.geometry.TriangleMesh, indices: list[int], cleanup: bool = True) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to select mesh from input triangle mesh into output triangle mesh. ``input``: The input triangle mesh. ``indices``: Indices of vertices to be selected.
 |
 |      Args:
 |          indices (list[int]): Indices of vertices to be selected.
 |          cleanup (bool, optional, default=True): If true calls number of mesh cleanup functions to remove unreferenced vertices and degenerate triangles
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  simplify_quadric_decimation(...)
 |      simplify_quadric_decimation(self: open3d.cuda.pybind.geometry.TriangleMesh, target_number_of_triangles: int, maximum_error: float = inf, boundary_weight: float = 1.0) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to simplify mesh using Quadric Error Metric Decimation by Garland and Heckbert
 |
 |      Args:
 |          target_number_of_triangles (int): The number of triangles that the simplified mesh should have. It is not guaranteed that this number will be reached.
 |          maximum_error (float, optional, default=inf): The maximum error where a vertex is allowed to be merged
 |          boundary_weight (float, optional, default=1.0): A weight applied to edge vertices used to preserve boundaries
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  simplify_vertex_clustering(...)
 |      simplify_vertex_clustering(self: open3d.cuda.pybind.geometry.TriangleMesh, voxel_size: float, contraction: open3d.cuda.pybind.geometry.SimplificationContraction = SimplificationContraction.Average) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function to simplify mesh using vertex clustering.
 |
 |      Args:
 |          voxel_size (float): The size of the voxel within vertices are pooled.
 |          contraction (open3d.cuda.pybind.geometry.SimplificationContraction, optional, default=SimplificationContraction.Average): Method to aggregate vertex information. Average computes a simple average, Quadric minimizes the distance to the adjacent planes.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  subdivide_loop(...)
 |      subdivide_loop(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_iterations: int = 1) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function subdivide mesh using Loop's algorithm. Loop, "Smooth subdivision surfaces based on triangles", 1987.
 |
 |      Args:
 |          number_of_iterations (int, optional, default=1): Number of iterations. A single iteration splits each triangle into four triangles.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  subdivide_midpoint(...)
 |      subdivide_midpoint(self: open3d.cuda.pybind.geometry.TriangleMesh, number_of_iterations: int = 1) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function subdivide mesh using midpoint algorithm.
 |
 |      Args:
 |          number_of_iterations (int, optional, default=1): Number of iterations. A single iteration splits each triangle into four triangles that cover the same surface.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  ----------------------------------------------------------------------
 |  Static methods defined here:
 |
 |  create_arrow(...) method of builtins.PyCapsule instance
 |      create_arrow(cylinder_radius: float = 1.0, cone_radius: float = 1.5, cylinder_height: float = 5.0, cone_height: float = 4.0, resolution: int = 20, cylinder_split: int = 4, cone_split: int = 1) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create an arrow mesh
 |
 |      Args:
 |          cylinder_radius (float, optional, default=1.0): The radius of the cylinder.
 |          cone_radius (float, optional, default=1.5): The radius of the cone.
 |          cylinder_height (float, optional, default=5.0): The height of the cylinder. The cylinder is from (0, 0, 0) to (0, 0, cylinder_height)
 |          cone_height (float, optional, default=4.0): The height of the cone. The axis of the cone will be from (0, 0, cylinder_height) to (0, 0, cylinder_height + cone_height)
 |          resolution (int, optional, default=20): The cone will be split into ``resolution`` segments.
 |          cylinder_split (int, optional, default=4): The ``cylinder_height`` will be split into ``cylinder_split`` segments.
 |          cone_split (int, optional, default=1): The ``cone_height`` will be split into ``cone_split`` segments.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_box(...) method of builtins.PyCapsule instance
 |      create_box(width: float = 1.0, height: float = 1.0, depth: float = 1.0, create_uv_map: bool = False, map_texture_to_each_face: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a box. The left bottom corner on the front will be placed at (0, 0, 0), and default UV map, maps the entire texture to each face.
 |
 |      Args:
 |          width (float, optional, default=1.0): x-directional length.
 |          height (float, optional, default=1.0): y-directional length.
 |          depth (float, optional, default=1.0): z-directional length.
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |          map_texture_to_each_face (bool, optional, default=False): Map entire texture to each face.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_cone(...) method of builtins.PyCapsule instance
 |      create_cone(radius: float = 1.0, height: float = 2.0, resolution: int = 20, split: int = 1, create_uv_map: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a cone mesh.
 |
 |      Args:
 |          radius (float, optional, default=1.0): The radius of the cone.
 |          height (float, optional, default=2.0): The height of the cone. The axis of the cone will be from (0, 0, 0) to (0, 0, height).
 |          resolution (int, optional, default=20): The circle will be split into ``resolution`` segments
 |          split (int, optional, default=1): The ``height`` will be split into ``split`` segments.
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_coordinate_frame(...) method of builtins.PyCapsule instance
 |      create_coordinate_frame(size: float = 1.0, origin: numpy.ndarray[numpy.float64[3, 1]] = array([0., 0., 0.])) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a coordinate frame mesh. The coordinate frame will be centered at ``origin``. The x, y, z axis will be rendered as red, green, and blue arrows respectively.
 |
 |      Args:
 |          size (float, optional, default=1.0): The size of the coordinate frame.
 |          origin (numpy.ndarray[numpy.float64[3, 1]], optional, default=array([0., 0., 0.])): The origin of the coordinate frame.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_cylinder(...) method of builtins.PyCapsule instance
 |      create_cylinder(radius: float = 1.0, height: float = 2.0, resolution: int = 20, split: int = 4, create_uv_map: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a cylinder mesh.
 |
 |      Args:
 |          radius (float, optional, default=1.0): The radius of the cylinder.
 |          height (float, optional, default=2.0): The height of the cylinder. The axis of the cylinder will be from (0, 0, -height/2) to (0, 0, height/2).
 |          resolution (int, optional, default=20):  The circle will be split into ``resolution`` segments
 |          split (int, optional, default=4): The ``height`` will be split into ``split`` segments.
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_from_oriented_bounding_box(...) method of builtins.PyCapsule instance
 |      create_from_oriented_bounding_box(obox: open3d.cuda.pybind.geometry.OrientedBoundingBox, scale: numpy.ndarray[numpy.float64[3, 1]] = array([1., 1., 1.]), create_uv_map: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a solid oriented bounding box.
 |
 |      Args:
 |          obox (open3d.cuda.pybind.geometry.OrientedBoundingBox): OrientedBoundingBox object to create mesh of.
 |          scale (numpy.ndarray[numpy.float64[3, 1]], optional, default=array([1., 1., 1.])): scale factor along each direction of OrientedBoundingBox
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_from_point_cloud_alpha_shape(...) method of builtins.PyCapsule instance
 |      create_from_point_cloud_alpha_shape(*args, **kwargs)
 |      Overloaded function.
 |
 |
 |      1. create_from_point_cloud_alpha_shape(pcd: open3d.cuda.pybind.geometry.PointCloud, alpha: float) -> open3d.cuda.pybind.geometry.TriangleMesh
 |          Alpha shapes are a generalization of the convex hull. With decreasing alpha value the shape schrinks and creates cavities. See Edelsbrunner and Muecke, "Three-Dimensional Alpha Shapes", 1994.
 |
 |      Args:
 |          pcd (open3d.cuda.pybind.geometry.PointCloud): PointCloud from which the TriangleMesh surface is reconstructed.
 |          alpha (float): Parameter to control the shape. A very big value will give a shape close to the convex hull.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |      2. create_from_point_cloud_alpha_shape(pcd: open3d.cuda.pybind.geometry.PointCloud, alpha: float, tetra_mesh: open3d.cuda.pybind.geometry.TetraMesh, pt_map: list[int]) -> open3d.cuda.pybind.geometry.TriangleMesh
 |          Alpha shapes are a generalization of the convex hull. With decreasing alpha value the shape shrinks and creates cavities. See Edelsbrunner and Muecke, "Three-Dimensional Alpha Shapes", 1994.
 |
 |      Args:
 |          pcd (open3d.cuda.pybind.geometry.PointCloud): PointCloud from which the TriangleMesh surface is reconstructed.
 |          alpha (float): Parameter to control the shape. A very big value will give a shape close to the convex hull.
 |          tetra_mesh (open3d.cuda.pybind.geometry.TetraMesh): If not None, than uses this to construct the alpha shape. Otherwise, TetraMesh is computed from pcd.
 |          pt_map (list[int]): Optional map from tetra_mesh vertex indices to pcd points.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_from_point_cloud_ball_pivoting(...) method of builtins.PyCapsule instance
 |      create_from_point_cloud_ball_pivoting(pcd: open3d.cuda.pybind.geometry.PointCloud, radii: open3d.cuda.pybind.utility.DoubleVector) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Function that computes a triangle mesh from a oriented PointCloud. This implements the Ball Pivoting algorithm proposed in F. Bernardini et al., "The ball-pivoting algorithm for surface reconstruction", 1999. The implementation is also based on the algorithms outlined in Digne, "An Analysis and Implementation of a Parallel Ball Pivoting Algorithm", 2014. The surface reconstruction is done by rolling a ball with a given radius over the point cloud, whenever the ball touches three points a triangle is created.
 |
 |      Args:
 |          pcd (open3d.cuda.pybind.geometry.PointCloud): PointCloud from which the TriangleMesh surface is reconstructed. Has to contain normals.
 |          radii (open3d.cuda.pybind.utility.DoubleVector): The radii of the ball that are used for the surface reconstruction.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_from_point_cloud_poisson(...) method of builtins.PyCapsule instance
 |      create_from_point_cloud_poisson(pcd: open3d.cuda.pybind.geometry.PointCloud, depth: int = 8, width: float = 0, scale: float = 1.1, linear_fit: bool = False, n_threads: int = -1) -> tuple[open3d.cuda.pybind.geometry.TriangleMesh, open3d.cuda.pybind.utility.DoubleVector]
 |      Function that computes a triangle mesh from a oriented PointCloud pcd. This implements the Screened Poisson Reconstruction proposed in Kazhdan and Hoppe, "Screened Poisson Surface Reconstruction", 2013. This function uses the original implementation by Kazhdan. See https://github.com/mkazhdan/PoissonRecon
 |
 |      Args:
 |          pcd (open3d.cuda.pybind.geometry.PointCloud): PointCloud from which the TriangleMesh surface is reconstructed. Has to contain normals.
 |          depth (int, optional, default=8): Maximum depth of the tree that will be used for surface reconstruction. Running at depth d corresponds to solving on a grid whose resolution is no larger than 2^d x 2^d x 2^d. Note that since the reconstructor adapts the octree to the sampling density, the specified reconstruction depth is only an upper bound.
 |          width (float, optional, default=0): Specifies the target width of the finest level octree cells. This parameter is ignored if depth is specified
 |          scale (float, optional, default=1.1): Specifies the ratio between the diameter of the cube used for reconstruction and the diameter of the samples' bounding cube.
 |          linear_fit (bool, optional, default=False): If true, the reconstructor will use linear interpolation to estimate the positions of iso-vertices.
 |          n_threads (int, optional, default=-1): Number of threads used for reconstruction. Set to -1 to automatically determine it.
 |
 |      Returns:
 |          tuple[open3d.cuda.pybind.geometry.TriangleMesh, open3d.cuda.pybind.utility.DoubleVector]
 |
 |  create_icosahedron(...) method of builtins.PyCapsule instance
 |      create_icosahedron(radius: float = 1.0, create_uv_map: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a icosahedron. The centroid of the mesh will be placed at (0, 0, 0) and the vertices have a distance of radius to the center.
 |
 |      Args:
 |          radius (float, optional, default=1.0): Distance from centroid to mesh vetices.
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_mobius(...) method of builtins.PyCapsule instance
 |      create_mobius(length_split: int = 70, width_split: int = 15, twists: int = 1, raidus: float = 1, flatness: float = 1, width: float = 1, scale: float = 1) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a Mobius strip.
 |
 |      Args:
 |          length_split (int, optional, default=70): The number of segments along the Mobius strip.
 |          width_split (int, optional, default=15): The number of segments along the width of the Mobius strip.
 |          twists (int, optional, default=1): Number of twists of the Mobius strip.
 |          raidus (float, optional, default=1)
 |          flatness (float, optional, default=1): Controls the flatness/height of the Mobius strip.
 |          width (float, optional, default=1): Width of the Mobius strip.
 |          scale (float, optional, default=1): Scale the complete Mobius strip.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_octahedron(...) method of builtins.PyCapsule instance
 |      create_octahedron(radius: float = 1.0, create_uv_map: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a octahedron. The centroid of the mesh will be placed at (0, 0, 0) and the vertices have a distance of radius to the center.
 |
 |      Args:
 |          radius (float, optional, default=1.0): Distance from centroid to mesh vetices.
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_sphere(...) method of builtins.PyCapsule instance
 |      create_sphere(radius: float = 1.0, resolution: int = 20, create_uv_map: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a sphere mesh centered at (0, 0, 0).
 |
 |      Args:
 |          radius (float, optional, default=1.0): The radius of the sphere.
 |          resolution (int, optional, default=20): The resolution of the sphere. The longitues will be split into ``resolution`` segments (i.e. there are ``resolution + 1`` latitude lines including the north and south pole). The latitudes will be split into ```2 * resolution`` segments (i.e. there are ``2 * resolution`` longitude lines.)
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_tetrahedron(...) method of builtins.PyCapsule instance
 |      create_tetrahedron(radius: float = 1.0, create_uv_map: bool = False) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a tetrahedron. The centroid of the mesh will be placed at (0, 0, 0) and the vertices have a distance of radius to the center.
 |
 |      Args:
 |          radius (float, optional, default=1.0): Distance from centroid to mesh vetices.
 |          create_uv_map (bool, optional, default=False): Add default uv map to the mesh.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  create_torus(...) method of builtins.PyCapsule instance
 |      create_torus(torus_radius: float = 1.0, tube_radius: float = 0.5, radial_resolution: int = 30, tubular_resolution: int = 20) -> open3d.cuda.pybind.geometry.TriangleMesh
 |      Factory function to create a torus mesh.
 |
 |      Args:
 |          torus_radius (float, optional, default=1.0): The radius from the center of the torus to the center of the tube.
 |          tube_radius (float, optional, default=0.5): The radius of the torus tube.
 |          radial_resolution (int, optional, default=30): The number of segments along the radial direction.
 |          tubular_resolution (int, optional, default=20): The number of segments along the tubular direction.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.TriangleMesh
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  adjacency_list
 |      List of Sets: The set ``adjacency_list[i]`` contains the indices of adjacent vertices of vertex i.
 |
 |  textures
 |      open3d.geometry.Image: The texture images.
 |
 |  triangle_material_ids
 |      `int` array of shape ``(num_trianges, 1)``, use ``numpy.asarray()`` to access data: material index associated with each triangle
 |
 |  triangle_normals
 |      ``float64`` array of shape ``(num_triangles, 3)``, use ``numpy.asarray()`` to access data: Triangle normals.
 |
 |  triangle_uvs
 |      ``float64`` array of shape ``(3 * num_triangles, 2)``, use ``numpy.asarray()`` to access data: List of uvs denoted by the index of points forming the triangle.
 |
 |  triangles
 |      ``int`` array of shape ``(num_triangles, 3)``, use ``numpy.asarray()`` to access data: List of triangles denoted by the index of points forming the triangle.
 |
 |  vertex_colors
 |      ``float64`` array of shape ``(num_vertices, 3)``, range ``[0, 1]`` , use ``numpy.asarray()`` to access data: RGB colors of vertices.
 |
 |  vertex_normals
 |      ``float64`` array of shape ``(num_vertices, 3)``, use ``numpy.asarray()`` to access data: Vertex normals.
 |
 |  vertices
 |      ``float64`` array of shape ``(num_vertices, 3)``, use ``numpy.asarray()`` to access data: Vertex coordinates.
 |
 |  ----------------------------------------------------------------------
 |  Methods inherited from Geometry3D:
 |
 |  get_axis_aligned_bounding_box(...)
 |      get_axis_aligned_bounding_box(self: open3d.cuda.pybind.geometry.Geometry3D) -> open3d.cuda.pybind.geometry.AxisAlignedBoundingBox
 |      Returns an axis-aligned bounding box of the geometry.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.AxisAlignedBoundingBox
 |
 |  get_center(...)
 |      get_center(self: open3d.cuda.pybind.geometry.Geometry3D) -> numpy.ndarray[numpy.float64[3, 1]]
 |      Returns the center of the geometry coordinates.
 |
 |      Returns:
 |          numpy.ndarray[numpy.float64[3, 1]]
 |
 |  get_max_bound(...)
 |      get_max_bound(self: open3d.cuda.pybind.geometry.Geometry3D) -> numpy.ndarray[numpy.float64[3, 1]]
 |      Returns max bounds for geometry coordinates.
 |
 |      Returns:
 |          numpy.ndarray[numpy.float64[3, 1]]
 |
 |  get_min_bound(...)
 |      get_min_bound(self: open3d.cuda.pybind.geometry.Geometry3D) -> numpy.ndarray[numpy.float64[3, 1]]
 |      Returns min bounds for geometry coordinates.
 |
 |      Returns:
 |          numpy.ndarray[numpy.float64[3, 1]]
 |
 |  get_minimal_oriented_bounding_box(...)
 |      get_minimal_oriented_bounding_box(self: open3d.cuda.pybind.geometry.Geometry3D, robust: bool = False) -> open3d.cuda.pybind.geometry.OrientedBoundingBox
 |
 |
 |      Returns the minimal oriented bounding box for the geometry.
 |
 |      Creates the oriented bounding box with the smallest volume.
 |      The algorithm makes use of the fact that at least one edge of
 |      the convex hull must be collinear with an edge of the minimum
 |      bounding box: for each triangle in the convex hull, calculate
 |      the minimal axis aligned box in the frame of that triangle.
 |      at the end, return the box with the smallest volume
 |
 |      Args:
 |           robust (bool): If set to true uses a more robust method which works in
 |                degenerate cases but introduces noise to the points coordinates.
 |
 |      Returns:
 |           open3d.geometry.OrientedBoundingBox: The oriented bounding box. The
 |           bounding box is oriented such that its volume is minimized.
 |
 |  get_oriented_bounding_box(...)
 |      get_oriented_bounding_box(self: open3d.cuda.pybind.geometry.Geometry3D, robust: bool = False) -> open3d.cuda.pybind.geometry.OrientedBoundingBox
 |
 |
 |      Returns the oriented bounding box for the geometry.
 |
 |      Computes the oriented bounding box based on the PCA of the convex hull.
 |      The returned bounding box is an approximation to the minimal bounding box.
 |
 |      Args:
 |           robust (bool): If set to true uses a more robust method which works in
 |                degenerate cases but introduces noise to the points coordinates.
 |
 |      Returns:
 |           open3d.geometry.OrientedBoundingBox: The oriented bounding box. The
 |           bounding box is oriented such that the axes are ordered with respect to
 |           the principal components.
 |
 |  rotate(...)
 |      rotate(*args, **kwargs)
 |      Overloaded function.
 |
 |
 |      1. rotate(self: open3d.cuda.pybind.geometry.Geometry3D, R: numpy.ndarray[numpy.float64[3, 3]]) -> open3d.cuda.pybind.geometry.Geometry3D
 |          Apply rotation to the geometry coordinates and normals.
 |
 |      Args:
 |          R (numpy.ndarray[numpy.float64[3, 3]]): The rotation matrix
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry3D
 |
 |      2. rotate(self: open3d.cuda.pybind.geometry.Geometry3D, R: numpy.ndarray[numpy.float64[3, 3]], center: numpy.ndarray[numpy.float64[3, 1]]) -> open3d.cuda.pybind.geometry.Geometry3D
 |          Apply rotation to the geometry coordinates and normals.
 |
 |      Args:
 |          R (numpy.ndarray[numpy.float64[3, 3]]): The rotation matrix
 |          center (numpy.ndarray[numpy.float64[3, 1]]): Rotation center used for transformation.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry3D
 |
 |  scale(...)
 |      scale(*args, **kwargs)
 |      Overloaded function.
 |
 |
 |      1. scale(self: open3d.cuda.pybind.geometry.Geometry3D, scale: float, center: numpy.ndarray[numpy.float64[3, 1]]) -> open3d.cuda.pybind.geometry.Geometry3D
 |          Apply scaling to the geometry coordinates.
 |
 |      Args:
 |          scale (float): The scale parameter that is multiplied to the points/vertices of the geometry.
 |          center (numpy.ndarray[numpy.float64[3, 1]]): Scale center used for transformation.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry3D
 |
 |      2. scale(self: open3d.cuda.pybind.geometry.Geometry3D, scale: float, center: numpy.ndarray[numpy.float64[3, 1]]) -> open3d.cuda.pybind.geometry.Geometry3D
 |          Apply scaling to the geometry coordinates.
 |
 |      Args:
 |          scale (float): The scale parameter that is multiplied to the points/vertices of the geometry.
 |          center (numpy.ndarray[numpy.float64[3, 1]]): Scale center used for transformation.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry3D
 |
 |  transform(...)
 |      transform(self: open3d.cuda.pybind.geometry.Geometry3D, arg0: numpy.ndarray[numpy.float64[4, 4]]) -> open3d.cuda.pybind.geometry.Geometry3D
 |      Apply transformation (4x4 matrix) to the geometry coordinates.
 |
 |      Args:
 |          arg0 (numpy.ndarray[numpy.float64[4, 4]])
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry3D
 |
 |  translate(...)
 |      translate(self: open3d.cuda.pybind.geometry.Geometry3D, translation: numpy.ndarray[numpy.float64[3, 1]], relative: bool = True) -> open3d.cuda.pybind.geometry.Geometry3D
 |      Apply translation to the geometry coordinates.
 |
 |      Args:
 |          translation (numpy.ndarray[numpy.float64[3, 1]]): A 3D vector to transform the geometry
 |          relative (bool, optional, default=True): If true, the translation vector is directly added to the geometry coordinates. Otherwise, the center is moved to the translation vector.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry3D
 |
 |  ----------------------------------------------------------------------
 |  Static methods inherited from Geometry3D:
 |
 |  get_rotation_matrix_from_axis_angle(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_axis_angle(rotation: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  get_rotation_matrix_from_quaternion(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_quaternion(rotation: numpy.ndarray[numpy.float64[4, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  get_rotation_matrix_from_xyz(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_xyz(rotation: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  get_rotation_matrix_from_xzy(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_xzy(rotation: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  get_rotation_matrix_from_yxz(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_yxz(rotation: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  get_rotation_matrix_from_yzx(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_yzx(rotation: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  get_rotation_matrix_from_zxy(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_zxy(rotation: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  get_rotation_matrix_from_zyx(...) method of builtins.PyCapsule instance
 |      get_rotation_matrix_from_zyx(rotation: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 3]]
 |
 |  ----------------------------------------------------------------------
 |  Methods inherited from Geometry:
 |
 |  clear(...)
 |      clear(self: open3d.cuda.pybind.geometry.Geometry) -> open3d.cuda.pybind.geometry.Geometry
 |      Clear all elements in the geometry.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry
 |
 |  dimension(...)
 |      dimension(self: open3d.cuda.pybind.geometry.Geometry) -> int
 |      Returns whether the geometry is 2D or 3D.
 |
 |      Returns:
 |          int
 |
 |  get_geometry_type(...)
 |      get_geometry_type(self: open3d.cuda.pybind.geometry.Geometry) -> open3d.cuda.pybind.geometry.Geometry.Type
 |      Returns one of registered geometry types.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.Geometry.Type
 |
 |  is_empty(...)
 |      is_empty(self: open3d.cuda.pybind.geometry.Geometry) -> bool
 |      Returns ``True`` iff the geometry is empty.
 |
 |      Returns:
 |          bool
 |
 |  ----------------------------------------------------------------------
 |  Data and other attributes inherited from Geometry:
 |
 |  HalfEdgeTriangleMesh = <Type.HalfEdgeTriangleMesh: 7>
 |
 |  Image = <Type.Image: 8>
 |
 |  LineSet = <Type.LineSet: 4>
 |
 |  PointCloud = <Type.PointCloud: 1>
 |
 |  RGBDImage = <Type.RGBDImage: 9>
 |
 |  TetraMesh = <Type.TetraMesh: 10>
 |
 |  TriangleMesh = <Type.TriangleMesh: 6>
 |
 |  Type = <class 'open3d.cuda.pybind.geometry.Geometry.Type'>
 |
 |  Unspecified = <Type.Unspecified: 0>
 |
 |  VoxelGrid = <Type.VoxelGrid: 2>
 |
 |  ----------------------------------------------------------------------
 |  Static methods inherited from pybind11_builtins.pybind11_object:
 |
 |  __new__(*args, **kwargs) class method of pybind11_builtins.pybind11_object
 |      Create and return a new object.  See help(type) for accurate signature.

