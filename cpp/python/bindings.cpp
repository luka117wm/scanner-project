#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/eigen.h>

#include "scanner/point_cloud.h"
#include "scanner/triangle_mesh.h"
#include "scanner/mesh_repair.h"
#include "scanner/print_preparation.h"

namespace py = pybind11;
using namespace scanner;
using namespace pybind11::literals;

// ── numpy-конвертации ─────────────────────────────────────────────────────────

static py::array_t<double> vd_to_np(const std::vector<Vector3d>& v) {
    py::array_t<double> a({(py::ssize_t)v.size(), (py::ssize_t)3});
    auto b = a.mutable_unchecked<2>();
    for (py::ssize_t i = 0; i < (py::ssize_t)v.size(); ++i) {
        b(i,0) = v[i].x(); b(i,1) = v[i].y(); b(i,2) = v[i].z();
    }
    return a;
}

static std::vector<Vector3d> vd_from_np(
    py::array_t<double, py::array::c_style | py::array::forcecast> a)
{
    auto r = a.unchecked<2>();
    std::vector<Vector3d> out(r.shape(0));
    for (py::ssize_t i = 0; i < r.shape(0); ++i)
        out[i] = {r(i,0), r(i,1), r(i,2)};
    return out;
}

static py::array_t<int32_t> vi_to_np(const std::vector<Vector3i>& v) {
    py::array_t<int32_t> a({(py::ssize_t)v.size(), (py::ssize_t)3});
    auto b = a.mutable_unchecked<2>();
    for (py::ssize_t i = 0; i < (py::ssize_t)v.size(); ++i) {
        b(i,0) = v[i].x(); b(i,1) = v[i].y(); b(i,2) = v[i].z();
    }
    return a;
}

static std::vector<Vector3i> vi_from_np(
    py::array_t<int32_t, py::array::c_style | py::array::forcecast> a)
{
    auto r = a.unchecked<2>();
    std::vector<Vector3i> out(r.shape(0));
    for (py::ssize_t i = 0; i < r.shape(0); ++i)
        out[i] = {r(i,0), r(i,1), r(i,2)};
    return out;
}

static py::array_t<uint8_t> vc_to_np(const std::vector<Color>& v) {
    py::array_t<uint8_t> a({(py::ssize_t)v.size(), (py::ssize_t)3});
    auto b = a.mutable_unchecked<2>();
    for (py::ssize_t i = 0; i < (py::ssize_t)v.size(); ++i) {
        b(i,0) = v[i].r; b(i,1) = v[i].g; b(i,2) = v[i].b;
    }
    return a;
}

static std::vector<Color> vc_from_np(
    py::array_t<uint8_t, py::array::c_style | py::array::forcecast> a)
{
    auto r = a.unchecked<2>();
    std::vector<Color> out(r.shape(0));
    for (py::ssize_t i = 0; i < r.shape(0); ++i)
        out[i] = {r(i,0), r(i,1), r(i,2)};
    return out;
}

// ── Модуль ───────────────────────────────────────────────────────────────────

