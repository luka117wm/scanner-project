COLMAP 3.9.1 -- Structure-from-Motion and Multi-View Stereo
(Commit Unknown on Unknown without CUDA)

Usage:
  colmap [command] [options]

Documentation:
  https://colmap.github.io/

Example usage:
  colmap help [ -h, --help ]
  colmap gui
  colmap gui -h [ --help ]
  colmap automatic_reconstructor -h [ --help ]
  colmap automatic_reconstructor --image_path IMAGES --workspace_path WORKSPACE
  colmap feature_extractor --image_path IMAGES --database_path DATABASE
  colmap exhaustive_matcher --database_path DATABASE
  colmap mapper --image_path IMAGES --database_path DATABASE --output_path MODEL
  ...

Available commands:
  help
  gui
  automatic_reconstructor
  bundle_adjuster
  color_extractor
  database_cleaner
  database_creator
  database_merger
  delaunay_mesher
  exhaustive_matcher
  feature_extractor
  feature_importer
  hierarchical_mapper
  image_deleter
  image_filterer
  image_rectifier
  image_registrator
  image_undistorter
  image_undistorter_standalone
  mapper
  matches_importer
  model_aligner
  model_analyzer
  model_comparer
  model_converter
  model_cropper
  model_merger
  model_orientation_aligner
  model_splitter
  model_transformer
  patch_match_stereo
  point_filtering
  point_triangulator
  poisson_mesher
  project_generator
  rig_bundle_adjuster
  sequential_matcher
  spatial_matcher
  stereo_fusion
  transitive_matcher
  vocab_tree_builder
  vocab_tree_matcher
  vocab_tree_retriever


## feature_extractor

I20260419 05:19:47.236697 42720 option_manager.cc:849] COLMAP 3.9.1 (Commit Unknown on Unknown without CUDA)
I20260419 05:19:47.236902 42720 option_manager.cc:851] Options can either be specified via command-line or by defining them in a .ini project file passed to `--project_path`.
  -h [ --help ] 
  --random_seed arg (=0)
  --log_to_stderr arg (=1)
  --log_level arg (=0)
  --project_path arg
  --database_path arg
  --image_path arg
  --camera_mode arg (=-1)
  --image_list_path arg
  --descriptor_normalization arg (=l1_root)
                                        {'l1_root', 'l2'}
  --ImageReader.mask_path arg
  --ImageReader.camera_model arg (=SIMPLE_RADIAL)
  --ImageReader.single_camera arg (=0)
  --ImageReader.single_camera_per_folder arg (=0)
  --ImageReader.single_camera_per_image arg (=0)
  --ImageReader.existing_camera_id arg (=-1)
  --ImageReader.camera_params arg
  --ImageReader.default_focal_length_factor arg (=1.2)
  --ImageReader.camera_mask_path arg
  --SiftExtraction.num_threads arg (=-1)
  --SiftExtraction.use_gpu arg (=1)
  --SiftExtraction.gpu_index arg (=-1)
  --SiftExtraction.max_image_size arg (=3200)
  --SiftExtraction.max_num_features arg (=8192)
  --SiftExtraction.first_octave arg (=-1)
  --SiftExtraction.num_octaves arg (=4)
  --SiftExtraction.octave_resolution arg (=3)
  --SiftExtraction.peak_threshold arg (=0.0066666666666666671)
  --SiftExtraction.edge_threshold arg (=10)
  --SiftExtraction.estimate_affine_shape arg (=0)
  --SiftExtraction.max_num_orientations arg (=2)
  --SiftExtraction.upright arg (=0)
  --SiftExtraction.domain_size_pooling arg (=0)
  --SiftExtraction.dsp_min_scale arg (=0.16666666666666666)
  --SiftExtraction.dsp_max_scale arg (=3)
  --SiftExtraction.dsp_num_scales arg (=10)

## exhaustive_matcher

