// Тест: MeshRepair — куб без одной грани → fill_holes → watertight
#include "scanner/mesh_repair.h"

#include <cassert>
#include <cmath>
#include <iostream>

using namespace scanner;

static void check(bool cond, const char* msg) {
    if (!cond) { std::cerr << "FAIL: " << msg << "\n"; std::exit(1); }
}
static bool nearly(double a, double b, double tol = 1e-4) {
    return std::abs(a - b) < tol;
}

// Единичный куб [0,1]^3 — 12 граней, ориентация наружу
static TriangleMesh make_cube() {
    TriangleMesh m;
    m.vertices_ = {
        {0,0,0}, {1,0,0}, {1,1,0}, {0,1,0},
        {0,0,1}, {1,0,1}, {1,1,1}, {0,1,1}
    };
    m.faces_ = {
        {0,2,1}, {0,3,2},           // дно
        {4,5,6}, {4,6,7},           // крыша
        {0,1,5}, {0,5,4},           // перед
        {2,3,7}, {2,7,6},           // зад
        {0,4,7}, {0,7,3},           // лево
        {1,2,6}, {1,6,5}            // право
    };
    return m;
}

int main() {
    // ── 1. Базовый куб ───────────────────────────────────────────
    {
        auto cube = make_cube();
        check(cube.is_watertight(),            "full cube is watertight");
        check(nearly(cube.volume(), 1.0),      "full cube volume == 1.0");
        check(nearly(cube.surface_area(), 6.0),"full cube surface_area == 6.0");
    }

    // ── 2. fill_holes: куб без правой грани (2 треугольника) ────
    {
        auto cube = make_cube();
        cube.faces_.pop_back();   // убрать {1,6,5}
        cube.faces_.pop_back();   // убрать {1,2,6}

        check(!cube.is_watertight(), "cube minus right face: not watertight");
        auto bd = cube.find_boundary_edges();
        check(bd.size() == 4, "cube minus right face: 4 boundary edges");
        std::cout << "  boundary edges: " << bd.size() << "\n";

        MeshRepair r(cube);
        int filled = r.fill_holes();

        check(filled == 1,            "fill_holes: 1 hole filled");
        check(cube.num_faces() == 12, "fill_holes: 12 faces after fill");
        check(cube.is_watertight(),   "fill_holes: watertight after fill");
        check(nearly(cube.volume(), 1.0, 1e-4),      "fill_holes: volume ≈ 1.0");
        check(nearly(cube.surface_area(), 6.0, 1e-4),"fill_holes: surface_area ≈ 6.0");
        std::cout << "  filled=" << filled << "  faces=" << cube.num_faces()
                  << "  watertight=" << cube.is_watertight() << "\n";
    }

    // ── 3. fill_holes: куб без одного треугольника ───────────────
    {
        auto cube = make_cube();
        cube.faces_.pop_back();   // убрать {1,6,5}  — треугольная дырка

        MeshRepair r(cube);
        check(r.fill_holes() == 1,    "triangle hole: 1 hole filled");
        check(cube.is_watertight(),   "triangle hole: watertight after fill");
        check(cube.num_faces() == 12, "triangle hole: 12 faces");
    }

    // ── 4. remove_degenerate_faces ───────────────────────────────
    {
        auto cube = make_cube();
        // Добавляем вырожденную грань (дублированный индекс)
        cube.faces_.push_back({0, 0, 1});
        // Добавляем грань с нулевой площадью (коллинеарные вершины: все на x-axis)
        cube.vertices_.push_back({0.5, 0, 0});  // индекс 8
        cube.vertices_.push_back({0.6, 0, 0});  // индекс 9
        cube.faces_.push_back({0, 8, 9});        // коллинеарно с (0,0,0)-(0.5,0,0)-(0.6,0,0)

        check(cube.num_faces() == 14, "before degenerate removal: 14 faces");

        MeshRepair r(cube);
        int rem = r.remove_degenerate_faces();

        check(rem == 2,               "remove_degenerate_faces: removed 2");
        check(cube.num_faces() == 12, "remove_degenerate_faces: 12 faces left");
        std::cout << "  degenerate removed: " << rem << "\n";
    }

    // ── 5. remove_duplicate_faces ────────────────────────────────
    {
        auto cube = make_cube();
        // Добавляем дубликаты первых двух граней с другим обходом
        cube.faces_.push_back({2, 0, 1});   // {0,2,1} — циклический дубликат
        cube.faces_.push_back({3, 2, 0});   // {0,3,2} — другой порядок, те же вершины

        MeshRepair r(cube);
        int rem = r.remove_duplicate_faces();

        check(rem == 2,               "remove_duplicate_faces: removed 2");
        check(cube.num_faces() == 12, "remove_duplicate_faces: 12 faces left");
        std::cout << "  duplicates removed: " << rem << "\n";
    }

    // ── 6. merge_close_vertices ──────────────────────────────────
    {
        auto cube = make_cube();
        // Добавляем вершину почти совпадающую с вершиной 0=(0,0,0)
        cube.vertices_.push_back({1e-8, 0, 0});  // индекс 8
        cube.faces_.push_back({8, 1, 2});         // грань, использующая новую вершину

        check(cube.num_vertices() == 9, "before merge: 9 vertices");

        MeshRepair r(cube);
        int merged = r.merge_close_vertices(1e-6);

        check(merged == 1,              "merge_close_vertices: merged 1 pair");
        check(cube.num_vertices() == 8, "merge_close_vertices: 8 vertices left");
        std::cout << "  vertices merged: " << merged << "\n";
    }

    // ── 7. laplacian_smooth ───────────────────────────────────────
    {
        auto cube = make_cube();
        double vol_before = cube.volume();

        MeshRepair r(cube);
        r.laplacian_smooth(5, 0.5);

        // Нормали должны быть сброшены
        check(cube.normals_.empty(), "laplacian_smooth: normals cleared");
        // Замкнутый куб — все вершины двигаются, но объём меняется незначительно
        // (Laplacian shrinks shape, but test just checks it runs)
        double vol_after = cube.volume();
        std::cout << "  smooth: vol " << vol_before << " -> " << vol_after << "\n";
    }

    // ── 8. repair_all: полностью сломанный меш ───────────────────
    {
        auto cube = make_cube();
        // Убрать грань, добавить дырку; добавить дубликат; добавить вырожденность
        cube.faces_.pop_back();                // дырка (1 треугольник)
        cube.faces_.push_back({0, 0, 1});      // вырожденная
        cube.faces_.push_back({0, 2, 1});      // дубликат (дно уже имеет {0,2,1})

        MeshRepair r(cube);
        RepairReport rpt = r.repair_all(0);   // без сглаживания

        check(rpt.degenerate_removed >= 1, "repair_all: removed degenerate");
        check(rpt.duplicate_removed  >= 1, "repair_all: removed duplicate");
        check(rpt.holes_filled       == 1, "repair_all: filled 1 hole");
        check(cube.is_watertight(),        "repair_all: watertight result");

        std::cout << "  repair_all: degenerate=" << rpt.degenerate_removed
                  << "  dup=" << rpt.duplicate_removed
                  << "  merged=" << rpt.vertices_merged
                  << "  holes=" << rpt.holes_filled << "\n";
    }

    std::cout << "All tests PASSED\n";
    return 0;
}
