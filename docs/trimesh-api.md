Help on class Trimesh in module trimesh.base:

class Trimesh(trimesh.parent.Geometry3D)
 |  Trimesh(vertices: Optional[ArrayLike] = None, faces: Optional[ArrayLike] = None, face_normals: Optional[ArrayLike] = None, vertex_normals: Optional[ArrayLike] = None, face_colors: Optional[ArrayLike] = None, vertex_colors: Optional[ArrayLike] = None, face_attributes: Optional[dict[str, ArrayLike]] = None, vertex_attributes: Optional[dict[str, ArrayLike]] = None, metadata: Optional[dict[str, Any]] = None, process: bool = True, validate: bool = False, merge_tex: Optional[bool] = None, merge_norm: Optional[bool] = None, use_embree: bool = True, initial_cache: Optional[dict[str, numpy.ndarray]] = None, visual: Union[trimesh.visual.color.ColorVisuals, trimesh.visual.texture.TextureVisuals, NoneType] = None, **kwargs) -> None
 |
 |  Method resolution order:
 |      Trimesh
 |      trimesh.parent.Geometry3D
 |      trimesh.parent.Geometry
 |      abc.ABC
 |      builtins.object
 |
 |  Methods defined here:
 |
 |  __add__(self, other: 'Trimesh') -> 'Trimesh'
 |      Concatenate the mesh with another mesh.
 |
 |      Parameters
 |      ------------
 |      other : trimesh.Trimesh object
 |        Mesh to be concatenated with self
 |
 |      Returns
 |      ----------
 |      concat : trimesh.Trimesh
 |        Mesh object of combined result
 |
 |  __copy__(self, *args) -> 'Trimesh'
 |
 |  __deepcopy__(self, *args) -> 'Trimesh'
 |
 |  __init__(self, vertices: Optional[ArrayLike] = None, faces: Optional[ArrayLike] = None, face_normals: Optional[ArrayLike] = None, vertex_normals: Optional[ArrayLike] = None, face_colors: Optional[ArrayLike] = None, vertex_colors: Optional[ArrayLike] = None, face_attributes: Optional[dict[str, ArrayLike]] = None, vertex_attributes: Optional[dict[str, ArrayLike]] = None, metadata: Optional[dict[str, Any]] = None, process: bool = True, validate: bool = False, merge_tex: Optional[bool] = None, merge_norm: Optional[bool] = None, use_embree: bool = True, initial_cache: Optional[dict[str, numpy.ndarray]] = None, visual: Union[trimesh.visual.color.ColorVisuals, trimesh.visual.texture.TextureVisuals, NoneType] = None, **kwargs) -> None
 |      A Trimesh object contains a triangular 3D mesh.
 |
 |      Parameters
 |      ------------
 |      vertices : (n, 3) float
 |        Array of vertex locations
 |      faces : (m, 3) or (m, 4) int
 |        Array of triangular or quad faces (triangulated on load)
 |      face_normals : (m, 3) float
 |        Array of normal vectors corresponding to faces
 |      vertex_normals : (n, 3) float
 |        Array of normal vectors for vertices
 |      face_colors : (n, 3|4) uint8
 |        Array of colors for faces
 |      vertex_colors : (n, 3|4) uint8
 |        Array of colors for vertices
 |      face_attributes : dict
 |        Attributes corresponding to faces
 |      vertex_attributes : dict
 |        Attributes corresponding to vertices
 |      metadata : dict
 |        Any metadata about the mesh
 |      process : bool
 |        if True, Nan and Inf values will be removed
 |        immediately and vertices will be merged
 |      validate : bool
 |        If True, degenerate and duplicate faces will be
 |        removed immediately, and some functions will alter
 |        the mesh to ensure consistent results.
 |      merge_tex : bool
 |        If True textured meshes with UV coordinates will
 |        have vertices merged regardless of UV coordinates
 |      merge_norm : bool
 |        If True, meshes with vertex normals will have
 |        vertices merged ignoring different normals
 |      use_embree : bool
 |        If True try to use pyembree raytracer.
 |        If pyembree is not available it will automatically fall
 |        back to a much slower rtree/numpy implementation
 |      initial_cache : dict
 |        A way to pass things to the cache in case expensive
 |        things were calculated before creating the mesh object.
 |      visual : ColorVisuals or TextureVisuals
 |        Assigned to self.visual
 |
 |  apply_transform(self, matrix: ArrayLike) -> Self
 |      Transform mesh by a homogeneous transformation matrix.
 |
 |      Does the bookkeeping to avoid recomputing things so this function
 |      should be used rather than directly modifying self.vertices
 |      if possible.
 |
 |      Parameters
 |      ------------
 |      matrix : (4, 4) float
 |        Homogeneous transformation matrix
 |
 |  compute_stable_poses(self, center_mass: Optional[numpy.ndarray[tuple[Any, ...], numpy.dtype[numpy.float64]]] = None, sigma: Union[float, numpy.floating] = 0.0, n_samples: Union[int, numpy.integer, numpy.unsignedinteger] = 1, threshold: Union[float, numpy.floating] = 0.0) -> tuple[numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.float64]], numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.float64]]]
 |      Computes stable orientations of a mesh and their quasi-static probabilities.
 |
 |      This method samples the location of the center of mass from a multivariate
 |      gaussian (mean at com, cov equal to identity times sigma) over n_samples.
 |      For each sample, it computes the stable resting poses of the mesh on a
 |      a planar workspace and evaluates the probabilities of landing in
 |      each pose if the object is dropped onto the table randomly.
 |
 |      This method returns the 4x4 homogeneous transform matrices that place
 |      the shape against the planar surface with the z-axis pointing upwards
 |      and a list of the probabilities for each pose.
 |      The transforms and probabilities that are returned are sorted, with the
 |      most probable pose first.
 |
 |      Parameters
 |      ------------
 |      center_mass : (3, ) float
 |        The object center of mass (if None, this method
 |        assumes uniform density and watertightness and
 |        computes a center of mass explicitly)
 |      sigma : float
 |        The covariance for the multivariate gaussian used
 |        to sample center of mass locations
 |      n_samples : int
 |        The number of samples of the center of mass location
 |      threshold : float
 |        The probability value at which to threshold
 |        returned stable poses
 |
 |      Returns
 |      -------
 |      transforms : (n, 4, 4) float
 |        The homogeneous matrices that transform the
 |        object to rest in a stable pose, with the
 |        new z-axis pointing upwards from the table
 |        and the object just touching the table.
 |
 |      probs : (n, ) float
 |        A probability ranging from 0.0 to 1.0 for each pose
 |
 |  contains(self, points: ArrayLike) -> numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.bool]]
 |      Given an array of points determine whether or not they
 |      are inside the mesh. This raises an error if called on a
 |      non-watertight mesh.
 |
 |      Parameters
 |      ------------
 |      points : (n, 3) float
 |        Points in cartesian space
 |
 |      Returns
 |      ---------
 |      contains : (n, ) bool
 |        Whether or not each point is inside the mesh
 |
 |  convert_units(self, desired: str, guess: bool = False) -> Self
 |      Convert the units of the mesh into a specified unit.
 |
 |      Parameters
 |      ------------
 |      desired : string
 |        Units to convert to (eg 'inches')
 |      guess : boolean
 |        If self.units are not defined should we
 |        guess the current units of the document and then convert?
 |
 |      Returns
 |      ------------
 |      self: trimesh.Trimesh
 |        Current mesh
 |
 |  convex_decomposition(self, **kwargs) -> list['Trimesh']
 |      Compute an approximate convex decomposition of a mesh
 |      using `pip install pyVHACD`.
 |
 |      Returns
 |      -------
 |      meshes
 |        List of convex meshes that approximate the original
 |      **kwargs : VHACD keyword arguments
 |
 |  copy(self, include_cache: bool = False, include_visual: bool = True) -> 'Trimesh'
 |      Safely return a copy of the current mesh.
 |
 |      By default, copied meshes will have emptied cache
 |      to avoid memory issues and so may be slow on initial
 |      operations until caches are regenerated.
 |
 |      Current object will *never* have its cache cleared.
 |
 |      Parameters
 |      ------------
 |      include_cache : bool
 |        If True, will shallow copy cached data to new mesh
 |      include_visual : bool
 |        If True, will copy visual information
 |
 |      Returns
 |      ---------
 |      copied : trimesh.Trimesh
 |        Copy of current mesh
 |
 |  difference(self, other: Union[ForwardRef('Trimesh'), collections.abc.Sequence['Trimesh']], engine: Literal['manifold', 'blender', None] = None, check_volume: bool = True, **kwargs) -> 'Trimesh'
 |      Boolean difference between this mesh and other meshes.
 |
 |      Parameters
 |      ------------
 |      other
 |        One or more meshes to difference with the current mesh.
 |      engine
 |        Which backend to use, the default
 |        recommendation is: `pip install manifold3d`.
 |      check_volume
 |        Raise an error if not all meshes are watertight
 |        positive volumes. Advanced users may want to ignore
 |        this check as it is expensive.
 |      kwargs
 |        Passed through to the `engine`.
 |
 |      Returns
 |      ---------
 |      difference : trimesh.Trimesh
 |        Difference between self and other Trimesh objects
 |
 |  eval_cached(self, statement: str, *args) -> Any
 |      Evaluate a statement and cache the result before returning.
 |
 |      Statements are evaluated inside the Trimesh object, and
 |
 |      Parameters
 |      ------------
 |      statement : str
 |        Statement of valid python code
 |      *args : list
 |        Available inside statement as args[0], etc
 |
 |      Returns
 |      -----------
 |      result : result of running eval on statement with args
 |
 |      Examples
 |      -----------
 |      r = mesh.eval_cached('np.dot(self.vertices, args[0])', [0, 0, 1])
 |
 |  export(self, file_obj: Union[str, pathlib.Path, IO, _io.BytesIO, _io.StringIO, BinaryIO, TextIO, _io.BufferedRandom, dict, NoneType] = None, file_type: Optional[str] = None, **kwargs) -> Union[dict, bytes, str]
 |      Export the current mesh to a file object.
 |      If file_obj is a filename, file will be written there.
 |
 |      Supported formats are stl, off, ply, collada, json,
 |      dict, glb, dict64, msgpack.
 |
 |      Parameters
 |      ------------
 |      file_obj : open writeable file object
 |        str, file name where to save the mesh
 |        None, return the export blob
 |      file_type : str
 |        Which file type to export as, if `file_name`
 |        is passed this is not required.
 |
 |      Returns
 |      ----------
 |      exported : bytes or str
 |        Result of exporter
 |
 |  extend_faces(self, new_faces: ArrayLike)
 |      Extend `mesh.faces` in-place with new triangles.
 |
 |      This does substantial bookkeeping: padding face colors
 |      and face attributes with default values, and preserving cached
 |      face normals to avoid recomputing every normal.
 |
 |      Parameters
 |      ------------
 |      new_faces : (n, 3) integer
 |        The new faces as indexes of `self.vertices`
 |
 |  fill_holes(self) -> bool
 |      Fill single triangle and single quad holes in the current mesh.
 |
 |      Returns
 |      ----------
 |      watertight : bool
 |        Is the mesh watertight after the function completes
 |
 |  fix_normals(self, multibody: Optional[bool] = None) -> Self
 |      Find and fix problems with self.face_normals and self.faces
 |      winding direction.
 |
 |      For face normals ensure that vectors are consistently pointed
 |      outwards, and that self.faces is wound in the correct direction
 |      for all connected components.
 |
 |      Parameters
 |      -------------
 |      multibody : None or bool
 |        Fix normals across multiple bodies or if unspecified
 |        check the current `Trimesh.body_count`.
 |
 |  intersection(self, other: Union[ForwardRef('Trimesh'), collections.abc.Sequence['Trimesh']], engine: Literal['manifold', 'blender', None] = None, check_volume: bool = True, **kwargs) -> 'Trimesh'
 |      Boolean intersection between this mesh and other meshes.
 |
 |      Parameters
 |      ------------
 |      other : trimesh.Trimesh, or list of trimesh.Trimesh objects
 |        Meshes to calculate intersections with
 |      engine
 |        Which backend to use, the default
 |        recommendation is: `pip install manifold3d`.
 |      check_volume
 |        Raise an error if not all meshes are watertight
 |        positive volumes. Advanced users may want to ignore
 |        this check as it is expensive.
 |      kwargs
 |        Passed through to the `engine`.
 |
 |      Returns
 |      ---------
 |      intersection : trimesh.Trimesh
 |        Mesh of the volume contained by all passed meshes
 |
 |  invert(self) -> Self
 |      Invert the mesh in-place by reversing the winding of every
 |      face and negating normals without dumping the cache.
 |
 |      Alters `self.faces` by reversing columns, and negating
 |      `self.face_normals` and `self.vertex_normals`.
 |
 |  merge_vertices(self, merge_tex: Optional[bool] = None, merge_norm: Optional[bool] = None, digits_vertex: Union[int, numpy.integer, numpy.unsignedinteger, NoneType] = None, digits_norm: Union[int, numpy.integer, numpy.unsignedinteger, NoneType] = None, digits_uv: Union[int, numpy.integer, numpy.unsignedinteger, NoneType] = None) -> None
 |      Removes duplicate vertices grouped by position and
 |      optionally texture coordinate and normal.
 |
 |      Parameters
 |      -------------
 |      merge_tex : bool
 |        If True textured meshes with UV coordinates will
 |        have vertices merged regardless of UV coordinates
 |      merge_norm : bool
 |        If True, meshes with vertex normals will have
 |        vertices merged ignoring different normals
 |      digits_vertex : None or int
 |        Number of digits to consider for vertex position
 |      digits_norm : int
 |        Number of digits to consider for unit normals
 |      digits_uv : int
 |        Number of digits to consider for UV coordinates
 |
 |  moment_inertia_frame(self, transform: ArrayLike) -> numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.float64]]
 |      Get the moment of inertia of this mesh with respect to
 |      an arbitrary frame, versus with respect to the center
 |      of mass as returned by `mesh.moment_inertia`.
 |
 |      For example if `transform` is an identity matrix `np.eye(4)`
 |      this will give the moment at the origin.
 |
 |      Uses the parallel axis theorum to move the center mass
 |      tensor to this arbitrary frame.
 |
 |      Parameters
 |      ------------
 |      transform : (4, 4) float
 |        Homogeneous transformation matrix.
 |
 |      Returns
 |      -------------
 |      inertia : (3, 3)
 |        Moment of inertia in the requested frame.
 |
 |  nondegenerate_faces(self, height: Union[float, numpy.floating] = 1e-08) -> numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.bool]]
 |      Identify degenerate faces (faces without 3 unique vertex indices)
 |      in the current mesh.
 |
 |      Usage example for removing them:
 |      `mesh.update_faces(mesh.nondegenerate_faces())`
 |
 |      If a height is specified, it will identify any face with a 2D oriented
 |      bounding box with one edge shorter than that height.
 |
 |      If not specified, it will identify any face with a zero normal.
 |
 |      Parameters
 |      ------------
 |      height : float
 |        If specified identifies faces with an oriented bounding
 |        box shorter than this on one side.
 |
 |      Returns
 |      -------------
 |      nondegenerate : (len(self.faces), ) bool
 |        Mask that can be used to remove faces
 |
 |  outline(self, face_ids: Optional[numpy.ndarray[tuple[Any, ...], numpy.dtype[numpy.int64]]] = None, **kwargs) -> trimesh.path.path.Path3D
 |      Given a list of face indexes find the outline of those
 |      faces and return it as a Path3D.
 |
 |      The outline is defined here as every edge which is only
 |      included by a single triangle.
 |
 |      Note that this implies a non-watertight mesh as the
 |      outline of a watertight mesh is an empty path.
 |
 |      Parameters
 |      ------------
 |      face_ids : (n, ) int
 |        Indices to compute the outline of.
 |        If None, outline of full mesh will be computed.
 |      **kwargs: passed to Path3D constructor
 |
 |      Returns
 |      ----------
 |      path : Path3D
 |        Curve in 3D of the outline
 |
 |  process(self, validate: bool = False, merge_tex: Optional[bool] = None, merge_norm: Optional[bool] = None) -> Self
 |      Do processing to make a mesh useful.
 |
 |      Does this by:
 |          1) removing NaN and Inf values
 |          2) merging duplicate vertices
 |      If validate:
 |          3) Remove triangles which have one edge
 |             of their 2D oriented bounding box
 |             shorter than tol.merge
 |          4) remove duplicated triangles
 |          5) Attempt to ensure triangles are consistently wound
 |             and normals face outwards.
 |
 |      Parameters
 |      ------------
 |      validate : bool
 |        Remove degenerate and duplicate faces.
 |      merge_tex : bool
 |        If True textured meshes with UV coordinates will
 |        have vertices merged regardless of UV coordinates
 |      merge_norm : bool
 |        If True, meshes with vertex normals will have
 |        vertices merged ignoring different normals
 |
 |      Returns
 |      ------------
 |      self: trimesh.Trimesh
 |        Current mesh
 |
 |  projected(self, normal: ArrayLike, **kwargs) -> trimesh.path.path.Path2D
 |      Project a mesh onto a plane and then extract the
 |      polygon that outlines the mesh projection on that
 |      plane.
 |
 |      Parameters
 |      ----------
 |      normal : (3,) float
 |        Normal to extract flat pattern along
 |      origin : None or (3,) float
 |        Origin of plane to project mesh onto
 |      ignore_sign : bool
 |        Allow a projection from the normal vector in
 |        either direction: this provides a substantial speedup
 |        on watertight meshes where the direction is irrelevant
 |        but if you have a triangle soup and want to discard
 |        backfaces you should set this to False.
 |      rpad : float
 |        Proportion to pad polygons by before unioning
 |        and then de-padding result by to avoid zero-width gaps.
 |      apad : float
 |        Absolute padding to pad polygons by before unioning
 |        and then de-padding result by to avoid zero-width gaps.
 |      tol_dot : float
 |        Tolerance for discarding on-edge triangles.
 |      precise : bool
 |        Use the precise projection computation using shapely.
 |      precise_eps : float
 |        Tolerance for precise triangle checks.
 |
 |      Returns
 |      ----------
 |      projected : trimesh.path.Path2D
 |        Outline of source mesh
 |
 |  register(self, other: Union[trimesh.parent.Geometry3D, numpy.ndarray[tuple[Any, ...], numpy.dtype[~_ScalarT]]], **kwargs) -> tuple[numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.float64]], numpy.float64]
 |      Align a mesh with another mesh or a PointCloud using
 |      the principal axes of inertia as a starting point which
 |      is refined by iterative closest point.
 |
 |      Parameters
 |      ------------
 |      other : trimesh.Trimesh or (n, 3) float
 |        Mesh or points in space
 |      samples : int
 |        Number of samples from mesh surface to align
 |      icp_first : int
 |        How many ICP iterations for the 9 possible
 |        combinations of
 |      icp_final : int
 |        How many ICP itertations for the closest
 |        candidate from the wider search
 |
 |      Returns
 |      -----------
 |      mesh_to_other : (4, 4) float
 |        Transform to align mesh to the other object
 |      cost : float
 |        Average square distance per point
 |
 |  remove_infinite_values(self) -> None
 |      Ensure that every vertex and face consists of finite numbers.
 |      This will remove vertices or faces containing np.nan and np.inf
 |
 |      Alters `self.faces` and `self.vertices`
 |
 |  remove_unreferenced_vertices(self) -> None
 |      Remove all vertices in the current mesh which are not
 |      referenced by a face.
 |
 |  rezero(self) -> None
 |      Translate the mesh so that all vertex vertices are positive
 |      and the lower bound of `self.bounds` will be exactly zero.
 |
 |      Alters `self.vertices`.
 |
 |  sample(self, count: Union[int, numpy.integer, numpy.unsignedinteger], return_index: bool = False, face_weight: Optional[numpy.ndarray[tuple[Any, ...], numpy.dtype[numpy.float64]]] = None)
 |      Return random samples distributed across the
 |      surface of the mesh
 |
 |      Parameters
 |      ------------
 |      count : int
 |        Number of points to sample
 |      return_index : bool
 |        If True will also return the index of which face each
 |        sample was taken from.
 |      face_weight : None or len(mesh.faces) float
 |        Weight faces by a factor other than face area.
 |        If None will be the same as face_weight=mesh.area
 |
 |      Returns
 |      ---------
 |      samples : (count, 3) float
 |        Points on surface of mesh
 |      face_index : (count, ) int
 |        Index of self.faces
 |
 |  scene(self, **kwargs) -> trimesh.scene.scene.Scene
 |      Returns a Scene object containing the current mesh.
 |
 |      Returns
 |      ---------
 |      scene : trimesh.scene.scene.Scene
 |        Contains just the current mesh
 |
 |  section(self, plane_normal: ArrayLike, plane_origin: ArrayLike, **kwargs) -> Optional[trimesh.path.path.Path3D]
 |      Returns a 3D cross section of the current mesh and a plane
 |      defined by origin and normal.
 |
 |      Parameters
 |      ------------
 |      plane_normal : (3,) float
 |        Normal vector of section plane.
 |      plane_origin : (3, ) float
 |        Point on the cross section plane.
 |
 |      Returns
 |      ---------
 |      intersections
 |        Curve of intersection or None if it was not hit by plane.
 |
 |  section_multiplane(self, plane_origin: ArrayLike, plane_normal: ArrayLike, heights: ArrayLike) -> list[typing.Optional[trimesh.path.path.Path2D]]
 |      Return multiple parallel cross sections of the current
 |      mesh in 2D.
 |
 |      Parameters
 |      ------------
 |      plane_origin : (3, ) float
 |        Point on the cross section plane
 |      plane_normal : (3) float
 |        Normal vector of section plane
 |      heights : (n, ) float
 |        Each section is offset by height along
 |        the plane normal.
 |
 |      Returns
 |      ---------
 |      paths : (n, ) Path2D or None
 |        2D cross sections at specified heights.
 |        path.metadata['to_3D'] contains transform
 |        to return 2D section back into 3D space.
 |
 |  show(self, viewer: Union[NoneType, collections.abc.Callable, Literal['gl', 'jupyter', 'marimo']] = None, **kwargs) -> trimesh.scene.scene.Scene
 |      Render the mesh in an opengl window. Requires pyglet.
 |
 |      Parameters
 |      ------------
 |      viewer : ViewerType
 |        What kind of viewer to use, such as
 |        `gl` to open a pyglet window
 |        `jupyter` for a jupyter notebook
 |        `marimo'` for a marimo notebook
 |        None for a "best guess"
 |      smooth : bool
 |        Run smooth shading on mesh or not,
 |        large meshes will be slow
 |
 |      Returns
 |      -----------
 |      scene : trimesh.scene.Scene
 |        Scene with current mesh in it
 |
 |  simplify_quadric_decimation(self, percent: Union[float, numpy.floating, NoneType] = None, face_count: Union[int, numpy.integer, numpy.unsignedinteger, NoneType] = None, aggression: Union[int, numpy.integer, numpy.unsignedinteger, NoneType] = None) -> 'Trimesh'
 |      A thin wrapper around `pip install fast-simplification`.
 |
 |      Parameters
 |      -----------
 |      percent
 |        A number between 0.0 and 1.0 for how much
 |      face_count
 |        Target number of faces desired in the resulting mesh.
 |      aggression
 |        An integer between `0` and `10`, the scale being roughly
 |        `0` is "slow and good" and `10` being "fast and bad."
 |
 |      Returns
 |      ---------
 |      simple : trimesh.Trimesh
 |        Simplified version of mesh.
 |
 |  slice_plane(self, plane_origin: ArrayLike, plane_normal: ArrayLike, cap: bool = False, face_index: Optional[ArrayLike] = None, **kwargs) -> 'Trimesh'
 |      Slice the mesh with a plane, returning a new mesh that is the
 |      portion of the original mesh to the positive normal side of the plane
 |
 |      plane_origin : (3,) float
 |        Point on plane to intersect with mesh
 |      plane_normal : (3,) float
 |        Normal vector of plane to intersect with mesh
 |      cap : bool
 |        If True, cap the result with a triangulated polygon
 |      face_index : ((m,) int)
 |          Indexes of mesh.faces to slice. When no mask is
 |          provided, the default is to slice all faces.
 |
 |      Returns
 |      ---------
 |      new_mesh: trimesh.Trimesh or None
 |        Subset of current mesh that intersects the half plane
 |        to the positive normal side of the plane
 |
 |  split(self, **kwargs) -> list['Trimesh']
 |      Split a mesh into multiple meshes from face
 |      connectivity.
 |
 |      If only_watertight is true it will only return
 |      watertight meshes and will attempt to repair
 |      single triangle or quad holes.
 |
 |      Parameters
 |      ----------
 |      mesh : trimesh.Trimesh
 |        The source multibody mesh to split
 |      only_watertight
 |        Only return watertight components and discard
 |        any connected component that isn't fully watertight.
 |      repair
 |        If set try to fill small holes in a mesh, before the
 |        discard step in `only_watertight.
 |      adjacency : (n, 2) int
 |        If passed will be used instead of `mesh.face_adjacency`
 |      engine
 |        Which graph engine to use for the connected components.
 |      kwargs
 |        Will be passed to `mesh.submesh`
 |
 |      Returns
 |      ----------
 |      meshes : (m,) trimesh.Trimesh
 |        Results of splitting based on parameters.
 |
 |  subdivide(self, face_index: Optional[ArrayLike] = None, iterations: Union[int, numpy.integer, numpy.unsignedinteger, NoneType] = None) -> 'Trimesh'
 |      Subdivide a mesh with each subdivided face replaced
 |      with four smaller faces. Will return a copy of current
 |      mesh with subdivided faces.
 |
 |      Parameters
 |      ------------
 |      face_index : (m, ) int or None
 |        If None all faces of mesh will be subdivided
 |        If (m, ) int array of indices: only specified faces will be
 |        subdivided. Note that in this case the mesh will generally
 |        no longer be manifold, as the additional vertex on the midpoint
 |        will not be used by the adjacent faces to the faces specified,
 |        and an additional postprocessing step will be required to
 |        make resulting mesh watertight
 |      iterations : int
 |        If passed will run subdivisions multiple times recursively.
 |        NOT COMPATIBLE with `face_index` and will raise a `ValueError`
 |        if both arguments are passed.
 |
 |      Returns
 |      ------------
 |      mesh: trimesh.Trimesh
 |        The copy of current mesh with subdivided faces.
 |
 |  subdivide_loop(self, iterations: Union[int, numpy.integer, numpy.unsignedinteger, NoneType] = None) -> 'Trimesh'
 |      Subdivide a mesh by dividing each triangle into four
 |      triangles and approximating their smoothed surface
 |      using loop subdivision. Loop subdivision often looks
 |      better on triangular meshes than catmul-clark, which
 |      operates primarily on quads.
 |
 |      Parameters
 |      ------------
 |      iterations : int
 |        Number of iterations to run subdivision.
 |      multibody : bool
 |        If True will try to subdivide for each submesh
 |
 |      Returns
 |      ------------
 |      mesh: trimesh.Trimesh
 |        The copy of current mesh with subdivided faces.
 |
 |  subdivide_to_size(self, max_edge: Union[float, numpy.floating], max_iter: Union[int, numpy.integer, numpy.unsignedinteger] = 10, return_index: bool = False) -> Union[ForwardRef('Trimesh'), tuple['Trimesh', numpy.ndarray[tuple[Any, ...], numpy.dtype[numpy.int64]]]]
 |      Subdivide a mesh until every edge is shorter than a
 |      specified length.
 |
 |      Will return a triangle soup, not a nicely structured mesh.
 |
 |      Parameters
 |      ------------
 |      max_edge : float
 |          Maximum length of any edge in the result
 |      max_iter : int
 |          The maximum number of times to run subdivision
 |      return_index : bool
 |          If True, return index of original face for new faces
 |
 |      Returns
 |      ------------
 |      mesh: trimesh.Trimesh
 |        The copy of current mesh with subdivided faces.
 |
 |  submesh(self, faces_sequence: collections.abc.Sequence[ArrayLike], only_watertight: bool = False, repair: bool = False, **kwargs) -> Union[ForwardRef('Trimesh'), list['Trimesh']]
 |      Return a subset of the mesh.
 |
 |      Parameters
 |      ------------
 |      faces_sequence : sequence (m, ) int
 |        Face indices of mesh
 |      only_watertight : bool
 |        Only return submeshes which are watertight
 |      repair
 |        Try to repair the submesh if it is not watertight
 |      append : bool
 |        Return a single mesh which has the faces appended.
 |        if this flag is set, only_watertight is ignored
 |
 |      Returns
 |      ---------
 |      submesh : Trimesh or (n,) Trimesh
 |        Single mesh if `append` or list of submeshes
 |
 |  to_dict(self) -> dict[str, typing.Union[str, list[list[float]], list[list[int]]]]
 |      Return a dictionary representation of the current mesh
 |      with keys that can be used as the kwargs for the
 |      Trimesh constructor and matches the schema in:
 |      `trimesh/resources/schema/primitive/trimesh.schema.json`
 |
 |      Returns
 |      ----------
 |      result : dict
 |        Matches schema and Trimesh constructor.
 |
 |  union(self, other: Union[ForwardRef('Trimesh'), collections.abc.Sequence['Trimesh']], engine: Literal['manifold', 'blender', None] = None, check_volume: bool = True, **kwargs) -> 'Trimesh'
 |      Boolean union between this mesh and other meshes.
 |
 |      Parameters
 |      ------------
 |      other : Trimesh or (n, ) Trimesh
 |        Other meshes to union
 |      engine
 |        Which backend to use, the default
 |        recommendation is: `pip install manifold3d`.
 |      check_volume
 |        Raise an error if not all meshes are watertight
 |        positive volumes. Advanced users may want to ignore
 |        this check as it is expensive.
 |      kwargs
 |        Passed through to the `engine`.
 |
 |      Returns
 |      ---------
 |      union : trimesh.Trimesh
 |        Union of self and other Trimesh objects
 |
 |  unique_faces(self) -> numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.bool]]
 |      On the current mesh find which faces are unique.
 |
 |      Returns
 |      --------
 |      unique : (len(faces),) bool
 |        A mask where the first occurrence of a unique face is true.
 |
 |  unmerge_vertices(self) -> None
 |      Removes all face references so that every face contains
 |      three unique vertex indices and no faces are adjacent.
 |
 |  unwrap(self, image: <module 'PIL.Image' from '/home/merrimen/scanner-project/.venv/lib/python3.12/site-packages/PIL/Image.py'> = None) -> 'Trimesh'
 |      Returns a Trimesh object equivalent to the current mesh where
 |      the vertices have been assigned uv texture coordinates. Vertices
 |      may be split into as many as necessary by the unwrapping
 |      algorithm, depending on how many uv maps they appear in.
 |
 |      Requires `pip install xatlas`
 |
 |      Parameters
 |      ------------
 |      image : None or PIL.Image
 |        Image to assign to the material
 |
 |      Returns
 |      --------
 |      unwrapped : trimesh.Trimesh
 |        Mesh with unwrapped uv coordinates
 |
 |  update_faces(self, mask: ArrayLike) -> None
 |      In many cases, we will want to remove specific faces.
 |      However, there is additional bookkeeping to do this cleanly.
 |      This function updates the set of faces with a validity mask,
 |      as well as keeping track of normals and colors.
 |
 |      Parameters
 |      ------------
 |      mask : (m) int or (len(self.faces)) bool
 |        Mask to remove faces
 |
 |  update_vertices(self, mask: ArrayLike, inverse: Optional[ArrayLike] = None) -> None
 |      Update vertices with a mask.
 |
 |      Parameters
 |      ------------
 |      mask : (len(self.vertices)) bool
 |        Array of which vertices to keep
 |      inverse : (len(self.vertices)) int
 |        Array to reconstruct vertex references
 |        such as output by np.unique
 |
 |  voxelized(self, pitch: Union[float, numpy.floating, NoneType], method: str = 'subdivide', **kwargs)
 |      Return a VoxelGrid object representing the current mesh
 |      discretized into voxels at the specified pitch
 |
 |      Parameters
 |      ------------
 |      pitch : float
 |        The edge length of a single voxel
 |      method: implementation key. See `trimesh.voxel.creation.voxelizers`
 |      **kwargs: additional kwargs passed to the specified implementation.
 |
 |      Returns
 |      ----------
 |      voxelized : VoxelGrid object
 |        Representing the current mesh
 |
 |  ----------------------------------------------------------------------
 |  Readonly properties defined here:
 |
 |  area
 |      Summed area of all triangles in the current mesh.
 |
 |      Returns
 |      ---------
 |      area : float
 |        Surface area of mesh
 |
 |  area_faces
 |      The area of each face in the mesh.
 |
 |      Returns
 |      ---------
 |      area_faces : (n, ) float
 |        Area of each face
 |
 |  body_count
 |      How many connected groups of vertices exist in this mesh.
 |      Note that this number may differ from result in mesh.split,
 |      which is calculated from FACE rather than vertex adjacency.
 |
 |      Returns
 |      -----------
 |      count : int
 |        Number of connected vertex groups
 |
 |  bounds
 |      The axis aligned bounds of the faces of the mesh.
 |
 |      Returns
 |      -----------
 |      bounds : (2, 3) float or None
 |        Bounding box with [min, max] coordinates
 |        If mesh is empty will return None
 |
 |  centroid
 |      The point in space which is the average of the triangle
 |      centroids weighted by the area of each triangle.
 |
 |      This will be valid even for non-watertight meshes,
 |      unlike self.center_mass
 |
 |      Returns
 |      ----------
 |      centroid : (3, ) float
 |        The average vertex weighted by face area
 |
 |  convex_hull
 |      Returns a Trimesh object representing the convex hull of
 |      the current mesh.
 |
 |      Returns
 |      --------
 |      convex : trimesh.Trimesh
 |        Mesh of convex hull of current mesh
 |
 |  edges
 |      Edges of the mesh (derived from faces).
 |
 |      Returns
 |      ---------
 |      edges : (n, 2) int
 |        List of vertex indices making up edges
 |
 |  edges_face
 |      Which face does each edge belong to.
 |
 |      Returns
 |      ---------
 |      edges_face : (n, ) int
 |        Index of self.faces
 |
 |  edges_sorted
 |      Edges sorted along axis 1
 |
 |      Returns
 |      ----------
 |      edges_sorted : (n, 2)
 |        Same as self.edges but sorted along axis 1
 |
 |  edges_sorted_tree
 |      A KDTree for mapping edges back to edge index.
 |
 |      Returns
 |      ------------
 |      tree : scipy.spatial.cKDTree
 |        Tree when queried with edges will return
 |        their index in mesh.edges_sorted
 |
 |  edges_sparse
 |      Edges in sparse bool COO graph format where connected
 |      vertices are True.
 |
 |      Returns
 |      ----------
 |      sparse: (len(self.vertices), len(self.vertices)) bool
 |        Sparse graph in COO format
 |
 |  edges_unique
 |      The unique edges of the mesh.
 |
 |      Returns
 |      ----------
 |      edges_unique : (n, 2) int
 |        Vertex indices for unique edges
 |
 |  edges_unique_inverse
 |      Return the inverse required to reproduce
 |      self.edges_sorted from self.edges_unique.
 |
 |      Useful for referencing edge properties:
 |      mesh.edges_unique[mesh.edges_unique_inverse] == m.edges_sorted
 |
 |      Returns
 |      ----------
 |      inverse : (len(self.edges), ) int
 |        Indexes of self.edges_unique
 |
 |  edges_unique_length
 |      How long is each unique edge.
 |
 |      Returns
 |      ----------
 |      length : (len(self.edges_unique), ) float
 |        Length of each unique edge
 |
 |  euler_number
 |      Return the Euler characteristic (a topological invariant) for the mesh
 |      In order to guarantee correctness, this should be called after
 |      remove_unreferenced_vertices
 |
 |      Returns
 |      ----------
 |      euler_number : int
 |        Topological invariant
 |
 |  extents
 |      The length, width, and height of the axis aligned
 |      bounding box of the mesh.
 |
 |      Returns
 |      -----------
 |      extents : (3, ) float or None
 |        Array containing axis aligned [length, width, height]
 |        If mesh is empty returns None
 |
 |  face_adjacency
 |      Find faces that share an edge i.e. 'adjacent' faces.
 |
 |      Returns
 |      ----------
 |      adjacency : (n, 2) int
 |        Pairs of faces which share an edge
 |
 |      Examples
 |      ---------
 |
 |      In [1]: mesh = trimesh.load('models/featuretype.STL')
 |
 |      In [2]: mesh.face_adjacency
 |      Out[2]:
 |      array([[   0,    1],
 |             [   2,    3],
 |             [   0,    3],
 |             ...,
 |             [1112,  949],
 |             [3467, 3475],
 |             [1113, 3475]])
 |
 |      In [3]: mesh.faces[mesh.face_adjacency[0]]
 |      Out[3]:
 |      TrackedArray([[   1,    0,  408],
 |                    [1239,    0,    1]], dtype=int64)
 |
 |      In [4]: import networkx as nx
 |
 |      In [5]: graph = nx.from_edgelist(mesh.face_adjacency)
 |
 |      In [6]: groups = nx.connected_components(graph)
 |
 |  face_adjacency_angles
 |      Return the unsigned angle between adjacent faces
 |      in radians.
 |
 |      Note that if you want a signed angle you can easily
 |      use the `face_adjacency_convex` attribute to get a
 |      signed angle with advanced indexing:
 |
 |      ```
 |      # get a sign per face_adacency pair from the "is it convex" boolean
 |      signs = np.array([-1.0, 1.0])[mesh.face_adjacency_convex.astype(np.int64)]
 |
 |      # apply the signs to the angles
 |      angles = mesh.face_adjacency_angles * signs
 |      ```
 |
 |      Returns
 |      --------
 |      adjacency_angle : (len(self.face_adjacency), ) float
 |        Unsigned angle between adjacent faces
 |        corresponding with `self.face_adjacency`
 |
 |  face_adjacency_convex
 |      Return faces which are adjacent and locally convex.
 |
 |      What this means is that given faces A and B, the one vertex
 |      in B that is not shared with A, projected onto the plane of A
 |      has a projection that is zero or negative.
 |
 |      Returns
 |      ----------
 |      are_convex : (len(self.face_adjacency), ) bool
 |        Face pairs that are locally convex
 |
 |  face_adjacency_edges
 |      Returns the edges that are shared by the adjacent faces.
 |
 |      Returns
 |      --------
 |      edges : (n, 2) int
 |         Vertex indices which correspond to face_adjacency
 |
 |  face_adjacency_edges_tree
 |      A KDTree for mapping edges back face adjacency index.
 |
 |      Returns
 |      ------------
 |      tree : scipy.spatial.cKDTree
 |        Tree when queried with SORTED edges will return
 |        their index in mesh.face_adjacency
 |
 |  face_adjacency_projections
 |      The projection of the non-shared vertex of a triangle onto
 |      its adjacent face
 |
 |      Returns
 |      ----------
 |      projections : (len(self.face_adjacency), ) float
 |        Dot product of vertex
 |        onto plane of adjacent triangle.
 |
 |  face_adjacency_radius
 |      The approximate radius of a cylinder that fits inside adjacent faces.
 |
 |      Returns
 |      ------------
 |      radii : (len(self.face_adjacency), ) float
 |        Approximate radius formed by triangle pair
 |
 |  face_adjacency_span
 |      The approximate perpendicular projection of the non-shared
 |      vertices in a pair of adjacent faces onto the shared edge of
 |      the two faces.
 |
 |      Returns
 |      ------------
 |      span : (len(self.face_adjacency), ) float
 |        Approximate span between the non-shared vertices
 |
 |  face_adjacency_tree
 |      An R-tree of face adjacencies.
 |
 |      Returns
 |      --------
 |      tree
 |        Where each edge in self.face_adjacency has a
 |        rectangular cell
 |
 |  face_adjacency_unshared
 |      Return the vertex index of the two vertices not in the shared
 |      edge between two adjacent faces
 |
 |      Returns
 |      -----------
 |      vid_unshared : (len(mesh.face_adjacency), 2) int
 |        Indexes of mesh.vertices
 |
 |  face_angles
 |      Returns the angle at each vertex of a face.
 |
 |      Returns
 |      --------
 |      angles : (len(self.faces), 3) float
 |        Angle at each vertex of a face
 |
 |  face_angles_sparse
 |      A sparse matrix representation of the face angles.
 |
 |      Returns
 |      ----------
 |      sparse : scipy.sparse.coo_matrix
 |        Float sparse matrix with with shape:
 |        (len(self.vertices), len(self.faces))
 |
 |  face_neighborhood
 |      Find faces that share a vertex i.e. 'neighbors' faces.
 |
 |      Returns
 |      ----------
 |      neighborhood : (n, 2) int
 |        Pairs of faces which share a vertex
 |
 |  faces_sparse
 |      A sparse matrix representation of the faces.
 |
 |      Returns
 |      ----------
 |      sparse : scipy.sparse.coo_matrix
 |        Has properties:
 |        dtype : bool
 |        shape : (len(self.vertices), len(self.faces))
 |
 |  faces_unique_edges
 |      For each face return which indexes in mesh.unique_edges constructs
 |      that face.
 |
 |      Returns
 |      ---------
 |      faces_unique_edges : (len(self.faces), 3) int
 |        Indexes of self.edges_unique that
 |        construct self.faces
 |
 |      Examples
 |      ---------
 |      In [0]: mesh.faces[:2]
 |      Out[0]:
 |      TrackedArray([[    1,  6946, 24224],
 |                    [ 6946,  1727, 24225]])
 |
 |      In [1]: mesh.edges_unique[mesh.faces_unique_edges[:2]]
 |      Out[1]:
 |      array([[[    1,  6946],
 |              [ 6946, 24224],
 |              [    1, 24224]],
 |             [[ 1727,  6946],
 |              [ 1727, 24225],
 |              [ 6946, 24225]]])
 |
 |  facets
 |      Return a list of face indices for coplanar adjacent faces.
 |
 |      Returns
 |      ---------
 |      facets : (n, ) sequence of (m, ) int
 |        Groups of indexes of self.faces
 |
 |  facets_area
 |      Return an array containing the area of each facet.
 |
 |      Returns
 |      ---------
 |      area : (len(self.facets), ) float
 |        Total area of each facet (group of faces)
 |
 |  facets_boundary
 |      Return the edges which represent the boundary of each facet
 |
 |      Returns
 |      ---------
 |      edges_boundary : sequence of (n, 2) int
 |        Indices of self.vertices
 |
 |  facets_normal
 |      Return the normal of each facet
 |
 |      Returns
 |      ---------
 |      normals: (len(self.facets), 3) float
 |        A unit normal vector for each facet
 |
 |  facets_on_hull
 |      Find which facets of the mesh are on the convex hull.
 |
 |      Returns
 |      ---------
 |      on_hull : (len(mesh.facets), ) bool
 |        is A facet on the meshes convex hull or not
 |
 |  facets_origin
 |      Return a point on the facet plane.
 |
 |      Returns
 |      ------------
 |      origins : (len(self.facets), 3) float
 |        A point on each facet plane
 |
 |  identifier
 |      Return a float vector which is unique to the mesh
 |      and is robust to rotation and translation.
 |
 |      Returns
 |      -----------
 |      identifier : (7,) float
 |        Identifying properties of the current mesh
 |
 |  identifier_hash
 |      A hash of the rotation invariant identifier vector.
 |
 |      Returns
 |      ---------
 |      hashed : str
 |        Hex string of the SHA256 hash from
 |        the identifier vector at hand-tuned sigfigs.
 |
 |  integral_mean_curvature
 |      The integral mean curvature, or the surface integral of the mean curvature.
 |
 |      Returns
 |      ---------
 |      area : float
 |        Integral mean curvature of mesh
 |
 |  is_convex
 |      Check if a mesh is convex or not.
 |
 |      Returns
 |      ----------
 |      is_convex: bool
 |        Is mesh convex or not
 |
 |  is_empty
 |      Does the current mesh have data defined.
 |
 |      Returns
 |      --------
 |      empty : bool
 |        If True, no data is set on the current mesh
 |
 |  is_volume
 |      Check if a mesh has all the properties required to represent
 |      a valid volume, rather than just a surface.
 |
 |      These properties include being watertight, having consistent
 |      winding and outward facing normals.
 |
 |      Returns
 |      ---------
 |      valid
 |        Does the mesh represent a volume
 |
 |  is_watertight
 |      Check if a mesh is watertight by making sure every edge is
 |      included in two faces.
 |
 |      Returns
 |      ----------
 |      is_watertight : bool
 |        Is mesh watertight or not
 |
 |  is_winding_consistent
 |      Does the mesh have consistent winding or not.
 |      A mesh with consistent winding has each shared edge
 |      going in an opposite direction from the other in the pair.
 |
 |      Returns
 |      --------
 |      consistent : bool
 |        Is winding is consistent or not
 |
 |  kdtree
 |      Return a scipy.spatial.cKDTree of the vertices of the mesh.
 |      Not cached as this lead to observed memory issues and segfaults.
 |
 |      Returns
 |      ---------
 |      tree : scipy.spatial.cKDTree
 |        Contains mesh.vertices
 |
 |  mass
 |      Mass of the current mesh, based on specified density and
 |      volume. If the current mesh isn't watertight this is garbage.
 |
 |      Returns
 |      ---------
 |      mass : float
 |        Mass of the current mesh
 |
 |  mass_properties
 |      Returns the mass properties of the current mesh.
 |
 |      Assumes uniform density, and result is probably garbage if mesh
 |      isn't watertight.
 |
 |      Returns
 |      ----------
 |      properties : dict
 |        With keys:
 |        'volume'      : in global units^3
 |        'mass'        : From specified density
 |        'density'     : Included again for convenience (same as kwarg density)
 |        'inertia'     : Taken at the center of mass and aligned with global
 |                       coordinate system
 |        'center_mass' : Center of mass location, in global coordinate system
 |
 |  moment_inertia
 |      Return the moment of inertia matrix of the current mesh.
 |      If mesh isn't watertight this is garbage. The returned
 |      moment of inertia is *axis aligned* at the mesh's center
 |      of mass `mesh.center_mass`. If you want the moment at any
 |      other frame including the origin call:
 |      `mesh.moment_inertia_frame`
 |
 |      Returns
 |      ---------
 |      inertia : (3, 3) float
 |        Moment of inertia of the current mesh at the center of
 |        mass and aligned with the cartesian axis.
 |
 |  principal_inertia_components
 |      Return the principal components of inertia
 |
 |      Ordering corresponds to mesh.principal_inertia_vectors
 |
 |      Returns
 |      ----------
 |      components : (3, ) float
 |        Principal components of inertia
 |
 |  principal_inertia_transform
 |      A transform which moves the current mesh so the principal
 |      inertia vectors are on the X,Y, and Z axis, and the centroid is
 |      at the origin.
 |
 |      Returns
 |      ----------
 |      transform : (4, 4) float
 |        Homogeneous transformation matrix
 |
 |  principal_inertia_vectors
 |      Return the principal axis of inertia as unit vectors.
 |      The order corresponds to `mesh.principal_inertia_components`.
 |
 |      Returns
 |      ----------
 |      vectors : (3, 3) float
 |        Three vectors pointing along the
 |        principal axis of inertia directions
 |
 |  referenced_vertices
 |      Which vertices in the current mesh are referenced by a face.
 |
 |      Returns
 |      -------------
 |      referenced : (len(self.vertices), ) bool
 |        Which vertices are referenced by a face
 |
 |  smooth_shaded
 |      Smooth shading in OpenGL relies on which vertices are shared,
 |      this function will disconnect regions above an angle threshold
 |      and return a non-watertight version which will look better
 |      in an OpenGL rendering context.
 |
 |      If you would like to use non-default arguments see `graph.smooth_shade`.
 |
 |      Returns
 |      ---------
 |      smooth_shaded : trimesh.Trimesh
 |        Non watertight version of current mesh.
 |
 |  symmetry
 |      Check whether a mesh has rotational symmetry around
 |      an axis (radial) or point (spherical).
 |
 |      Returns
 |      -----------
 |      symmetry : None, 'radial', 'spherical'
 |        What kind of symmetry does the mesh have.
 |
 |  symmetry_axis
 |      If a mesh has rotational symmetry, return the axis.
 |
 |      Returns
 |      ------------
 |      axis : (3, ) float
 |        Axis around which a 2D profile was revolved to create this mesh.
 |
 |  symmetry_section
 |      If a mesh has rotational symmetry return the two
 |      vectors which make up a section coordinate frame.
 |
 |      Returns
 |      ----------
 |      section : (2, 3) float
 |        Vectors to take a section along
 |
 |  triangles
 |      Actual triangles of the mesh (points, not indexes)
 |
 |      Returns
 |      ---------
 |      triangles : (n, 3, 3) float
 |        Points of triangle vertices
 |
 |  triangles_center
 |      The center of each triangle (barycentric [1/3, 1/3, 1/3])
 |
 |      Returns
 |      ---------
 |      triangles_center : (len(self.faces), 3) float
 |        Center of each triangular face
 |
 |  triangles_cross
 |      The cross product of two edges of each triangle.
 |
 |      Returns
 |      ---------
 |      crosses : (n, 3) float
 |        Cross product of each triangle
 |
 |  triangles_tree
 |      An R-tree containing each face of the mesh.
 |
 |      Returns
 |      ----------
 |      tree : rtree.index
 |        Each triangle in self.faces has a rectangular cell
 |
 |  vertex_adjacency_graph
 |      Returns a networkx graph representing the vertices and their connections
 |      in the mesh.
 |
 |      Returns
 |      ---------
 |      graph: networkx.Graph
 |        Graph representing vertices and edges between
 |        them where vertices are nodes and edges are edges
 |
 |      Examples
 |      ----------
 |      This is useful for getting nearby vertices for a given vertex,
 |      potentially for some simple smoothing techniques.
 |
 |      mesh = trimesh.primitives.Box()
 |      graph = mesh.vertex_adjacency_graph
 |      graph.neighbors(0)
 |      > [1, 2, 3, 4]
 |
 |  vertex_defects
 |      Return the vertex defects, or (2*pi) minus the sum of the angles
 |      of every face that includes that vertex.
 |
 |      If a vertex is only included by coplanar triangles, this
 |      will be zero. For convex regions this is positive, and
 |      concave negative.
 |
 |      Returns
 |      --------
 |      vertex_defect : (len(self.vertices), ) float
 |        Vertex defect at the every vertex
 |
 |  vertex_degree
 |      Return the number of faces each vertex is included in.
 |
 |      Returns
 |      ----------
 |      degree : (len(self.vertices), ) int
 |        Number of faces each vertex is included in
 |
 |  vertex_faces
 |      A representation of the face indices that correspond to each vertex.
 |
 |      Returns
 |      ----------
 |      vertex_faces : (n,m) int
 |        Each row contains the face indices that correspond to the given vertex,
 |        padded with -1 up to the max number of faces corresponding to any one vertex
 |        Where n == len(self.vertices), m == max number of faces for a single vertex
 |
 |  vertex_neighbors
 |      The vertex neighbors of each vertex of the mesh, determined from
 |      the cached vertex_adjacency_graph, if already existent.
 |
 |      Returns
 |      ----------
 |      vertex_neighbors : (len(self.vertices), ) int
 |        Represents immediate neighbors of each vertex along
 |        the edge of a triangle
 |
 |      Examples
 |      ----------
 |      This is useful for getting nearby vertices for a given vertex,
 |      potentially for some simple smoothing techniques.
 |
 |      >>> mesh = trimesh.primitives.Box()
 |      >>> mesh.vertex_neighbors[0]
 |      [1, 2, 3, 4]
 |
 |  volume
 |      Volume of the current mesh calculated using a surface
 |      integral. If the current mesh isn't watertight this is
 |      garbage.
 |
 |      Returns
 |      ---------
 |      volume : float
 |        Volume of the current mesh
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  center_mass
 |      The point in space which is the center of mass/volume.
 |
 |      Returns
 |      -----------
 |      center_mass : (3, ) float
 |         Volumetric center of mass of the mesh.
 |
 |  density
 |      The density of the mesh used in inertia calculations.
 |
 |      Returns
 |      -----------
 |      density
 |        The density of the primitive.
 |
 |  face_normals
 |      Return the unit normal vector for each face.
 |
 |      If a face is degenerate and a normal can't be generated
 |      a zero magnitude unit vector will be returned for that face.
 |
 |      Returns
 |      -----------
 |      normals : (len(self.faces), 3) float64
 |        Normal vectors of each face
 |
 |  faces
 |      The faces of the mesh.
 |
 |      This is regarded as core information which cannot be
 |      regenerated from cache and as such is stored in
 |      `self._data` which tracks the array for changes and
 |      clears cached values of the mesh altered.
 |
 |      Returns
 |      ----------
 |      faces : (n, 3) int64
 |        References for `self.vertices` for triangles.
 |
 |  mutable
 |      Is the current mesh allowed to be altered in-place?
 |
 |      Returns
 |      -------------
 |      mutable
 |        If data is allowed to be set for the mesh.
 |
 |  vertex_normals
 |      The vertex normals of the mesh. If the normals were loaded
 |      we check to make sure we have the same number of vertex
 |      normals and vertices before returning them. If there are
 |      no vertex normals defined or a shape mismatch we  calculate
 |      the vertex normals from the mean normals of the faces the
 |      vertex is used in.
 |
 |      Returns
 |      ----------
 |      vertex_normals : (n, 3) float
 |        Represents the surface normal at each vertex.
 |        Where n == len(self.vertices)
 |
 |  vertices
 |      The vertices of the mesh.
 |
 |      This is regarded as core information which cannot be
 |      generated from cache and as such is stored in self._data
 |      which tracks the array for changes and clears cached
 |      values of the mesh if this is altered.
 |
 |      Returns
 |      ----------
 |      vertices : (n, 3) float
 |        Points in cartesian space referenced by self.faces
 |
 |  visual
 |      Get the stored visuals for the current mesh.
 |
 |      Returns
 |      -------------
 |      visual : ColorVisuals or TextureVisuals
 |        Contains visual information about the mesh
 |
 |  ----------------------------------------------------------------------
 |  Data and other attributes defined here:
 |
 |  __abstractmethods__ = frozenset()
 |
 |  __annotations__ = {}
 |
 |  ----------------------------------------------------------------------
 |  Methods inherited from trimesh.parent.Geometry3D:
 |
 |  apply_obb(self, **kwargs) -> numpy.ndarray[tuple[typing.Any, ...], numpy.dtype[numpy.float64]]
 |      Apply the oriented bounding box transform to the current mesh.
 |
 |      This will result in a mesh with an AABB centered at the
 |      origin and the same dimensions as the OBB.
 |
 |      Parameters
 |      ------------
 |      kwargs
 |        Passed through to `bounds.oriented_bounds`
 |
 |      Returns
 |      ----------
 |      matrix : (4, 4) float
 |        Transformation matrix that was applied
 |        to mesh to move it into OBB frame
 |
 |  ----------------------------------------------------------------------
 |  Readonly properties inherited from trimesh.parent.Geometry3D:
 |
 |  bounding_box
 |      An axis aligned bounding box for the current mesh.
 |
 |      Returns
 |      ----------
 |      aabb : trimesh.primitives.Box
 |        Box object with transform and extents defined
 |        representing the axis aligned bounding box of the mesh
 |
 |  bounding_box_oriented
 |      An oriented bounding box for the current mesh.
 |
 |      Returns
 |      ---------
 |      obb : trimesh.primitives.Box
 |        Box object with transform and extents defined
 |        representing the minimum volume oriented
 |        bounding box of the mesh
 |
 |  bounding_cylinder
 |      A minimum volume bounding cylinder for the current mesh.
 |
 |      Returns
 |      --------
 |      mincyl : trimesh.primitives.Cylinder
 |        Cylinder primitive containing current mesh
 |
 |  bounding_primitive
 |      The minimum volume primitive (box, sphere, or cylinder) that
 |      bounds the mesh.
 |
 |      Returns
 |      ---------
 |      bounding_primitive : object
 |        Smallest primitive which bounds the mesh:
 |        trimesh.primitives.Sphere
 |        trimesh.primitives.Box
 |        trimesh.primitives.Cylinder
 |
 |  bounding_sphere
 |      A minimum volume bounding sphere for the current mesh.
 |
 |      Note that the Sphere primitive returned has an unpadded
 |      exact `sphere_radius` so while the distance of every vertex
 |      of the current mesh from sphere_center will be less than
 |      sphere_radius, the faceted sphere primitive may not
 |      contain every vertex.
 |
 |      Returns
 |      --------
 |      minball : trimesh.primitives.Sphere
 |        Sphere primitive containing current mesh
 |
 |  ----------------------------------------------------------------------
 |  Methods inherited from trimesh.parent.Geometry:
 |
 |  __hash__(self)
 |      Get a hash of the current geometry.
 |
 |      Returns
 |      ---------
 |      hash
 |        Hash of current graph and geometry.
 |
 |  __radd__(self, other)
 |      Concatenate the geometry allowing concatenation with
 |      built in `sum()` function:
 |        `sum(Iterable[trimesh.Trimesh])`
 |
 |      Parameters
 |      ------------
 |      other : Geometry
 |        Geometry or 0
 |
 |      Returns
 |      ----------
 |      concat : Geometry
 |        Geometry of combined result
 |
 |  __repr__(self) -> str
 |      Print quick summary of the current geometry without
 |      computing properties.
 |
 |      Returns
 |      -----------
 |      repr : str
 |        Human readable quick look at the geometry.
 |
 |  apply_scale(self, scaling)
 |      Scale the mesh.
 |
 |      Parameters
 |      ----------
 |      scaling : float or (3,) float
 |        Scale factor to apply to the mesh
 |
 |  apply_translation(self, translation: ArrayLike)
 |      Translate the current mesh.
 |
 |      Parameters
 |      ----------
 |      translation : (3,) float
 |        Translation in XYZ
 |
 |  ----------------------------------------------------------------------
 |  Readonly properties inherited from trimesh.parent.Geometry:
 |
 |  scale
 |      A loosely specified "order of magnitude scale" for the
 |      geometry which always returns a value and can be used
 |      to make code more robust to large scaling differences.
 |
 |      It returns the diagonal of the axis aligned bounding box
 |      or if anything is invalid or undefined, `1.0`.
 |
 |      Returns
 |      ----------
 |      scale : float
 |        Approximate order of magnitude scale of the geometry.
 |
 |  source
 |      Where and what was this current geometry loaded from?
 |
 |      Returns
 |      --------
 |      source
 |        If loaded from a file, has the path, type, etc.
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited from trimesh.parent.Geometry:
 |
 |  __dict__
 |      dictionary for instance variables
 |
 |  __weakref__
 |      list of weak references to the object
 |
 |  units
 |      Definition of units for the mesh.
 |
 |      Returns
 |      ----------
 |      units : str
 |        Unit system mesh is in, or None if not defined