I20260419 05:19:47.250905 42721 option_manager.cc:849] COLMAP 3.9.1 (Commit Unknown on Unknown without CUDA)
I20260419 05:19:47.251019 42721 option_manager.cc:851] Options can either be specified via command-line or by defining them in a .ini project file passed to `--project_path`.
  -h [ --help ] 
  --random_seed arg (=0)
  --log_to_stderr arg (=1)
  --log_level arg (=0)
  --project_path arg
  --database_path arg
  --SiftMatching.num_threads arg (=-1)
  --SiftMatching.use_gpu arg (=1)
  --SiftMatching.gpu_index arg (=-1)
  --SiftMatching.max_ratio arg (=0.80000000000000004)
  --SiftMatching.max_distance arg (=0.69999999999999996)
  --SiftMatching.cross_check arg (=1)
  --SiftMatching.guided_matching arg (=0)
  --SiftMatching.max_num_matches arg (=32768)
  --TwoViewGeometry.min_num_inliers arg (=15)
  --TwoViewGeometry.multiple_models arg (=0)
  --TwoViewGeometry.compute_relative_pose arg (=0)
  --TwoViewGeometry.max_error arg (=4)
  --TwoViewGeometry.confidence arg (=0.999)
  --TwoViewGeometry.max_num_trials arg (=10000)
  --TwoViewGeometry.min_inlier_ratio arg (=0.25)
  --ExhaustiveMatching.block_size arg (=50)

## sequential_matcher

I20260419 05:19:47.264528 42722 option_manager.cc:849] COLMAP 3.9.1 (Commit Unknown on Unknown without CUDA)
I20260419 05:19:47.264616 42722 option_manager.cc:851] Options can either be specified via command-line or by defining them in a .ini project file passed to `--project_path`.
  -h [ --help ] 
  --random_seed arg (=0)
  --log_to_stderr arg (=1)
  --log_level arg (=0)
  --project_path arg
  --database_path arg
  --SiftMatching.num_threads arg (=-1)
  --SiftMatching.use_gpu arg (=1)
  --SiftMatching.gpu_index arg (=-1)
  --SiftMatching.max_ratio arg (=0.80000000000000004)
  --SiftMatching.max_distance arg (=0.69999999999999996)
  --SiftMatching.cross_check arg (=1)
  --SiftMatching.guided_matching arg (=0)
  --SiftMatching.max_num_matches arg (=32768)
  --TwoViewGeometry.min_num_inliers arg (=15)
  --TwoViewGeometry.multiple_models arg (=0)
  --TwoViewGeometry.compute_relative_pose arg (=0)
  --TwoViewGeometry.max_error arg (=4)
  --TwoViewGeometry.confidence arg (=0.999)
  --TwoViewGeometry.max_num_trials arg (=10000)
  --TwoViewGeometry.min_inlier_ratio arg (=0.25)
  --SequentialMatching.overlap arg (=10)
  --SequentialMatching.quadratic_overlap arg (=1)
  --SequentialMatching.loop_detection arg (=0)
  --SequentialMatching.loop_detection_period arg (=10)
  --SequentialMatching.loop_detection_num_images arg (=50)
  --SequentialMatching.loop_detection_num_nearest_neighbors arg (=1)
  --SequentialMatching.loop_detection_num_checks arg (=256)
  --SequentialMatching.loop_detection_num_images_after_verification arg (=0)
  --SequentialMatching.loop_detection_max_num_features arg (=-1)
  --SequentialMatching.vocab_tree_path arg

## mapper

