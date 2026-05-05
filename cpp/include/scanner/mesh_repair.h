#pragma once
#include "triangle_mesh.h"

namespace scanner {

struct RepairReport {
    int degenerate_removed   = 0;
    int duplicate_removed    = 0;
    int vertices_merged      = 0;
    int non_manifold_removed = 0;
    int holes_filled         = 0;
    int smooth_iterations    = 0;

    bool any_repair() const {
        return degenerate_removed || duplicate_removed || vertices_merged
            || non_manifold_removed || holes_filled || smooth_iterations > 0;
    }
};

// Все методы модифицируют mesh_ на месте и возвращают количество изменений.
class MeshRepair {
public:
    explicit MeshRepair(TriangleMesh& mesh) : mesh_(mesh) {}

    // Удалить грани с нулевой площадью или дублирующимися индексами вершин
    int remove_degenerate_faces();

    // Удалить грани-дубликаты (одинаковый набор вершин в любом порядке)
    int remove_duplicate_faces();

    // Слить вершины, расстояние между которыми <= threshold; обновить индексы граней
    int merge_close_vertices(double threshold = 1e-6);

    // Удалить грани, содержащие non-manifold рёбра (ребро в > 2 гранях)
    int make_manifold();

    // Заполнить дырки фановой триангуляцией; пропустить контуры длиннее max_hole_edges
    int fill_holes(int max_hole_edges = 100);

    // Сглаживание Лапласа; граничные вершины не двигать
    void laplacian_smooth(int iterations = 3, double lambda = 0.5);

    // Полный цикл ремонта; возвращает отчёт
    RepairReport repair_all(int smooth_iterations = 3, int max_hole_edges = 100);

private:
    TriangleMesh& mesh_;
};

} // namespace scanner
