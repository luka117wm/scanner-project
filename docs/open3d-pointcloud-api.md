Help on class PointCloud in module open3d.cuda.pybind.geometry:

class PointCloud(Geometry3D)
 |  PointCloud class. A point cloud consists of point coordinates, and optionally point colors and point normals.
 |
 |  Method resolution order:
 |      PointCloud
 |      Geometry3D
 |      Geometry
 |      pybind11_builtins.pybind11_object
 |      builtins.object
 |
 |  Methods defined here:
 |
 |  __add__(...)
 |      __add__(self: open3d.cuda.pybind.geometry.PointCloud, arg0: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.geometry.PointCloud
 |
 |  __copy__(...)
 |      __copy__(self: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.geometry.PointCloud
 |
 |  __deepcopy__(...)
 |      __deepcopy__(self: open3d.cuda.pybind.geometry.PointCloud, arg0: dict) -> open3d.cuda.pybind.geometry.PointCloud
 |
 |  __iadd__(...)
 |      __iadd__(self: open3d.cuda.pybind.geometry.PointCloud, arg0: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.geometry.PointCloud
 |
 |  __init__(...)
 |      __init__(*args, **kwargs)
 |      Overloaded function.
 |
 |      1. __init__(self: open3d.cuda.pybind.geometry.PointCloud) -> None
 |
 |      Default constructor
 |
 |      2. __init__(self: open3d.cuda.pybind.geometry.PointCloud, arg0: open3d.cuda.pybind.geometry.PointCloud) -> None
 |
 |      Copy constructor
 |
 |      3. __init__(self: open3d.cuda.pybind.geometry.PointCloud, points: open3d.cuda.pybind.utility.Vector3dVector) -> None
 |
 |      Create a PointCloud from points
 |
 |  __repr__(...)
 |      __repr__(self: open3d.cuda.pybind.geometry.PointCloud) -> str
 |
 |  cluster_dbscan(...)
 |      cluster_dbscan(self: open3d.cuda.pybind.geometry.PointCloud, eps: float, min_points: int, print_progress: bool = False) -> open3d.cuda.pybind.utility.IntVector
 |      Cluster PointCloud using the DBSCAN algorithm  Ester et al., 'A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise', 1996. Returns a list of point labels, -1 indicates noise according to the algorithm.
 |
 |      Args:
 |          eps (float): Density parameter that is used to find neighbouring points.
 |          min_points (int): Minimum number of points to form a cluster.
 |          print_progress (bool, optional, default=False): If true the progress is visualized in the console.
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.IntVector
 |
 |  compute_convex_hull(...)
 |      compute_convex_hull(self: open3d.cuda.pybind.geometry.PointCloud, joggle_inputs: bool = False) -> tuple[open3d.cuda.pybind.geometry.TriangleMesh, list[int]]
 |
 |
 |      Computes the convex hull of the point cloud.
 |
 |      Args:
 |           joggle_inputs (bool): If True allows the algorithm to add random noise to
 |                the points to work around degenerate inputs. This adds the 'QJ'
 |                option to the qhull command.
 |
 |      Returns:
 |           tuple(open3d.geometry.TriangleMesh, list): The triangle mesh of the convex
 |           hull and the list of point indices that are part of the convex hull.
 |
 |  compute_mahalanobis_distance(...)
 |      compute_mahalanobis_distance(self: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.utility.DoubleVector
 |      Function to compute the Mahalanobis distance for points in a point cloud. See: https://en.wikipedia.org/wiki/Mahalanobis_distance.
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.DoubleVector
 |
 |  compute_mean_and_covariance(...)
 |      compute_mean_and_covariance(self: open3d.cuda.pybind.geometry.PointCloud) -> tuple[numpy.ndarray[numpy.float64[3, 1]], numpy.ndarray[numpy.float64[3, 3]]]
 |      Function to compute the mean and covariance matrix of a point cloud.
 |
 |      Returns:
 |          tuple[numpy.ndarray[numpy.float64[3, 1]], numpy.ndarray[numpy.float64[3, 3]]]
 |
 |  compute_nearest_neighbor_distance(...)
 |      compute_nearest_neighbor_distance(self: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.utility.DoubleVector
 |      Function to compute the distance from a point to its nearest neighbor in the point cloud
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.DoubleVector
 |
 |  compute_point_cloud_distance(...)
 |      compute_point_cloud_distance(self: open3d.cuda.pybind.geometry.PointCloud, target: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.utility.DoubleVector
 |      For each point in the source point cloud, compute the distance to the target point cloud.
 |
 |      Args:
 |          target (open3d.cuda.pybind.geometry.PointCloud): The target point cloud.
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.DoubleVector
 |
 |  crop(...)
 |      crop(*args, **kwargs)
 |      Overloaded function.
 |
 |
 |      1. crop(self: open3d.cuda.pybind.geometry.PointCloud, bounding_box: open3d.cuda.pybind.geometry.AxisAlignedBoundingBox, invert: bool = False) -> open3d.cuda.pybind.geometry.PointCloud
 |          Function to crop input pointcloud into output pointcloud
 |
 |      Args:
 |          bounding_box (open3d.cuda.pybind.geometry.AxisAlignedBoundingBox): AxisAlignedBoundingBox to crop points
 |          invert (bool, optional, default=False): optional boolean to invert cropping
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |      2. crop(self: open3d.cuda.pybind.geometry.PointCloud, bounding_box: open3d.cuda.pybind.geometry.OrientedBoundingBox, invert: bool = False) -> open3d.cuda.pybind.geometry.PointCloud
 |          Function to crop input pointcloud into output pointcloud
 |
 |      Args:
 |          bounding_box (open3d.cuda.pybind.geometry.OrientedBoundingBox): AxisAlignedBoundingBox to crop points
 |          invert (bool, optional, default=False): optional boolean to invert cropping
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  detect_planar_patches(...)
 |      detect_planar_patches(self: open3d.cuda.pybind.geometry.PointCloud, normal_variance_threshold_deg: float = 60, coplanarity_deg: float = 75, outlier_ratio: float = 0.75, min_plane_edge_length: float = 0.0, min_num_points: int = 0, search_param: open3d.cuda.pybind.geometry.KDTreeSearchParam = KDTreeSearchParamKNN(knn=30)) -> list[open3d.cuda.pybind.geometry.OrientedBoundingBox]
 |      Detects planar patches in the point cloud using a robust statistics-based approach.
 |
 |      Returns:
 |           A list of detected planar patches, represented as
 |           OrientedBoundingBox objects, with the third column (z) of R indicating
 |           the planar patch normal vector. The extent in the z direction is
 |           non-zero so that the OrientedBoundingBox contains the points that
 |           contribute to the plane detection.
 |
 |      Args:
 |          normal_variance_threshold_deg (float, optional, default=60)
 |          coplanarity_deg (float, optional, default=75)
 |          outlier_ratio (float, optional, default=0.75): Maximum allowable ratio of outliers associated to a plane.
 |          min_plane_edge_length (float, optional, default=0.0): Minimum edge length of plane's long edge before being rejected.
 |          min_num_points (int, optional, default=0): Minimum number of points allowable for fitting planes.
 |          search_param (open3d.cuda.pybind.geometry.KDTreeSearchParam, optional, default=KDTreeSearchParamKNN(knn=30)): The KDTree search parameters for neighborhood search.
 |
 |      Returns:
 |          list[open3d.cuda.pybind.geometry.OrientedBoundingBox]
 |
 |  estimate_covariances(...)
 |      estimate_covariances(self: open3d.cuda.pybind.geometry.PointCloud, search_param: open3d.cuda.pybind.geometry.KDTreeSearchParam = KDTreeSearchParamKNN(knn=30)) -> None
 |      Function to compute the covariance matrix for each point in the point cloud
 |
 |      Args:
 |          search_param (open3d.cuda.pybind.geometry.KDTreeSearchParam, optional, default=KDTreeSearchParamKNN(knn=30)): The KDTree search parameters for neighborhood search.
 |
 |      Returns:
 |          None
 |
 |  estimate_normals(...)
 |      estimate_normals(self: open3d.cuda.pybind.geometry.PointCloud, search_param: open3d.cuda.pybind.geometry.KDTreeSearchParam = KDTreeSearchParamKNN(knn=30), fast_normal_computation: bool = True) -> None
 |      Function to compute the normals of a point cloud. Normals are oriented with respect to the input point cloud if normals exist
 |
 |      Args:
 |          search_param (open3d.cuda.pybind.geometry.KDTreeSearchParam, optional, default=KDTreeSearchParamKNN(knn=30)): The KDTree search parameters for neighborhood search.
 |          fast_normal_computation (bool, optional, default=True): If true, the normal estimation uses a non-iterative method to extract the eigenvector from the covariance matrix. This is faster, but is not as numerical stable.
 |
 |      Returns:
 |          None
 |
 |  farthest_point_down_sample(...)
 |      farthest_point_down_sample(self: open3d.cuda.pybind.geometry.PointCloud, num_samples: int, start_index: int = 0) -> open3d.cuda.pybind.geometry.PointCloud
 |
 |      Index to start downsampling from. Valid index is a non-negative number less than number of points in the input pointcloud.
 |
 |  has_colors(...)
 |      has_colors(self: open3d.cuda.pybind.geometry.PointCloud) -> bool
 |      Returns ``True`` if the point cloud contains point colors.
 |
 |      Returns:
 |          bool
 |
 |  has_covariances(...)
 |      has_covariances(self: open3d.cuda.pybind.geometry.PointCloud) -> bool
 |
 |      Returns ``True`` if the point cloud contains covariances.
 |
 |  has_normals(...)
 |      has_normals(self: open3d.cuda.pybind.geometry.PointCloud) -> bool
 |      Returns ``True`` if the point cloud contains point normals.
 |
 |      Returns:
 |          bool
 |
 |  has_points(...)
 |      has_points(self: open3d.cuda.pybind.geometry.PointCloud) -> bool
 |      Returns ``True`` if the point cloud contains points.
 |
 |      Returns:
 |          bool
 |
 |  hidden_point_removal(...)
 |      hidden_point_removal(self: open3d.cuda.pybind.geometry.PointCloud, camera_location: numpy.ndarray[numpy.float64[3, 1]], radius: float) -> tuple[open3d.cuda.pybind.geometry.TriangleMesh, list[int]]
 |      Removes hidden points from a point cloud and returns a mesh of the remaining points. Based on Katz et al. 'Direct Visibility of Point Sets', 2007. Additional information about the choice of radius for noisy point clouds can be found in Mehra et. al. 'Visibility of Noisy Point Cloud Data', 2010.
 |
 |      Args:
 |          camera_location (numpy.ndarray[numpy.float64[3, 1]]): All points not visible from that location will be removed
 |          radius (float): The radius of the sperical projection
 |
 |      Returns:
 |          tuple[open3d.cuda.pybind.geometry.TriangleMesh, list[int]]
 |
 |  normalize_normals(...)
 |      normalize_normals(self: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.geometry.PointCloud
 |      Normalize point normals to length 1.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  orient_normals_consistent_tangent_plane(...)
 |      orient_normals_consistent_tangent_plane(self: open3d.cuda.pybind.geometry.PointCloud, k: int, lambda_penalty: float = 0.0, cos_alpha_tol: float = 1.0) -> None
 |      Function to orient the normals with respect to consistent tangent planes
 |
 |      Args:
 |          k (int): Number of k nearest neighbors used in constructing the Riemannian graph used to propagate normal orientation.
 |          lambda_penalty (float, optional, default=0.0)
 |          cos_alpha_tol (float, optional, default=1.0)
 |
 |      Returns:
 |          None
 |
 |  orient_normals_to_align_with_direction(...)
 |      orient_normals_to_align_with_direction(self: open3d.cuda.pybind.geometry.PointCloud, orientation_reference: numpy.ndarray[numpy.float64[3, 1]] = array([0., 0., 1.])) -> None
 |      Function to orient the normals of a point cloud
 |
 |      Args:
 |          orientation_reference (numpy.ndarray[numpy.float64[3, 1]], optional, default=array([0., 0., 1.])): Normals are oriented with respect to orientation_reference.
 |
 |      Returns:
 |          None
 |
 |  orient_normals_towards_camera_location(...)
 |      orient_normals_towards_camera_location(self: open3d.cuda.pybind.geometry.PointCloud, camera_location: numpy.ndarray[numpy.float64[3, 1]] = array([0., 0., 0.])) -> None
 |      Function to orient the normals of a point cloud
 |
 |      Args:
 |          camera_location (numpy.ndarray[numpy.float64[3, 1]], optional, default=array([0., 0., 0.])): Normals are oriented with towards the camera_location.
 |
 |      Returns:
 |          None
 |
 |  paint_uniform_color(...)
 |      paint_uniform_color(self: open3d.cuda.pybind.geometry.PointCloud, color: numpy.ndarray[numpy.float64[3, 1]]) -> open3d.cuda.pybind.geometry.PointCloud
 |      Assigns each point in the PointCloud the same color.
 |
 |      Args:
 |          color (numpy.ndarray[numpy.float64[3, 1]]): RGB color for the PointCloud.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  random_down_sample(...)
 |      random_down_sample(self: open3d.cuda.pybind.geometry.PointCloud, sampling_ratio: float) -> open3d.cuda.pybind.geometry.PointCloud
 |      Function to downsample input pointcloud into output pointcloud randomly. The sample is generated by randomly sampling the indexes from the point cloud.
 |
 |      Args:
 |          sampling_ratio (float): Sampling ratio, the ratio of number of selected points to total number of points[0-1]
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  remove_duplicated_points(...)
 |      remove_duplicated_points(self: open3d.cuda.pybind.geometry.PointCloud) -> open3d.cuda.pybind.geometry.PointCloud
 |      Removes duplicated points, i.e., points that have identical coordinates. It also removes the corresponding attributes associated with the non-finite point such as normals, covariances and color entries. It doesn't re-computes these attributes after removing duplicated points.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  remove_non_finite_points(...)
 |      remove_non_finite_points(self: open3d.cuda.pybind.geometry.PointCloud, remove_nan: bool = True, remove_infinite: bool = True) -> open3d.cuda.pybind.geometry.PointCloud
 |      Removes all points from the point cloud that have a nan entry, or infinite entries. It also removes the corresponding attributes associated with the non-finite point such as normals, covariances and color entries. It doesn't re-computes these attributes after removing non-finite points.
 |
 |      Args:
 |          remove_nan (bool, optional, default=True): Remove NaN values from the PointCloud
 |          remove_infinite (bool, optional, default=True): Remove infinite values from the PointCloud
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  remove_radius_outlier(...)
 |      remove_radius_outlier(self: open3d.cuda.pybind.geometry.PointCloud, nb_points: int, radius: float, print_progress: bool = False) -> tuple[open3d.cuda.pybind.geometry.PointCloud, list[int]]
 |      Removes points that have neighbors less than nb_points in a sphere of a given radius
 |
 |      Args:
 |          nb_points (int): Number of points within the radius.
 |          radius (float): Radius of the sphere.
 |          print_progress (bool, optional, default=False): Set to True to print progress bar.
 |
 |      Returns:
 |          tuple[open3d.cuda.pybind.geometry.PointCloud, list[int]]
 |
 |  remove_statistical_outlier(...)
 |      remove_statistical_outlier(self: open3d.cuda.pybind.geometry.PointCloud, nb_neighbors: int, std_ratio: float, print_progress: bool = False) -> tuple[open3d.cuda.pybind.geometry.PointCloud, list[int]]
 |      Removes points that are further away from their neighbors in average.
 |
 |      Args:
 |          nb_neighbors (int): Number of neighbors around the target point.
 |          std_ratio (float): Standard deviation ratio.
 |          print_progress (bool, optional, default=False): Set to True to print progress bar.
 |
 |      Returns:
 |          tuple[open3d.cuda.pybind.geometry.PointCloud, list[int]]
 |
 |  segment_plane(...)
 |      segment_plane(self: open3d.cuda.pybind.geometry.PointCloud, distance_threshold: float, ransac_n: int, num_iterations: int, probability: float = 0.99999999) -> tuple[numpy.ndarray[numpy.float64[4, 1]], list[int]]
 |      Segments a plane in the point cloud using the RANSAC algorithm.
 |
 |      Args:
 |          distance_threshold (float): Max distance a point can be from the plane model, and still be considered an inlier.
 |          ransac_n (int): Number of initial points to be considered inliers in each iteration.
 |          num_iterations (int): Number of iterations.
 |          probability (float, optional, default=0.99999999): Expected probability of finding the optimal plane.
 |
 |      Returns:
 |          tuple[numpy.ndarray[numpy.float64[4, 1]], list[int]]
 |
 |  select_by_index(...)
 |      select_by_index(self: open3d.cuda.pybind.geometry.PointCloud, indices: list[int], invert: bool = False) -> open3d.cuda.pybind.geometry.PointCloud
 |      Function to select points from input pointcloud into output pointcloud.
 |
 |      Args:
 |          indices (list[int]): Indices of points to be selected.
 |          invert (bool, optional, default=False): Set to ``True`` to invert the selection of indices.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  uniform_down_sample(...)
 |      uniform_down_sample(self: open3d.cuda.pybind.geometry.PointCloud, every_k_points: int) -> open3d.cuda.pybind.geometry.PointCloud
 |      Function to downsample input pointcloud into output pointcloud uniformly. The sample is performed in the order of the points with the 0-th point always chosen, not at random.
 |
 |      Args:
 |          every_k_points (int): Sample rate, the selected point indices are [0, k, 2k, ...]
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  voxel_down_sample(...)
 |      voxel_down_sample(self: open3d.cuda.pybind.geometry.PointCloud, voxel_size: float) -> open3d.cuda.pybind.geometry.PointCloud
 |      Function to downsample input pointcloud into output pointcloud with a voxel. Normals and colors are averaged if they exist.
 |
 |      Args:
 |          voxel_size (float): Voxel size to downsample into.
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  voxel_down_sample_and_trace(...)
 |      voxel_down_sample_and_trace(self: open3d.cuda.pybind.geometry.PointCloud, voxel_size: float, min_bound: numpy.ndarray[numpy.float64[3, 1]], max_bound: numpy.ndarray[numpy.float64[3, 1]], approximate_class: bool = False) -> tuple[open3d.cuda.pybind.geometry.PointCloud, numpy.ndarray[numpy.int32[m, n]], list[open3d.cuda.pybind.utility.IntVector]]
 |      Function to downsample using PointCloud::VoxelDownSample. Also records point cloud index before downsampling
 |
 |      Args:
 |          voxel_size (float): Voxel size to downsample into.
 |          min_bound (numpy.ndarray[numpy.float64[3, 1]]): Minimum coordinate of voxel boundaries
 |          max_bound (numpy.ndarray[numpy.float64[3, 1]]): Maximum coordinate of voxel boundaries
 |          approximate_class (bool, optional, default=False)
 |
 |      Returns:
 |          tuple[open3d.cuda.pybind.geometry.PointCloud, numpy.ndarray[numpy.int32[m, n]], list[open3d.cuda.pybind.utility.IntVector]]
 |
 |  ----------------------------------------------------------------------
 |  Static methods defined here:
 |
 |  create_from_depth_image(...) method of builtins.PyCapsule instance
 |      create_from_depth_image(depth: open3d.cuda.pybind.geometry.Image, intrinsic: open3d.cuda.pybind.camera.PinholeCameraIntrinsic, extrinsic: numpy.ndarray[numpy.float64[4, 4]] = array([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]), depth_scale: float = 1000.0, depth_trunc: float = 1000.0, stride: int = 1, project_valid_depth_only: bool = True) -> open3d.cuda.pybind.geometry.PointCloud
 |      Factory function to create a pointcloud from a depth image and a
 |      camera. Given depth value d at (u, v) image coordinate, the corresponding 3d point is:
 |
 |          - z = d / depth_scale
 |          - x = (u - cx) * z / fx
 |          - y = (v - cy) * z / fy
 |
 |      Args:
 |          depth (open3d.cuda.pybind.geometry.Image): The input depth image can be either a float image, or a uint16_t image.
 |          intrinsic (open3d.cuda.pybind.camera.PinholeCameraIntrinsic): Intrinsic parameters of the camera.
 |          extrinsic (numpy.ndarray[numpy.float64[4, 4]], optional, default=array([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]))
 |          depth_scale (float, optional, default=1000.0): The depth is scaled by 1 / depth_scale.
 |          depth_trunc (float, optional, default=1000.0): Truncated at depth_trunc distance.
 |          stride (int, optional, default=1): Sampling factor to support coarse point cloud extraction.
 |          project_valid_depth_only (bool, optional, default=True)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  create_from_rgbd_image(...) method of builtins.PyCapsule instance
 |      create_from_rgbd_image(image: open3d.cuda.pybind.geometry.RGBDImage, intrinsic: open3d.cuda.pybind.camera.PinholeCameraIntrinsic, extrinsic: numpy.ndarray[numpy.float64[4, 4]] = array([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]), project_valid_depth_only: bool = True) -> open3d.cuda.pybind.geometry.PointCloud
 |      Factory function to create a pointcloud from an RGB-D image and a camera. Given depth value d at (u, v) image coordinate, the corresponding 3d point is:
 |
 |          - z = d / depth_scale
 |          - x = (u - cx) * z / fx
 |          - y = (v - cy) * z / fy
 |
 |      Args:
 |          image (open3d.cuda.pybind.geometry.RGBDImage): The input image.
 |          intrinsic (open3d.cuda.pybind.camera.PinholeCameraIntrinsic): Intrinsic parameters of the camera.
 |          extrinsic (numpy.ndarray[numpy.float64[4, 4]], optional, default=array([[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]))
 |          project_valid_depth_only (bool, optional, default=True)
 |
 |      Returns:
 |          open3d.cuda.pybind.geometry.PointCloud
 |
 |  estimate_point_covariances(...) method of builtins.PyCapsule instance
 |      estimate_point_covariances(input: open3d.cuda.pybind.geometry.PointCloud, search_param: open3d.cuda.pybind.geometry.KDTreeSearchParam = KDTreeSearchParamKNN(knn=30)) -> open3d.cuda.pybind.utility.Matrix3dVector
 |      Static function to compute the covariance matrix for each point in the given point cloud, doesn't change the input
 |
 |      Args:
 |          input (open3d.cuda.pybind.geometry.PointCloud): The input point cloud.
 |          search_param (open3d.cuda.pybind.geometry.KDTreeSearchParam, optional, default=KDTreeSearchParamKNN(knn=30)): The KDTree search parameters for neighborhood search.
 |
 |      Returns:
 |          open3d.cuda.pybind.utility.Matrix3dVector
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors defined here:
 |
 |  colors
 |      ``float64`` array of shape ``(num_points, 3)``, range ``[0, 1]`` , use ``numpy.asarray()`` to access data: RGB colors of points.
 |
 |  covariances
 |      ``float64`` array of shape ``(num_points, 3, 3)``, use ``numpy.asarray()`` to access data: Points covariances.
 |
 |  normals
 |      ``float64`` array of shape ``(num_points, 3)``, use ``numpy.asarray()`` to access data: Points normals.
 |
 |  points
 |      ``float64`` array of shape ``(num_points, 3)``, use ``numpy.asarray()`` to access data: Points coordinates.
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