I20260419 05:19:47.279907 42723 option_manager.cc:849] COLMAP 3.9.1 (Commit Unknown on Unknown without CUDA)
I20260419 05:19:47.280055 42723 option_manager.cc:851] Options can either be specified via command-line or by defining them in a .ini project file passed to `--project_path`.
  -h [ --help ] 
  --random_seed arg (=0)
  --log_to_stderr arg (=1)
  --log_level arg (=0)
  --project_path arg
  --database_path arg
  --image_path arg
  --input_path arg
  --output_path arg
  --image_list_path arg
  --Mapper.min_num_matches arg (=15)
  --Mapper.ignore_watermarks arg (=0)
  --Mapper.multiple_models arg (=1)
  --Mapper.max_num_models arg (=50)
  --Mapper.max_model_overlap arg (=20)
  --Mapper.min_model_size arg (=10)
  --Mapper.init_image_id1 arg (=-1)
  --Mapper.init_image_id2 arg (=-1)
  --Mapper.init_num_trials arg (=200)
  --Mapper.extract_colors arg (=1)
  --Mapper.num_threads arg (=-1)
  --Mapper.min_focal_length_ratio arg (=0.10000000000000001)
  --Mapper.max_focal_length_ratio arg (=10)
  --Mapper.max_extra_param arg (=1)
  --Mapper.ba_refine_focal_length arg (=1)
  --Mapper.ba_refine_principal_point arg (=0)
  --Mapper.ba_refine_extra_params arg (=1)
  --Mapper.ba_min_num_residuals_for_multi_threading arg (=50000)
  --Mapper.ba_local_num_images arg (=6)
  --Mapper.ba_local_function_tolerance arg (=0)
  --Mapper.ba_local_max_num_iterations arg (=25)
  --Mapper.ba_global_images_ratio arg (=1.1000000000000001)
  --Mapper.ba_global_points_ratio arg (=1.1000000000000001)
  --Mapper.ba_global_images_freq arg (=500)
  --Mapper.ba_global_points_freq arg (=250000)
  --Mapper.ba_global_function_tolerance arg (=0)
  --Mapper.ba_global_max_num_iterations arg (=50)
  --Mapper.ba_global_max_refinements arg (=5)
  --Mapper.ba_global_max_refinement_change arg (=0.00050000000000000001)
  --Mapper.ba_local_max_refinements arg (=2)
  --Mapper.ba_local_max_refinement_change arg (=0.001)
  --Mapper.snapshot_path arg
  --Mapper.snapshot_images_freq arg (=0)
  --Mapper.fix_existing_images arg (=0)
  --Mapper.init_min_num_inliers arg (=100)
  --Mapper.init_max_error arg (=4)
  --Mapper.init_max_forward_motion arg (=0.94999999999999996)
  --Mapper.init_min_tri_angle arg (=16)
  --Mapper.init_max_reg_trials arg (=2)
  --Mapper.abs_pose_max_error arg (=12)
  --Mapper.abs_pose_min_num_inliers arg (=30)
  --Mapper.abs_pose_min_inlier_ratio arg (=0.25)
  --Mapper.filter_max_reproj_error arg (=4)
  --Mapper.filter_min_tri_angle arg (=1.5)
  --Mapper.max_reg_trials arg (=3)
  --Mapper.local_ba_min_tri_angle arg (=6)
  --Mapper.tri_max_transitivity arg (=1)
  --Mapper.tri_create_max_angle_error arg (=2)
  --Mapper.tri_continue_max_angle_error arg (=2)
  --Mapper.tri_merge_max_reproj_error arg (=4)
  --Mapper.tri_complete_max_reproj_error arg (=4)
  --Mapper.tri_complete_max_transitivity arg (=5)
  --Mapper.tri_re_max_angle_error arg (=5)
  --Mapper.tri_re_min_ratio arg (=0.20000000000000001)
  --Mapper.tri_re_max_trials arg (=1)
  --Mapper.tri_min_angle arg (=1.5)
  --Mapper.tri_ignore_two_view_tracks arg (=1)

## patch_match_stereo

E20260419 05:19:47.297819 42724 mvs.cc:80] Dense stereo reconstruction requires CUDA, which is not available on your system.

## stereo_fusion

I20260419 05:19:47.313009 42725 option_manager.cc:849] COLMAP 3.9.1 (Commit Unknown on Unknown without CUDA)
I20260419 05:19:47.313145 42725 option_manager.cc:851] Options can either be specified via command-line or by defining them in a .ini project file passed to `--project_path`.
  -h [ --help ] 
  --random_seed arg (=0)
  --log_to_stderr arg (=1)
  --log_level arg (=0)
  --project_path arg
  --workspace_path arg
  --workspace_format arg (=COLMAP)      {COLMAP, PMVS}
  --pmvs_option_name arg (=option-all)
  --input_type arg (=geometric)         {photometric, geometric}
  --output_type arg (=PLY)              {BIN, TXT, PLY}
  --output_path arg
  --bbox_path arg
  --StereoFusion.mask_path arg
  --StereoFusion.num_threads arg (=-1)
  --StereoFusion.max_image_size arg (=-1)
  --StereoFusion.min_num_pixels arg (=5)
  --StereoFusion.max_num_pixels arg (=10000)
  --StereoFusion.max_traversal_depth arg (=100)
  --StereoFusion.max_reproj_error arg (=2)
  --StereoFusion.max_depth_error arg (=0.0099999997764825821)
  --StereoFusion.max_normal_error arg (=10)
  --StereoFusion.check_num_images arg (=50)
  --StereoFusion.cache_size arg (=32)
  --StereoFusion.use_cache arg (=0)
