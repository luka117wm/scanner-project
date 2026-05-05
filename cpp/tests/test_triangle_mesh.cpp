// Тест: TriangleMesh — куб → save_stl → load_stl → watertight, volume ≈ 1.0
#include "scanner/triangle_mesh.h"

#include <cassert>
#include <cmath>
#include <filesystem>
#include <iostream>

using namespace scanner;
namespace fs = std::filesystem;

static void check(bool cond, const char* msg) {
    if (!cond) { std::cerr << "FAIL: " << msg << "\n"; std::exit(1); }
}
static bool nearly(double a, double b, double tol = 1e-4) {
    return std::abs(a - b) < tol;
}

// Единичный куб [0,1]^3 — 8 вершин, 12 граней, ориентация наружу
static TriangleMesh make_unit_cube() {
    TriangleMesh m;
    m.vertices_ = {
        {0,0,0}, {1,0,0}, {1,1,0}, {0,1,0},
        {0,0,1}, {1,0,1}, {1,1,1}, {0,1,1}
    };
    m.faces_ = {
        // Дно (-Z): нормаль (0,0,-1)
        {0,2,1}, {0,3,2},
        // Крыша (+Z): нормаль (0,0,+1)
        {4,5,6}, {4,6,7},
        // Перед (-Y): нормаль (0,-1,0)
        {0,1,5}, {0,5,4},
        // Зад (+Y): нормаль (0,+1,0)
        {2,3,7}, {2,7,6},
        // Лево (-X): нормаль (-1,0,0)
        {0,4,7}, {0,7,3},
        // Право (+X): нормаль (+1,0,0)
        {1,2,6}, {1,6,5}
    };
    return m;
}

int main() {
    auto tmp = fs::temp_directory_path();

    // ── 1. Базовые размеры ───────────────────────────────────────────
    auto cube = make_unit_cube();
    check(cube.num_vertices() == 8,  "num_vertices == 8");
    check(cube.num_faces()    == 12, "num_faces == 12");
    check(!cube.empty(),             "not empty");

    // ── 2. BBox ──────────────────────────────────────────────────────
    BoundingBox bb = cube.bounding_box();
    check(bb.valid(), "bbox valid");
    check(nearly(bb.min.x(), 0.0) && nearly(bb.max.x(), 1.0), "bbox X [0,1]");
    check(nearly(bb.min.y(), 0.0) && nearly(bb.max.y(), 1.0), "bbox Y [0,1]");
    check(nearly(bb.min.z(), 0.0) && nearly(bb.max.z(), 1.0), "bbox Z [0,1]");

    // ── 3. Нормали ───────────────────────────────────────────────────
    cube.compute_normals();
    check(cube.normals_.size() == 12, "normals_.size() == 12");
    // Нормали — единичные
    for (const auto& n : cube.normals_)
        check(nearly(n.norm(), 1.0, 1e-6), "normal is unit");

    // ── 4. Площадь поверхности = 6.0 ────────────────────────────────
    double sa = cube.surface_area();
    check(nearly(sa, 6.0, 1e-5), "surface_area == 6.0");
    std::cout << "  surface_area = " << sa << "\n";

    // ── 5. Объём = 1.0 ───────────────────────────────────────────────
    double vol = cube.volume();
    check(nearly(vol, 1.0, 1e-5), "volume == 1.0");
    std::cout << "  volume = " << vol << "\n";

    // ── 6. Watertight ────────────────────────────────────────────────
    check(cube.is_watertight(), "cube is watertight");
    auto boundary = cube.find_boundary_edges();
    check(boundary.empty(), "no boundary edges on watertight cube");

    // ── 7. Edge map ──────────────────────────────────────────────────
    auto em = cube.build_edge_map();
    // Куб: 12 рёбер (AABB) + 6 диагоналей = 18 рёбер. Каждое в ровно 2 гранях.
    check(em.size() == 18, "cube has 18 unique edges");
    for (const auto& [e, fi] : em)
        check(fi.size() == 2, "every edge in exactly 2 faces");

    // ── 8. Соседи вершины 0 ──────────────────────────────────────────
    auto nbrs = cube.get_vertex_neighbors(0);
    // v0 принадлежит 6 граням и имеет 6 соседних вершин
    check(nbrs.size() == 6, "vertex 0 has 6 neighbors");
    std::cout << "  neighbors(0): ";
    for (int n : nbrs) std::cout << n << " ";
    std::cout << "\n";

    // ── 9. Граница (незамкнутая сетка) ──────────────────────────────
    {
        TriangleMesh open = cube;
        open.faces_.pop_back();   // удалили одну грань
        check(!open.is_watertight(), "mesh with removed face is not watertight");
        auto bd = open.find_boundary_edges();
        check(!bd.empty(), "open mesh has boundary edges");
        std::cout << "  boundary edges after removing 1 face: " << bd.size() << "\n";
    }

    // ── 10. Round-trip: save_stl → load_stl ──────────────────────────
    {
        auto stl_path = tmp / "scanner_test_cube.stl";
        check(cube.save_stl(stl_path), "save_stl returned true");
        check(fs::exists(stl_path),    "STL file exists");
        // Binary STL: 80 + 4 + 12 × 50 = 684 bytes
        check(fs::file_size(stl_path) == 684, "STL file size == 684 bytes");

        TriangleMesh loaded;
        check(loaded.load_stl(stl_path), "load_stl returned true");
        check(loaded.num_faces() == 12,  "loaded num_faces == 12");
        // После дедупликации вершин должно быть 8
        check(loaded.num_vertices() == 8, "loaded num_vertices == 8 after weld");
        std::cout << "  STL round-trip: "
                  << loaded.num_vertices() << " verts, "
                  << loaded.num_faces()    << " faces\n";

        check(loaded.is_watertight(), "STL-loaded cube is watertight");
        check(nearly(loaded.volume(), 1.0, 1e-4), "STL-loaded volume ≈ 1.0");
        check(nearly(loaded.surface_area(), 6.0, 1e-4), "STL-loaded surface_area ≈ 6.0");
        fs::remove(stl_path);
    }

    // ── 11. Round-trip: save_ply → load_ply ──────────────────────────
    {
        auto ply_path = tmp / "scanner_test_cube.ply";
        check(cube.save_ply(ply_path), "save_ply returned true");
        check(fs::exists(ply_path),    "PLY file exists");

        TriangleMesh loaded;
        check(loaded.load_ply(ply_path), "load_ply returned true");
        check(loaded.num_vertices() == 8,  "PLY-loaded num_vertices == 8");
        check(loaded.num_faces()    == 12, "PLY-loaded num_faces == 12");
        check(loaded.is_watertight(), "PLY-loaded cube is watertight");
        check(nearly(loaded.volume(), 1.0, 1e-4), "PLY-loaded volume ≈ 1.0");
        std::cout << "  PLY round-trip: "
                  << loaded.num_vertices() << " verts, "
                  << loaded.num_faces()    << " faces\n";
        fs::remove(ply_path);
    }

    // ── 12. save_obj ─────────────────────────────────────────────────
    {
        auto obj_path = tmp / "scanner_test_cube.obj";
        check(cube.save_obj(obj_path), "save_obj returned true");
        check(fs::exists(obj_path) && fs::file_size(obj_path) > 0, "OBJ file non-empty");
        std::cout << "  OBJ: " << fs::file_size(obj_path) << " bytes\n";
        fs::remove(obj_path);
    }

    std::cout << "All tests PASSED\n";
    return 0;
}
