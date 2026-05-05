#include "scanner/print_preparation.h"
#include "scanner/mesh_repair.h"

#ifndef M_PI
#  define M_PI 3.14159265358979323846
#endif

#include <algorithm>
#include <cmath>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace scanner {

// ============================================================
//  cut_with_plane
// ============================================================

void PrintPreparation::cut_with_plane(const Vector3d& point, const Vector3d& normal) {
    const Vector3d n = normal.normalized();

    // Signed distance от плоскости для каждой вершины
    const int NV = static_cast<int>(mesh_.vertices_.size());
    std::vector<double> dist(NV);
    for (int i = 0; i < NV; ++i)
        dist[i] = n.dot(mesh_.vertices_[i] - point);

    // Кэш пересечений рёбер: ключ = min_v * NV_MAX + max_v (уникальный)
    // Значение = индекс новой вершины-пересечения
    std::unordered_map<int64_t, int> edge_cache;

    auto split_edge = [&](int a, int b) -> int {
        // Если конечная точка лежит на плоскости — вернуть её напрямую,
        // иначе создадим дублирующую вершину и сломаем boundary_next.
        if (std::abs(dist[b]) < 1e-12) return b;
        if (std::abs(dist[a]) < 1e-12) return a;

        int lo = std::min(a, b), hi = std::max(a, b);
        int64_t key = static_cast<int64_t>(lo) * 1000000LL + hi;
        auto it = edge_cache.find(key);
        if (it != edge_cache.end()) return it->second;

        double da = dist[a], db = dist[b];
        double t = da / (da - db);
        Vector3d p = mesh_.vertices_[a] + t * (mesh_.vertices_[b] - mesh_.vertices_[a]);
        int idx = static_cast<int>(mesh_.vertices_.size());
        mesh_.vertices_.push_back(p);
        dist.push_back(0.0);
        edge_cache[key] = idx;
        return idx;
    };

    std::vector<Vector3i> new_faces;
    new_faces.reserve(mesh_.faces_.size());

    for (const auto& f : mesh_.faces_) {
        int vi[3] = { f[0], f[1], f[2] };
        // ниже/на плоскости → сохраняем; выше → отбрасываем
        bool below[3];
        for (int k = 0; k < 3; ++k) below[k] = dist[vi[k]] <= 0.0;

        int cnt_below = below[0] + below[1] + below[2];

        if (cnt_below == 3) {
            new_faces.push_back(f);
            continue;
        }
        if (cnt_below == 0) continue;

        // Ровно 1 вершина ниже или на плоскости
        if (cnt_below == 1) {
            // Найти единственную нижнюю вершину
            int ia = -1;
            for (int k = 0; k < 3; ++k) if (below[k]) { ia = k; break; }
            int ib = (ia + 1) % 3, ic = (ia + 2) % 3;
            int va = vi[ia], vb = vi[ib], vc = vi[ic];

            // Если da == 0 (точно на плоскости) — треугольник вырождается в точку/линию
            if (std::abs(dist[va]) < 1e-12) continue;

            int pab = split_edge(va, vb);
            int pac = split_edge(va, vc);
            new_faces.push_back({ va, pab, pac });
            continue;
        }

        // Ровно 2 вершины ниже
        {
            // Найти единственную верхнюю вершину
            int ia = -1;
            for (int k = 0; k < 3; ++k) if (!below[k]) { ia = k; break; }
            int ib = (ia + 1) % 3, ic = (ia + 2) % 3;
            int va = vi[ia], vb = vi[ib], vc = vi[ic];

            int pab = split_edge(va, vb);
            int pac = split_edge(va, vc);

            // Два треугольника, обход совпадает с оригинальным
            new_faces.push_back({ vb, vc, pac });
            new_faces.push_back({ vb, pac, pab });
        }
    }

    mesh_.faces_   = std::move(new_faces);
    mesh_.normals_.clear();

    // Убрать вырожденные грани, затем удалить вершины без ссылок.
    // fill_holes НЕ вызываем: граничный контур остаётся открытым,
    // чтобы add_flat_base мог построить стенки и крышку.
    MeshRepair(mesh_).remove_degenerate_faces();

    {
        const int NV2 = static_cast<int>(mesh_.vertices_.size());
        std::vector<int> remap(NV2, -1);
        std::vector<Vector3d> new_verts;
        for (const auto& f : mesh_.faces_)
            for (int k = 0; k < 3; ++k) remap[f[k]] = 1;
        for (int i = 0; i < NV2; ++i) {
            if (remap[i] == 1) {
                remap[i] = static_cast<int>(new_verts.size());
                new_verts.push_back(mesh_.vertices_[i]);
            }
        }
        for (auto& f : mesh_.faces_)
            for (int k = 0; k < 3; ++k) f[k] = remap[f[k]];
        mesh_.vertices_ = std::move(new_verts);
        if (!mesh_.colors_.empty()) mesh_.colors_.clear();
    }
}