PYBIND11_MODULE(_scanner_cpp, m) {
    m.doc() = "C++ ядро scanner: PointCloud, TriangleMesh, MeshRepair, PrintPreparation";

    // ── BoundingBox ───────────────────────────────────────────────────────────
    py::class_<BoundingBox>(m, "BoundingBox")
        .def(py::init<>())
        .def_property("min",
            [](const BoundingBox& b) { return b.min; },
            [](BoundingBox& b, const Vector3d& v) { b.min = v; })
        .def_property("max",
            [](const BoundingBox& b) { return b.max; },
            [](BoundingBox& b, const Vector3d& v) { b.max = v; })
        .def("size",   &BoundingBox::size)
        .def("center", &BoundingBox::center)
        .def("valid",  &BoundingBox::valid)
        .def("__repr__", [](const BoundingBox& b) {
            return "<BoundingBox min=(" +
                   std::to_string(b.min.x()) + "," + std::to_string(b.min.y()) + "," + std::to_string(b.min.z()) +
                   ") max=(" +
                   std::to_string(b.max.x()) + "," + std::to_string(b.max.y()) + "," + std::to_string(b.max.z()) + ")>";
        });

    // ── PointCloud ────────────────────────────────────────────────────────────
    py::class_<PointCloud>(m, "PointCloud")
        .def(py::init<>())

        // numpy-свойства для основных полей
        .def_property("points",
            [](const PointCloud& pc) { return vd_to_np(pc.points_); },
            [](PointCloud& pc, py::array_t<double, py::array::c_style | py::array::forcecast> a) {
                pc.points_ = vd_from_np(a);
            })
        .def_property("normals",
            [](const PointCloud& pc) { return vd_to_np(pc.normals_); },
            [](PointCloud& pc, py::array_t<double, py::array::c_style | py::array::forcecast> a) {
                pc.normals_ = vd_from_np(a);
            })
        .def_property("colors",
            [](const PointCloud& pc) { return vc_to_np(pc.colors_); },
            [](PointCloud& pc, py::array_t<uint8_t, py::array::c_style | py::array::forcecast> a) {
                pc.colors_ = vc_from_np(a);
            })

        // I/O
        .def("load_ply", [](PointCloud& pc, const std::string& path) {
            return pc.load_ply(path);
        }, "path"_a)
        .def("save_ply", [](const PointCloud& pc, const std::string& path) {
            return pc.save_ply(path);
        }, "path"_a)

        // геометрия
        .def("__len__",          &PointCloud::size)
        .def("size",             &PointCloud::size)
        .def("empty",            &PointCloud::empty)
        .def("bounding_box",     &PointCloud::bounding_box)
        .def("center_to_origin", &PointCloud::center_to_origin)

        // обработка — все возвращают новый PointCloud (move)
        .def("statistical_outlier_removal",
            &PointCloud::statistical_outlier_removal,
            "k"_a = 20, "std_ratio"_a = 2.0,
            py::return_value_policy::move)
        .def("voxel_downsample",
            &PointCloud::voxel_downsample,
            "voxel_size"_a,
            py::return_value_policy::move)
        .def("estimate_normals", &PointCloud::estimate_normals, "k"_a = 30)
        .def("segment_largest_cluster",
            &PointCloud::segment_largest_cluster,
            "eps"_a = 0.02, "min_points"_a = 50,
            "min_cluster_fraction"_a = 0.05,
            py::return_value_policy::move)

        // KD-tree
        .def("build_kdtree", &PointCloud::build_kdtree)
        .def("k_nearest", [](const PointCloud& pc, const Vector3d& q, std::size_t k) {
            return pc.k_nearest(q, k);
        }, "query"_a, "k"_a)
        .def("radius_search", [](const PointCloud& pc, const Vector3d& q, double r) {
            return pc.radius_search(q, r);
        }, "query"_a, "radius"_a)

        .def("__repr__", [](const PointCloud& pc) {
            return "<PointCloud points=" + std::to_string(pc.size()) + ">";
        });

    // ── TriangleMesh ──────────────────────────────────────────────────────────
    py::class_<TriangleMesh>(m, "TriangleMesh")
        .def(py::init<>())

        // numpy-свойства
        .def_property("vertices",
            [](const TriangleMesh& m) { return vd_to_np(m.vertices_); },
            [](TriangleMesh& m, py::array_t<double, py::array::c_style | py::array::forcecast> a) {
                m.vertices_ = vd_from_np(a);
            })
        .def_property("faces",
            [](const TriangleMesh& m) { return vi_to_np(m.faces_); },
            [](TriangleMesh& m, py::array_t<int32_t, py::array::c_style | py::array::forcecast> a) {
                m.faces_ = vi_from_np(a);
            })
        .def_property("normals",
            [](const TriangleMesh& m) { return vd_to_np(m.normals_); },
            [](TriangleMesh& m, py::array_t<double, py::array::c_style | py::array::forcecast> a) {
                m.normals_ = vd_from_np(a);
            })
        .def_property("colors",
            [](const TriangleMesh& m) { return vc_to_np(m.colors_); },
            [](TriangleMesh& m, py::array_t<uint8_t, py::array::c_style | py::array::forcecast> a) {
                m.colors_ = vc_from_np(a);
            })

        // I/O
        .def("load_ply", [](TriangleMesh& m, const std::string& p) { return m.load_ply(p); }, "path"_a)
        .def("load_stl", [](TriangleMesh& m, const std::string& p) { return m.load_stl(p); }, "path"_a)
        .def("save_ply", [](const TriangleMesh& m, const std::string& p) { return m.save_ply(p); }, "path"_a)
        .def("save_stl", [](const TriangleMesh& m, const std::string& p) { return m.save_stl(p); }, "path"_a)
        .def("save_obj", [](const TriangleMesh& m, const std::string& p) { return m.save_obj(p); }, "path"_a)

        // свойства
        .def("num_vertices",  &TriangleMesh::num_vertices)
        .def("num_faces",     &TriangleMesh::num_faces)
        .def("empty",         &TriangleMesh::empty)
        .def("bounding_box",  &TriangleMesh::bounding_box)

        // геометрия
        .def("compute_normals", &TriangleMesh::compute_normals)
        .def("surface_area",    &TriangleMesh::surface_area)
        .def("volume",          &TriangleMesh::volume)

        // топология
        .def("is_watertight",       &TriangleMesh::is_watertight)
        .def("find_boundary_edges", &TriangleMesh::find_boundary_edges)
        .def("get_vertex_neighbors",&TriangleMesh::get_vertex_neighbors, "v"_a)
        .def("build_edge_map", [](const TriangleMesh& mesh) {
            // EdgeMap: std::map<pair<int,int>, vector<int>> → dict[(int,int): list[int]]
            py::dict d;
            for (const auto& [k, v] : mesh.build_edge_map())
                d[py::make_tuple(k.first, k.second)] = v;
            return d;
        })

        .def("__repr__", [](const TriangleMesh& m) {
            return "<TriangleMesh vertices=" + std::to_string(m.num_vertices()) +
                   " faces=" + std::to_string(m.num_faces()) + ">";
        });

    // ── RepairReport ──────────────────────────────────────────────────────────
    py::class_<RepairReport>(m, "RepairReport")
        .def(py::init<>())
        .def_readwrite("degenerate_removed",   &RepairReport::degenerate_removed)
        .def_readwrite("duplicate_removed",    &RepairReport::duplicate_removed)
        .def_readwrite("vertices_merged",      &RepairReport::vertices_merged)
        .def_readwrite("non_manifold_removed", &RepairReport::non_manifold_removed)
        .def_readwrite("holes_filled",         &RepairReport::holes_filled)
        .def_readwrite("smooth_iterations",    &RepairReport::smooth_iterations)
        .def("any_repair", &RepairReport::any_repair)
        .def("__repr__", [](const RepairReport& r) {
            return "<RepairReport degen=" + std::to_string(r.degenerate_removed) +
                   " dup=" + std::to_string(r.duplicate_removed) +
                   " merged=" + std::to_string(r.vertices_merged) +
                   " holes=" + std::to_string(r.holes_filled) + ">";
        });

    // ── MeshRepair ────────────────────────────────────────────────────────────
    // keep_alive<1,2>: MeshRepair (arg 1) держит ссылку на mesh (arg 2) живой
    py::class_<MeshRepair>(m, "MeshRepair")
        .def(py::init<TriangleMesh&>(), "mesh"_a, py::keep_alive<1, 2>())
        .def("remove_degenerate_faces", &MeshRepair::remove_degenerate_faces)
        .def("remove_duplicate_faces",  &MeshRepair::remove_duplicate_faces)
        .def("merge_close_vertices",    &MeshRepair::merge_close_vertices,
             "threshold"_a = 1e-6)
        .def("make_manifold",           &MeshRepair::make_manifold)
        .def("fill_holes",              &MeshRepair::fill_holes,
             "max_hole_edges"_a = 100)
        .def("laplacian_smooth",        &MeshRepair::laplacian_smooth,
             "iterations"_a = 3, "lambda_"_a = 0.5)
        .def("repair_all",              &MeshRepair::repair_all,
             "smooth_iterations"_a = 3, "max_hole_edges"_a = 100);

    // ── PrintabilityReport ────────────────────────────────────────────────────
    py::class_<PrintabilityReport>(m, "PrintabilityReport")
        .def(py::init<>())
        .def_readwrite("is_watertight",    &PrintabilityReport::is_watertight)
        .def_readwrite("has_thin_walls",   &PrintabilityReport::has_thin_walls)
        .def_readwrite("has_overhangs",    &PrintabilityReport::has_overhangs)
        .def_readwrite("volume_mm3",       &PrintabilityReport::volume_mm3)
        .def_readwrite("surface_area_mm2", &PrintabilityReport::surface_area_mm2)
        .def_readwrite("bbox_x_mm",        &PrintabilityReport::bbox_x_mm)
        .def_readwrite("bbox_y_mm",        &PrintabilityReport::bbox_y_mm)
        .def_readwrite("bbox_z_mm",        &PrintabilityReport::bbox_z_mm)
        .def_readwrite("open_edges",       &PrintabilityReport::open_edges)
        .def_readwrite("warnings",         &PrintabilityReport::warnings)
        .def("is_printable", &PrintabilityReport::is_printable)
        .def("__repr__", [](const PrintabilityReport& r) {
            return "<PrintabilityReport watertight=" + std::string(r.is_watertight ? "True" : "False") +
                   " vol=" + std::to_string(r.volume_mm3) + "mm3" +
                   " printable=" + std::string(r.is_printable() ? "True" : "False") + ">";
        });

    // ── PrintPreparation ──────────────────────────────────────────────────────
    py::class_<PrintPreparation>(m, "PrintPreparation")
        .def(py::init<TriangleMesh&>(), "mesh"_a, py::keep_alive<1, 2>())
        .def("cut_with_plane", [](PrintPreparation& pp,
                                   const Vector3d& point,
                                   const Vector3d& normal) {
            pp.cut_with_plane(point, normal);
        }, "point"_a, "normal"_a)
        .def("add_flat_base",  &PrintPreparation::add_flat_base, "thickness"_a = 2.0)
        .def("scale_to_size",  [](PrintPreparation& pp, double target_mm, const std::string& axis) {
            if (axis.empty()) throw py::value_error("axis must be 'x', 'y', or 'z'");
            pp.scale_to_size(target_mm, axis[0]);
        }, "target_mm"_a, "axis"_a = "z")
        .def("auto_orient",        &PrintPreparation::auto_orient)
        .def("add_disc_stand",     &PrintPreparation::add_disc_stand,
             "radius_fraction"_a = 0.9, "thickness"_a = 2.0)
        .def("check_printability", &PrintPreparation::check_printability);
}
