// Тест: PrintPreparation — icosphere → cut → base → scale → watertight
#include "scanner/print_preparation.h"
#include "scanner/mesh_repair.h"

#include <cassert>
#include <cmath>
#include <iostream>
#include <numbers>

using namespace scanner;

static void check(bool cond, const char* msg) {
    if (!cond) { std::cerr << "FAIL: " << msg << "\n"; std::exit(1); }
}
static bool nearly(double a, double b, double tol = 1e-3) {
    return std::abs(a - b) < tol;
}

// Единичный икосаэдр: 12 вершин, 20 граней
static TriangleMesh make_icosphere() {
    const double phi = (1.0 + std::sqrt(5.0)) / 2.0;

    TriangleMesh m;
    // 12 вершин — нормализованных
    auto add = [&](double x, double y, double z) {
        Vector3d v(x, y, z);
        m.vertices_.push_back(v.normalized());
    };
    add(-1,  phi,  0);  // 0
    add( 1,  phi,  0);  // 1
    add(-1, -phi,  0);  // 2
    add( 1, -phi,  0);  // 3
    add( 0, -1,  phi);  // 4
    add( 0,  1,  phi);  // 5
    add( 0, -1, -phi);  // 6
    add( 0,  1, -phi);  // 7
    add( phi,  0, -1);  // 8
    add( phi,  0,  1);  // 9
    add(-phi,  0, -1);  // 10
    add(-phi,  0,  1);  // 11

    // 20 граней с правильной ориентацией (нормали наружу)
    m.faces_ = {
        {0,11, 5}, {0, 5, 1}, {0, 1, 7}, {0, 7,10}, {0,10,11},
        {1, 5, 9}, {5,11, 4}, {11,10, 2}, {10,7, 6}, {7,1, 8},
        {3, 9, 4}, {3, 4, 2}, {3, 2, 6}, {3, 6, 8}, {3, 8, 9},
        {4, 9, 5}, {2, 4,11}, {6, 2,10}, {8, 6, 7}, {9, 8, 1}
    };
    return m;
}

