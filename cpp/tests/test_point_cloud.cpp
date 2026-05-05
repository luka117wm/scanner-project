// Тест: PointCloud — PLY round-trip + KD-tree
// Запуск: ctest -C Release --output-on-failure
#include "scanner/point_cloud.h"

#include <cassert>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <random>

using namespace scanner;

// ----------------------------------------------------------------
// Вспомогательные проверки
// ----------------------------------------------------------------
static void check(bool cond, const char* msg) {
    if (!cond) {
        std::cerr << "FAIL: " << msg << "\n";
        std::exit(1);
    }
}

static bool nearly_eq(double a, double b, double tol = 1e-5) {
    return std::abs(a - b) < tol;
}

// ----------------------------------------------------------------
// Основной тест
// ----------------------------------------------------------------
int main() {
    constexpr int N = 1000;
    std::mt19937 rng(42);
    std::uniform_real_distribution<double> pos_dist(-10.0, 10.0);
    std::uniform_real_distribution<double> dir_dist(-1.0, 1.0);

    // ── 1. Создаём облако точек ──────────────────────────────────
    PointCloud pc;
    pc.points_ .resize(N);
    pc.normals_.resize(N);
    pc.colors_ .resize(N);

    for (int i = 0; i < N; ++i) {
        pc.points_ [i] = { pos_dist(rng), pos_dist(rng), pos_dist(rng) };
        pc.normals_[i] = Vector3d(dir_dist(rng), dir_dist(rng), dir_dist(rng)).normalized();
        pc.colors_ [i] = {
            static_cast<uint8_t>(i % 256),
            static_cast<uint8_t>((i * 3) % 256),
            static_cast<uint8_t>((i * 7) % 256)
        };
    }
    check(pc.size() == N, "size() == N after fill");

    // ── 2. Bounding box ──────────────────────────────────────────
    BoundingBox bb = pc.bounding_box();
    check(bb.valid(), "bounding_box valid");
    for (int d = 0; d < 3; ++d)
        check(bb.min[d] <= bb.max[d], "bbox min <= max per axis");

    // ── 3. Save PLY (binary) ─────────────────────────────────────
    auto tmp = std::filesystem::temp_directory_path() / "scanner_test_pc.ply";
    bool saved = pc.save_ply(tmp);
    check(saved, "save_ply returned true");
    check(std::filesystem::exists(tmp), "PLY file exists on disk");
    check(std::filesystem::file_size(tmp) > 0, "PLY file non-empty");

    // ── 4. Load PLY ──────────────────────────────────────────────
    PointCloud pc2;
    bool loaded = pc2.load_ply(tmp);
    check(loaded, "load_ply returned true");
    check(pc2.size() == N, "loaded point count == N");
    check(pc2.normals_.size() == N, "loaded normals count == N");
    check(pc2.colors_ .size() == N, "loaded colors count == N");

    // ── 5. Round-trip: позиции (float32 precision ~1e-6 относительная) ──
    for (int i = 0; i < N; ++i) {
        for (int d = 0; d < 3; ++d) {
            check(nearly_eq(pc.points_[i][d], pc2.points_[i][d], 1e-4),
                  "position round-trip within tolerance");
        }
    }

    // ── 6. Round-trip: нормали ───────────────────────────────────
    for (int i = 0; i < N; ++i) {
        for (int d = 0; d < 3; ++d) {
            check(nearly_eq(pc.normals_[i][d], pc2.normals_[i][d], 1e-4),
                  "normal round-trip within tolerance");
        }
    }

    // ── 7. Round-trip: цвета (uint8, без потерь) ─────────────────
    for (int i = 0; i < N; ++i) {
        check(pc.colors_[i].r == pc2.colors_[i].r, "color.r round-trip");
        check(pc.colors_[i].g == pc2.colors_[i].g, "color.g round-trip");
        check(pc.colors_[i].b == pc2.colors_[i].b, "color.b round-trip");
    }

    // ── 8. center_to_origin ──────────────────────────────────────
    pc2.center_to_origin();
    BoundingBox bb2 = pc2.bounding_box();
    Vector3d c = bb2.center();
    for (int d = 0; d < 3; ++d)
        check(std::abs(c[d]) < 1e-9, "center_to_origin: bbox center ≈ 0");

    // ── 9. KD-tree: build ────────────────────────────────────────
    pc.build_kdtree();

    // 9a. k_nearest: ближайшая к самой себе — должна быть сама себя
    auto nn1 = pc.k_nearest(pc.points_[42], 1);
    check(nn1.size() == 1, "k_nearest(k=1) returns 1 result");
    check(nn1[0].first == 42, "k_nearest: closest to points_[42] is itself");
    check(nn1[0].second < 1e-20, "k_nearest: dist² to itself ≈ 0");

    // 9b. k_nearest: k=5, результаты отсортированы по расстоянию
    auto nn5 = pc.k_nearest(pc.points_[0], 5);
    check(nn5.size() == 5, "k_nearest(k=5) returns 5 results");
    for (int i = 0; i + 1 < 5; ++i)
        check(nn5[i].second <= nn5[i + 1].second + 1e-15, "k_nearest results sorted");

    // 9c. k_nearest: k > N — обрезается до size()
    auto nn_big = pc.k_nearest(pc.points_[0], N + 100);
    check(nn_big.size() == static_cast<std::size_t>(N), "k_nearest clips k to size()");

    // ── 10. radius_search ────────────────────────────────────────
    const double R = 3.0;   // облако в [-10,10]^3, радиус 3 — достаточно точек
    auto rr = pc.radius_search(pc.points_[42], R);

    // Все найденные точки действительно в радиусе R
    for (const auto& [idx, d2] : rr)
        check(d2 <= R * R + 1e-10, "radius_search: all results within radius");

    // points_[42] должна быть в своём же радиусе (расстояние 0)
    bool found_self = false;
    for (const auto& [idx, d2] : rr)
        if (idx == 42) { found_self = true; break; }
    check(found_self, "radius_search includes query point itself");

    // ── 11. Statistical Outlier Removal ─────────────────────────
    // Сфера: 5000 точек на единичной сфере + 500 шума в [-5,5]^3
    constexpr int N_SPHERE = 5000;
    constexpr int N_NOISE  = 500;

    std::normal_distribution<double> gauss(0.0, 1.0);
    std::uniform_real_distribution<double> noise_dist(-5.0, 5.0);

    PointCloud sphere;
    sphere.points_.resize(N_SPHERE + N_NOISE);
    for (int i = 0; i < N_SPHERE; ++i) {
        Vector3d p(gauss(rng), gauss(rng), gauss(rng));
        sphere.points_[i] = p.normalized();
    }
    for (int i = 0; i < N_NOISE; ++i) {
        sphere.points_[N_SPHERE + i] = { noise_dist(rng), noise_dist(rng), noise_dist(rng) };
    }
    check(sphere.size() == static_cast<std::size_t>(N_SPHERE + N_NOISE), "sphere+noise size");

    PointCloud filtered = sphere.statistical_outlier_removal(20, 2.0);
    check(filtered.size() >= 4500, "SOR: kept >= 4500 sphere points");
    check(filtered.size() < static_cast<std::size_t>(N_SPHERE + N_NOISE), "SOR: removed some noise");
    std::cout << "  SOR: " << sphere.size() << " -> " << filtered.size() << " points\n";

    // ── 12. Voxel Downsample ─────────────────────────────────────
    PointCloud vox_in;
    std::uniform_real_distribution<double> vox_dist(-10.0, 10.0);
    vox_in.points_.resize(1000);
    for (auto& p : vox_in.points_)
        p = { vox_dist(rng), vox_dist(rng), vox_dist(rng) };

    PointCloud vox_out = vox_in.voxel_downsample(1.0);
    check(!vox_out.empty(), "voxel_downsample: result non-empty");
    check(vox_out.size() <= vox_in.size(), "voxel_downsample: size reduced");
    std::cout << "  Voxel: " << vox_in.size() << " -> " << vox_out.size() << " points\n";

    // ── 13. Estimate Normals ─────────────────────────────────────
    PointCloud sphere_normals;
    sphere_normals.points_.resize(N_SPHERE);
    for (int i = 0; i < N_SPHERE; ++i) {
        Vector3d p(gauss(rng), gauss(rng), gauss(rng));
        sphere_normals.points_[i] = p.normalized();
    }

    sphere_normals.estimate_normals(30);
    check(sphere_normals.normals_.size() == static_cast<std::size_t>(N_SPHERE),
          "estimate_normals: normals count == N_SPHERE");

    int aligned = 0;
    for (int i = 0; i < N_SPHERE; ++i) {
        if (sphere_normals.normals_[i].dot(sphere_normals.points_[i]) > 0.5)
            ++aligned;
    }
    check(aligned >= N_SPHERE * 9 / 10, "estimate_normals: >= 90% normals outward");
    std::cout << "  Normals aligned: " << aligned << "/" << N_SPHERE << "\n";

    // ── 14. DBSCAN: segment_largest_cluster ─────────────────────
    // Большой шар: 2000 точек на единичной сфере (радиус 1, центр 0)
    // Малый шар:    500 точек на сфере радиуса 0.5, центр (5, 0, 0)
    // Шум:          200 случайных точек в [-2, 2]^3
    // eps=0.15, min_points=5 → два кластера + шум → largest = большой шар
    constexpr int N_BIG   = 2000;
    constexpr int N_SMALL =  500;
    constexpr int N_RAND  =  200;

    std::uniform_real_distribution<double> rand2(-2.0, 2.0);

    PointCloud two_spheres;
    two_spheres.points_.resize(N_BIG + N_SMALL + N_RAND);

    for (int i = 0; i < N_BIG; ++i) {
        Vector3d p(gauss(rng), gauss(rng), gauss(rng));
        two_spheres.points_[i] = p.normalized();          // единичная сфера
    }
    for (int i = 0; i < N_SMALL; ++i) {
        Vector3d p(gauss(rng), gauss(rng), gauss(rng));
        two_spheres.points_[N_BIG + i] = p.normalized() * 0.5 + Vector3d(5.0, 0.0, 0.0);
    }
    for (int i = 0; i < N_RAND; ++i) {
        two_spheres.points_[N_BIG + N_SMALL + i] = { rand2(rng), rand2(rng), rand2(rng) };
    }

    PointCloud largest = two_spheres.segment_largest_cluster(0.15, 5);

    // Большой шар должен быть найден целиком
    check(largest.size() >= 1800, "DBSCAN: largest cluster >= 1800 (big sphere)");
    // Малый шар не должен попасть в результат (он отдельный кластер)
    check(largest.size() < static_cast<std::size_t>(N_BIG + N_SMALL),
          "DBSCAN: largest cluster does not include small sphere");
    std::cout << "  DBSCAN: total=" << two_spheres.size()
              << " largest=" << largest.size() << " (expected ~" << N_BIG << ")\n";

    // ── Итог ─────────────────────────────────────────────────────
    std::filesystem::remove(tmp);

    std::cout << "All tests PASSED\n";
    std::cout << "  N = " << N << "  file = " << tmp.filename().string() << "\n";
    std::cout << "  BBox: ["
              << bb.min.transpose() << "] - ["
              << bb.max.transpose() << "]\n";
    std::cout << "  KNN(42, k=5): ";
    for (auto& [i, d2] : nn5) std::cout << i << "(d²=" << d2 << ") ";
    std::cout << "\n";
    std::cout << "  RadiusSearch(42, r=" << R << "): " << rr.size() << " points\n";
    return 0;
}
