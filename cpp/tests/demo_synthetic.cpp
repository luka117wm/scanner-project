#include "scanner/point_cloud.h"

#include <chrono>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <random>

using namespace scanner;
namespace fs = std::filesystem;

static double now_ms() {
    using clk = std::chrono::high_resolution_clock;
    return std::chrono::duration<double, std::milli>(
               clk::now().time_since_epoch()).count();
}

// Метка времени начала шага и вывод результата
struct Step {
    const char* name;
    double      t0;
    Step(const char* n) : name(n), t0(now_ms()) {}
    void done(const std::string& info) const {
        std::cout << "  " << name << "  " << info
                  << "  [" << (now_ms() - t0) << " ms]\n";
    }
};

int main(int argc, char* argv[]) {
    fs::path out_dir = (argc > 1) ? fs::path(argv[1])
                                  : fs::path(__FILE__).parent_path().parent_path()
                                        .parent_path() / "experiments" / "results";
    fs::create_directories(out_dir);

    const fs::path synthetic_path = out_dir / "synthetic.ply";
    const fs::path cleaned_path   = out_dir / "cleaned.ply";

    // Параметры тора
    constexpr int    N_TORUS = 30000;
    constexpr int    N_NOISE =  5000;
    constexpr double R       =  2.0;    // большой радиус
    constexpr double r_      =  0.8;    // малый радиус
    constexpr double PI2     =  6.283185307179586;

    std::cout << "=== Synthetic Pipeline Demo ===\n";
    std::cout << "  Torus: N=" << N_TORUS
              << "  R=" << R << "  r=" << r_ << "\n";
    std::cout << "  Noise: " << N_NOISE << " random outliers\n";
    std::cout << "  Output: " << out_dir.string() << "\n\n";

    // ── Шаг 1: Генерация тора + шума ────────────────────────────
    {
        Step s("[ 1 ] Generate  ");
        std::mt19937 rng(42);
        std::uniform_real_distribution<double> angle(0.0, PI2);
        const double box = R + r_ + 0.5;
        std::uniform_real_distribution<double> noise_d(-box, box);

        PointCloud pc;
        pc.points_.reserve(N_TORUS + N_NOISE);
        pc.colors_ .reserve(N_TORUS + N_NOISE);

        for (int i = 0; i < N_TORUS; ++i) {
            const double u = angle(rng), v = angle(rng);
            pc.points_.push_back({
                (R + r_ * std::cos(v)) * std::cos(u),
                (R + r_ * std::cos(v)) * std::sin(u),
                r_ * std::sin(v)
            });
            pc.colors_.push_back({100, 149, 237});   // синий — тор
        }
        for (int i = 0; i < N_NOISE; ++i) {
            pc.points_.push_back({ noise_d(rng), noise_d(rng), noise_d(rng) });
            pc.colors_.push_back({220, 80, 80});     // красный — шум
        }

        s.done(std::to_string(pc.size()) + " pts");

        // ── Шаг 2: Запись PLY ────────────────────────────────────
        {
            Step s2("[ 2 ] Save PLY  ");
            if (!pc.save_ply(synthetic_path)) {
                std::cerr << "FAIL: save_ply\n"; return 1;
            }
            s2.done(std::to_string(fs::file_size(synthetic_path) / 1024) + " KB  -> "
                    + synthetic_path.filename().string());
        }
    }

    // ── Шаг 3: Загрузка PLY ─────────────────────────────────────
    PointCloud pc;
    {
        Step s("[ 3 ] Load PLY  ");
        if (!pc.load_ply(synthetic_path)) {
            std::cerr << "FAIL: load_ply\n"; return 1;
        }
        s.done(std::to_string(pc.size()) + " pts");
    }

    // ── Шаг 4: Statistical Outlier Removal ──────────────────────
    PointCloud sor_pc;
    {
        Step s("[ 4 ] SOR(k=20, ratio=2.0)  ");
        sor_pc = pc.statistical_outlier_removal(20, 2.0);
        const int removed = static_cast<int>(pc.size())
                          - static_cast<int>(sor_pc.size());
        s.done(std::to_string(pc.size()) + " -> " + std::to_string(sor_pc.size())
               + "  (-" + std::to_string(removed) + " outliers)");
    }

    // ── Шаг 5: DBSCAN — выбрать наибольший кластер ──────────────
    PointCloud cluster;
    {
        Step s("[ 5 ] DBSCAN(eps=0.08, min=5)  ");
        cluster = sor_pc.segment_largest_cluster(0.08, 5);
        const int discarded = static_cast<int>(sor_pc.size())
                            - static_cast<int>(cluster.size());
        s.done(std::to_string(sor_pc.size()) + " -> " + std::to_string(cluster.size())
               + "  (-" + std::to_string(discarded) + " noise)");
    }

    // ── Шаг 6: Оценка нормалей (PCA) ────────────────────────────
    {
        Step s("[ 6 ] estimate_normals(k=20)  ");
        cluster.estimate_normals(20);
        s.done(std::to_string(cluster.normals_.size()) + " normals");
    }

    // ── Шаг 7: Сохранить cleaned.ply ────────────────────────────
    {
        Step s("[ 7 ] Save cleaned.ply  ");
        if (!cluster.save_ply(cleaned_path)) {
            std::cerr << "FAIL: save cleaned.ply\n"; return 1;
        }
        s.done(std::to_string(fs::file_size(cleaned_path) / 1024) + " KB  -> "
               + cleaned_path.filename().string());
    }

    // ── Итог ────────────────────────────────────────────────────
    const BoundingBox bb = cluster.bounding_box();
    std::cout << "\n=== Summary ===\n";
    std::cout << "  Input points   : " << (N_TORUS + N_NOISE) << "\n";
    std::cout << "  Cleaned points : " << cluster.size() << "\n";
    std::cout << "  Kept           : "
              << (100.0 * cluster.size() / N_TORUS) << "% of torus\n";
    std::cout << "  BBox min       : " << bb.min.transpose() << "\n";
    std::cout << "  BBox max       : " << bb.max.transpose() << "\n";
    std::cout << "  Normals        : "
              << (cluster.normals_.empty() ? "none" : "yes") << "\n";
    return 0;
}