// ============================================================
//  add_flat_base
// ============================================================

void PrintPreparation::add_flat_base(double thickness) {
    if (mesh_.faces_.empty()) return;

    // Построить множество направленных рёбер (directed edges)
    const int64_t NV = static_cast<int64_t>(mesh_.vertices_.size());
    std::unordered_set<int64_t> de_set;
    de_set.reserve(mesh_.faces_.size() * 3);
    for (const auto& f : mesh_.faces_) {
        de_set.insert(static_cast<int64_t>(f[0]) * NV + f[1]);
        de_set.insert(static_cast<int64_t>(f[1]) * NV + f[2]);
        de_set.insert(static_cast<int64_t>(f[2]) * NV + f[0]);
    }

    std::unordered_map<int,int> boundary_next;
    for (int64_t de : de_set) {
        int a = static_cast<int>(de / NV);
        int b = static_cast<int>(de % NV);
        if (!de_set.count(static_cast<int64_t>(b) * NV + a))
            boundary_next.emplace(b, a);
    }

    if (boundary_next.empty()) return;   // меш уже watertight

    // Трассируем ВСЕ граничные контуры
    std::vector<std::vector<int>> all_loops;
    std::unordered_set<int> visited;
    for (auto& [start_v, _] : boundary_next) {
        if (visited.count(start_v)) continue;
        std::vector<int> loop;
        int cur = start_v;
        while (!visited.count(cur)) {
            auto it = boundary_next.find(cur);
            if (it == boundary_next.end()) { loop.clear(); break; }
            visited.insert(cur);
            loop.push_back(cur);
            cur = it->second;
            if (cur == start_v) break;
        }
        if (!loop.empty() && cur == start_v)
            all_loops.push_back(std::move(loop));
    }
    if (all_loops.empty()) return;

    // Определяем «нижний» контур (наименьшая средняя Z) — ему делаем стенки + основание.
    // Все остальные контуры закрываем фановой крышкой.
    int base_idx = 0;
    double min_z_avg = std::numeric_limits<double>::max();
    for (int li = 0; li < static_cast<int>(all_loops.size()); ++li) {
        double z_sum = 0.0;
        for (int v : all_loops[li]) z_sum += mesh_.vertices_[v].z();
        double z_avg = z_sum / static_cast<double>(all_loops[li].size());
        if (z_avg < min_z_avg) { min_z_avg = z_avg; base_idx = li; }
    }

    // ── Нижний контур: стенки + плоское основание ─────────────────────────────
    {
        const auto& loop = all_loops[base_idx];
        const int n = static_cast<int>(loop.size());

        double z_min = mesh_.vertices_[loop[0]].z();
        for (int v : loop) z_min = std::min(z_min, mesh_.vertices_[v].z());
        double z_base = z_min - thickness;

        Vector3d cen = Vector3d::Zero();
        for (int v : loop) cen += mesh_.vertices_[v];
        cen /= static_cast<double>(n);
        cen.z() = z_base;

        const int base_start = static_cast<int>(mesh_.vertices_.size());
        for (int v : loop) {
            Vector3d bv = mesh_.vertices_[v];
            bv.z() = z_base;
            mesh_.vertices_.push_back(bv);
        }
        const int cen_idx = static_cast<int>(mesh_.vertices_.size());
        mesh_.vertices_.push_back(cen);

        for (int i = 0; i < n; ++i) {
            int j     = (i + 1) % n;
            int top_i = loop[i], top_j = loop[j];
            int bot_i = base_start + i, bot_j = base_start + j;
            mesh_.faces_.push_back({ top_j, top_i, bot_i });
            mesh_.faces_.push_back({ top_j, bot_i, bot_j });
        }
        for (int i = 0; i < n; ++i) {
            int ni = (i + 1) % n;
            mesh_.faces_.push_back({ cen_idx, base_start + i, base_start + ni });
        }
    }

    // ── Остальные контуры: фановая крышка (закрывает отверстия сверху/сбоку) ──
    for (int li = 0; li < static_cast<int>(all_loops.size()); ++li) {
        if (li == base_idx) continue;
        const auto& loop = all_loops[li];
        const int n = static_cast<int>(loop.size());

        Vector3d cen = Vector3d::Zero();
        for (int v : loop) cen += mesh_.vertices_[v];
        cen /= static_cast<double>(n);

        const int cen_idx = static_cast<int>(mesh_.vertices_.size());
        mesh_.vertices_.push_back(cen);

        // Ориентация крышки: нормаль должна смотреть наружу.
        // Вычисляем знак через первые три вершины.
        Vector3d edge1 = mesh_.vertices_[loop[1]] - cen;
        Vector3d edge2 = mesh_.vertices_[loop[0]] - cen;
        Vector3d fn    = edge1.cross(edge2);
        // Если нормаль смотрит вниз (-Z) — значит крышка снизу, нам нужна вверх.
        // Для верхних отверстий нормаль должна смотреть наружу (обычно +Z или вбок).
        bool flip = (fn.z() < 0.0);

        for (int i = 0; i < n; ++i) {
            int ni = (i + 1) % n;
            if (!flip)
                mesh_.faces_.push_back({ cen_idx, loop[i], loop[ni] });
            else
                mesh_.faces_.push_back({ cen_idx, loop[ni], loop[i] });
        }
    }

    mesh_.normals_.clear();
}

