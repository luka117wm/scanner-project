#pragma once
#include "types.h"
#include <filesystem>
#include <memory>
#include <vector>

namespace scanner {

// PIMPL: детали nanoflann скрыты от публичного заголовка
struct PointCloudKDTreeImpl;

class PointCloud {
public:
    std::vector<Vector3d> points_;   // XYZ координаты
    std::vector<Vector3d> normals_;  // единичные нормали (может быть пустым)
    std::vector<Color>    colors_;   // RGB [0,255]  (может быть пустым)

    // Специальные члены — деструктор определён в .cpp (неполный тип unique_ptr)
    PointCloud();
    ~PointCloud();
    PointCloud(PointCloud&&) noexcept;
    PointCloud& operator=(PointCloud&&) noexcept;
    PointCloud(const PointCloud&)            = delete;
    PointCloud& operator=(const PointCloud&) = delete;

    // --- I/O ---------------------------------------------------------------
    // Читает ASCII и binary_little_endian PLY; свойства по именам x/y/z/nx/ny/nz/red/green/blue
    bool load_ply(const std::filesystem::path& path);
    // Всегда пишет binary_little_endian: float x,y,z,nx,ny,nz + uchar r,g,b
    bool save_ply(const std::filesystem::path& path) const;

    // --- Геометрия ---------------------------------------------------------
    std::size_t size()  const noexcept { return points_.size(); }
    bool        empty() const noexcept { return points_.empty(); }

    BoundingBox bounding_box()    const;
    void        center_to_origin();   // смещает points_ так, чтобы центр bbox = (0,0,0)

    // --- Фильтрация и обработка -------------------------------------------
    // Statistical Outlier Removal: удаляет точки, у которых среднее расстояние
    // до k ближайших соседей > mean + std_ratio * stddev
    PointCloud statistical_outlier_removal(int k = 20, double std_ratio = 2.0) const;

    // Voxel grid downsampling: схлопывает точки в вокселях размером voxel_size
    // в их центроид; сохраняет средние нормали и цвета если есть
    PointCloud voxel_downsample(double voxel_size) const;

    // PCA-оценка нормалей по k ближайшим соседям; нормали ориентированы
    // от центра масс облака наружу (перезаписывает normals_)
    void estimate_normals(int k = 30);

    // DBSCAN: возвращает наибольший кластер + все кластеры, чей размер
    // >= largest_size * min_cluster_fraction (0 → только наибольший).
    PointCloud segment_largest_cluster(double eps = 0.02, int min_points = 50,
                                       double min_cluster_fraction = 0.05) const;

    // --- KD-tree (nanoflann L2, по points_) --------------------------------
    void build_kdtree();

    // k ближайших соседей → [(индекс, расстояние²), ...], отсортировано по расстоянию
    std::vector<std::pair<std::size_t, double>>
        k_nearest(const Vector3d& query, std::size_t k) const;

    // Все точки в радиусе r → [(индекс, расстояние²), ...]
    std::vector<std::pair<std::size_t, double>>
        radius_search(const Vector3d& query, double radius) const;

private:
    void ensure_kdtree() const;   // ленивое построение

    mutable std::unique_ptr<PointCloudKDTreeImpl> kdtree_;
};

} // namespace scanner