int main() {
    // ── 1. Икосаэдр корректен ────────────────────────────────────
    {
        auto ico = make_icosphere();
        check(ico.num_vertices() == 12, "icosphere: 12 vertices");
        check(ico.num_faces()    == 20, "icosphere: 20 faces");
        check(ico.is_watertight(),      "icosphere: watertight");
        double sa = ico.surface_area();
        double vol = ico.volume();
        std::cout << "  icosphere: surface=" << sa << "  vol=" << vol << "\n";
        check(sa > 0.0,  "icosphere: surface_area > 0");
        check(vol > 0.0, "icosphere: volume > 0");
    }

    // ── 2. cut_with_plane: срезать верхнюю половину (z > 0) ─────
    {
        auto ico = make_icosphere();
        PrintPreparation pp(ico);
        pp.cut_with_plane(Vector3d(0, 0, 0), Vector3d(0, 0, 1));

        // Все вершины должны иметь z <= 0 + eps
        for (const auto& v : ico.vertices_)
            check(v.z() <= 1e-6, "cut_with_plane: no vertex above plane");

        // После среза граница открытая (fill_holes не вызывается — это задача add_flat_base)
        check(!ico.is_watertight(), "cut_with_plane: open boundary after cut");
        check(ico.find_boundary_edges().size() > 0, "cut_with_plane: has boundary edges");
        std::cout << "  after cut: faces=" << ico.num_faces()
                  << "  boundary=" << ico.find_boundary_edges().size() << "\n";
    }

    // ── 3. add_flat_base ─────────────────────────────────────────
    {
        auto ico = make_icosphere();
        PrintPreparation pp(ico);
        pp.cut_with_plane(Vector3d(0, 0, 0), Vector3d(0, 0, 1));
        int faces_after_cut = static_cast<int>(ico.num_faces());

        pp.add_flat_base(0.1);

        check(static_cast<int>(ico.num_faces()) > faces_after_cut,
              "add_flat_base: face count increased");
        check(ico.is_watertight(), "add_flat_base: watertight after base");
        std::cout << "  after base: faces=" << ico.num_faces()
                  << "  watertight=" << ico.is_watertight() << "\n";
    }

    // ── 4. scale_to_size ─────────────────────────────────────────
    {
        auto ico = make_icosphere();
        PrintPreparation pp(ico);
        pp.scale_to_size(50.0, 'z');

        auto bb = ico.bounding_box();
        double height = bb.max.z() - bb.min.z();
        check(nearly(height, 50.0, 0.1), "scale_to_size: height ≈ 50 mm");
        std::cout << "  after scale: z-height=" << height << "\n";
    }

    // ── 5. auto_orient ───────────────────────────────────────────
    {
        auto ico = make_icosphere();
        // Наклоним меш
        for (auto& v : ico.vertices_) {
            double x = v.x(), z = v.z();
            v.x() = x * std::cos(0.5) - z * std::sin(0.5);
            v.z() = x * std::sin(0.5) + z * std::cos(0.5);
        }

        PrintPreparation pp(ico);
        pp.auto_orient();

        // z_min должен быть ≈ 0
        double z_min = ico.vertices_[0].z();
        for (const auto& v : ico.vertices_) z_min = std::min(z_min, v.z());
        check(std::abs(z_min) < 1e-6, "auto_orient: z_min ≈ 0");
        std::cout << "  auto_orient: z_min=" << z_min << "\n";
    }

    // ── 6. Полный пайплайн: cut → base → scale → watertight ─────
    {
        auto ico = make_icosphere();
        PrintPreparation pp(ico);

        pp.cut_with_plane(Vector3d(0, 0, 0.2), Vector3d(0, 0, 1));
        // После среза граница открыта — это ожидаемо
        check(!ico.is_watertight(), "pipeline: open after cut");

        pp.add_flat_base(2.0);
        check(ico.is_watertight(), "pipeline: watertight after base");

        pp.scale_to_size(50.0, 'z');

        auto bb = ico.bounding_box();
        check(nearly(bb.max.z() - bb.min.z(), 50.0, 0.5),
              "pipeline: height ≈ 50 mm");

        // check_printability
        PrintabilityReport rpt = pp.check_printability();
        check(rpt.is_watertight,    "pipeline: report is_watertight");
        check(rpt.volume_mm3 > 0.0, "pipeline: report volume > 0");
        std::cout << "  pipeline: vol=" << rpt.volume_mm3
                  << " mm3  sa=" << rpt.surface_area_mm2
                  << " mm2  warnings=" << rpt.warnings.size() << "\n";

        // Сохранить STL для внешней проверки Python
        bool saved = ico.save_stl("test_printprep.stl");
        check(saved, "pipeline: save_stl succeeded");
        std::cout << "  STL saved: test_printprep.stl\n";
    }

    // ── 7. check_printability на правильном кубе ─────────────────
    {
        TriangleMesh cube;
        cube.vertices_ = {
            {0,0,0}, {1,0,0}, {1,1,0}, {0,1,0},
            {0,0,1}, {1,0,1}, {1,1,1}, {0,1,1}
        };
        cube.faces_ = {
            {0,2,1}, {0,3,2},
            {4,5,6}, {4,6,7},
            {0,1,5}, {0,5,4},
            {2,3,7}, {2,7,6},
            {0,4,7}, {0,7,3},
            {1,2,6}, {1,6,5}
        };

        PrintPreparation pp(cube);
        PrintabilityReport rpt = pp.check_printability();

        check(rpt.is_watertight,         "cube: report is_watertight");
        check(rpt.open_edges == 0,       "cube: 0 open edges");
        check(nearly(rpt.volume_mm3, 1.0, 1e-4), "cube: volume ≈ 1");
        check(nearly(rpt.surface_area_mm2, 6.0, 1e-4), "cube: sa ≈ 6");
        // Нижняя грань куба (нормаль -Z) корректно помечается как навес
        check(rpt.has_overhangs, "cube: bottom face flagged as overhang");
        std::cout << "  cube: vol=" << rpt.volume_mm3
                  << "  sa=" << rpt.surface_area_mm2
                  << "  warnings=" << rpt.warnings.size() << "\n";
    }

    std::cout << "All tests PASSED\n";
    return 0;
}
