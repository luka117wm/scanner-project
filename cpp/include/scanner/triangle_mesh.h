#pragma once
#include "types.h"
#include <filesystem>
#include <map>
#include <vector>

namespace scanner {

class TriangleMesh {
public:
    std::vector<Vector3d> vertices_;   // XYZ координаты вершин
    std::vector<Vector3i> faces_;      // индексы вершин (3×int)
    std::vector<Vector3d> normals_;    // per-face нормали (может быть пустым)
    std::vector<Color>    colors_;     // per-vertex цвета RGB (может быть пустым)

    // --- I/O ---------------------------------------------------------------
    bool load_ply(const std::filesystem::path& path);
    bool load_stl(const std::filesystem::path& path);   // только binary STL
    bool save_ply(const std::filesystem::path& path) const;
    bool save_stl(const std::filesystem::path& path) const;  // binary STL
    bool save_obj(const std::filesystem::path& path) const;  // ASCII OBJ

    // --- Базовые свойства --------------------------------------------------
    std::size_t num_vertices() const noexcept { return vertices_.size(); }
    std::size_t num_faces()    const noexcept { return faces_.size(); }
    bool        empty()        const noexcept { return faces_.empty(); }

    BoundingBox bounding_box() const;

    // --- Геометрия ---------------------------------------------------------
    void   compute_normals();    // per-face нормали → normals_
    double surface_area() const;
    double volume()       const; // знаковый объём через теорему Гаусса, |result|

    // --- Топология ---------------------------------------------------------
    // Каждое ребро ровно в 2 гранях → замкнутая (wateright) поверхность
    bool is_watertight() const;

    // Рёбра: ключ (min_v, max_v) → список индексов граней, содержащих это ребро
    using EdgeMap = std::map<std::pair<int, int>, std::vector<int>>;
    EdgeMap build_edge_map() const;

    // Рёбра, принадлежащие != 2 граням (граница сетки)
    std::vector<std::pair<int, int>> find_boundary_edges() const;

    // Вершины, соединённые ребром с вершиной v
    std::vector<int> get_vertex_neighbors(int v) const;
};

} // namespace scanner