// ============================================================
//  scale_to_size
// ============================================================

void PrintPreparation::scale_to_size(double target_mm, char axis) {
    if (mesh_.vertices_.empty()) return;

    auto bb = mesh_.bounding_box();
    double ext = 0.0;
    switch (axis) {
        case 'x': ext = bb.max.x() - bb.min.x(); break;
        case 'y': ext = bb.max.y() - bb.min.y(); break;
        case 'z': default: ext = bb.max.z() - bb.min.z(); break;
    }
    if (ext < 1e-12) return;

    const double s = target_mm / ext;
    for (auto& v : mesh_.vertices_) v *= s;
    mesh_.normals_.clear();
}

// ============================================================
//  auto_orient
// ============================================================

void PrintPreparation::auto_orient() {
    if (mesh_.faces_.empty() || mesh_.vertices_.empty()) return;

    // PCA по вершинам — находим 3 главные оси объекта
    Vector3d centroid = Vector3d::Zero();
    for (const auto& v : mesh_.vertices_) centroid += v;
    centroid /= static_cast<double>(mesh_.vertices_.size());

    Eigen::Matrix3d cov = Eigen::Matrix3d::Zero();
    for (const auto& v : mesh_.vertices_) {
        Vector3d d = v - centroid;
        cov += d * d.transpose();
    }

    Eigen::SelfAdjointEigenSolver<Eigen::Matrix3d> solver(cov);
    // eigenvectors: col(0)=наименьший (плоская ось), col(2)=наибольший (длинная ось)

    // Перебираем 6 кандидатов: ±каждая из 3 осей PCA как направление "вверх"
    // Для каждого вычисляем суммарную площадь нижних граней (нормаль → -Z)
    // Лучший → наиболее устойчивое основание для печати.

    auto score_R = [&](const Eigen::Matrix3d& R) -> double {
        double area = 0.0;
        for (const auto& f : mesh_.faces_) {
            Vector3d rv0 = R * mesh_.vertices_[f[0]];
            Vector3d rv1 = R * mesh_.vertices_[f[1]];
            Vector3d rv2 = R * mesh_.vertices_[f[2]];
            Vector3d fn  = (rv1 - rv0).cross(rv2 - rv0);
            double   fa  = fn.norm() * 0.5;
            fn /= (fn.norm() + 1e-15);
            // Грань смотрит вниз (-Z) и находится в нижней трети объекта по Z
            if (fn.z() < -0.5) area += fa;
        }
        return area;
    };

    auto make_R = [](const Vector3d& up) -> Eigen::Matrix3d {
        Vector3d z   = Vector3d::UnitZ();
        Vector3d ax  = up.cross(z);
        double   s   = ax.norm();
        double   c   = up.dot(z);
        if (s < 1e-8)
            return (c > 0) ? Eigen::Matrix3d::Identity()
                           : Eigen::AngleAxisd(M_PI, Vector3d::UnitX()).toRotationMatrix();
        ax /= s;
        return Eigen::AngleAxisd(std::atan2(s, c), ax).toRotationMatrix();
    };

    Eigen::Matrix3d best_R = Eigen::Matrix3d::Identity();
    double best_score = -1.0;

    for (int col = 0; col < 3; ++col) {
        for (int sign : {1, -1}) {
            Vector3d up = sign * solver.eigenvectors().col(col);
            Eigen::Matrix3d R = make_R(up);
            double s = score_R(R);
            if (s > best_score) { best_score = s; best_R = R; }
        }
    }

    for (auto& v : mesh_.vertices_) v = best_R * v;

    double z_min = mesh_.vertices_[0].z();
    for (const auto& v : mesh_.vertices_) z_min = std::min(z_min, v.z());
    for (auto& v : mesh_.vertices_) v.z() -= z_min;

    mesh_.normals_.clear();
}

