#pragma once
#include "triangle_mesh.h"
#include <string>
#include <vector>

namespace scanner {

struct PrintabilityReport {
    bool   is_watertight      = false;
    bool   has_thin_walls     = false;   // min edge < 0.4 mm
    bool   has_overhangs      = false;   // face normal Z < -0.707
    double volume_mm3         = 0.0;
    double surface_area_mm2   = 0.0;
    double bbox_x_mm          = 0.0;
    double bbox_y_mm          = 0.0;
    double bbox_z_mm          = 0.0;
    int    open_edges         = 0;
    std::vector<std::string> warnings;

    bool is_printable() const { return is_watertight && !has_thin_walls; }
};

// Все методы модифицируют mesh_ на месте.
class PrintPreparation {
public:
    explicit PrintPreparation(TriangleMesh& mesh) : mesh_(mesh) {}

    // Срезать меш плоскостью; сохранить часть ниже (n·(v-p) <= 0).
    // Автоматически заполняет образовавшуюся дырку.
    void cut_with_plane(const Vector3d& point, const Vector3d& normal);

    // Добавить плоское основание: стенки к уровню z_min-thickness + крышка снизу.
    void add_flat_base(double thickness = 2.0);

    // Add a circular disc stand below the object (z_min-thickness .. z_min).
    // radius = min(bbox_x, bbox_y)/2 * radius_fraction.
    void add_disc_stand(double radius_fraction = 0.9, double thickness = 2.0);

    // Равномерный масштаб до целевого размера (мм) вдоль оси axis ('x','y','z').
    void scale_to_size(double target_mm, char axis = 'z');

    // Авто-ориентация: грань с наибольшей площадью — вниз; z_min → 0.
    void auto_orient();

    // Проверка пригодности к печати.
    PrintabilityReport check_printability() const;

private:
    TriangleMesh& mesh_;
};

} // namespace scanner