// ============================================================
//  check_printability
// ============================================================

PrintabilityReport PrintPreparation::check_printability() const {
    PrintabilityReport r;

    r.is_watertight   = mesh_.is_watertight();
    r.open_edges      = static_cast<int>(mesh_.find_boundary_edges().size());
    r.volume_mm3      = mesh_.volume();
    r.surface_area_mm2 = mesh_.surface_area();

    auto bb = mesh_.bounding_box();
    r.bbox_x_mm = bb.max.x() - bb.min.x();
    r.bbox_y_mm = bb.max.y() - bb.min.y();
    r.bbox_z_mm = bb.max.z() - bb.min.z();

    // Проверка тонких стенок (ребро < 0.4 мм)
    constexpr double MIN_EDGE = 0.4;
    for (const auto& f : mesh_.faces_) {
        for (int e = 0; e < 3; ++e) {
            double len = (mesh_.vertices_[f[e]] - mesh_.vertices_[f[(e+1)%3]]).norm();
            if (len < MIN_EDGE) { r.has_thin_walls = true; break; }
        }
        if (r.has_thin_walls) break;
    }

    // Проверка навесов: нормаль грани Z < -0.707 (угол > 45° вниз)
    for (const auto& f : mesh_.faces_) {
        const Vector3d& v0 = mesh_.vertices_[f[0]];
        const Vector3d& v1 = mesh_.vertices_[f[1]];
        const Vector3d& v2 = mesh_.vertices_[f[2]];
        Vector3d n = (v1 - v0).cross(v2 - v0);
        double len = n.norm();
        if (len < 1e-12) continue;
        if (n.z() / len < -0.707) { r.has_overhangs = true; break; }
    }

    if (!r.is_watertight)
        r.warnings.push_back("Mesh is not watertight (" +
                             std::to_string(r.open_edges) + " open edges)");
    if (r.has_thin_walls)
        r.warnings.push_back("Thin walls detected (edge < 0.4 mm)");
    if (r.has_overhangs)
        r.warnings.push_back("Overhanging faces detected (>45 deg)");

    return r;
}

// ============================================================
//  add_disc_stand
// ============================================================

void PrintPreparation::add_disc_stand(double radius_fraction, double thickness) {
    if (mesh_.vertices_.empty() || mesh_.faces_.empty()) return;

    auto bb = mesh_.bounding_box();
    if (!bb.valid()) return;

    const double z_min  = bb.min.z();
    const double z_base = z_min - std::max(thickness, 1e-6);
    const double cx     = (bb.min.x() + bb.max.x()) * 0.5;
    const double cy     = (bb.min.y() + bb.max.y()) * 0.5;

    const double half_x = (bb.max.x() - bb.min.x()) * 0.5;
    const double half_y = (bb.max.y() - bb.min.y()) * 0.5;
    const double radius = std::min(half_x, half_y) * radius_fraction;
    if (radius < 1e-8) return;

    constexpr int N = 64;
    const int base_v = static_cast<int>(mesh_.vertices_.size());

    for (int i = 0; i < N; ++i) {
        const double a = 2.0 * M_PI * i / N;
        mesh_.vertices_.push_back({cx + radius * std::cos(a), cy + radius * std::sin(a), z_min});
    }
    for (int i = 0; i < N; ++i) {
        const double a = 2.0 * M_PI * i / N;
        mesh_.vertices_.push_back({cx + radius * std::cos(a), cy + radius * std::sin(a), z_base});
    }
    const int top_cen = static_cast<int>(mesh_.vertices_.size());
    mesh_.vertices_.push_back({cx, cy, z_min});
    const int bot_cen = static_cast<int>(mesh_.vertices_.size());
    mesh_.vertices_.push_back({cx, cy, z_base});

    for (int i = 0; i < N; ++i) {
        const int ni  = (i + 1) % N;
        const int ti  = base_v + i,     tni = base_v + ni;
        const int bi  = base_v + N + i, bni = base_v + N + ni;
        mesh_.faces_.push_back({top_cen, ti,  tni});   // top face  (+Z)
        mesh_.faces_.push_back({bot_cen, bni, bi});    // bot face  (-Z)
        mesh_.faces_.push_back({ti,  bi,  tni});       // side quad (outward)
        mesh_.faces_.push_back({bi,  bni, tni});
    }
    mesh_.normals_.clear();
}

} // namespace scanner
