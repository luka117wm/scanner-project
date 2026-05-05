#include "scanner/point_cloud.h"
#include "ply_io.h"

// nanoflann включается ТОЛЬКО здесь (PIMPL) — не светится в публичном заголовке
#ifdef _MSC_VER
#  pragma warning(push)
#  pragma warning(disable: 4127 4267 4305 4714)
#endif
#include "nanoflann/nanoflann.hpp"
#ifdef _MSC_VER
#  pragma warning(pop)
#endif

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstring>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>

namespace scanner {

// ============================================================
//  nanoflann — адаптер и тип KD-tree
// ============================================================

struct PointCloudAdaptor {
    const std::vector<Vector3d>& pts;
    explicit PointCloudAdaptor(const std::vector<Vector3d>& p) : pts(p) {}

    // nanoflann interface
    std::size_t kdtree_get_point_count() const { return pts.size(); }
    double      kdtree_get_pt(std::size_t idx, int dim) const { return pts[idx][dim]; }
    template<class BBOX>
    bool kdtree_get_bbox(BBOX&) const { return false; }
};

using KDTree3d = nanoflann::KDTreeSingleIndexAdaptor<
    nanoflann::L2_Simple_Adaptor<double, PointCloudAdaptor>,
    PointCloudAdaptor,
    3,           /*dims*/
    std::size_t  /*IndexType — совпадает с size_t в публичном API*/>;

struct PointCloudKDTreeImpl {
    PointCloudAdaptor adaptor;
    KDTree3d          tree;

    explicit PointCloudKDTreeImpl(const std::vector<Vector3d>& pts)
        : adaptor(pts)
        , tree(3, adaptor, nanoflann::KDTreeSingleIndexAdaptorParams(10 /*leaf_max*/))
    {
        tree.buildIndex();
    }
};

// PropType / PropInfo / str_to_proptype / read_bin_double — из ply_io.h

// ============================================================
//  Специальные члены (определены здесь — PointCloudKDTreeImpl полный)
// ============================================================

PointCloud::PointCloud()  = default;
PointCloud::~PointCloud() = default;

PointCloud::PointCloud(PointCloud&& o) noexcept
    : points_ (std::move(o.points_))
    , normals_(std::move(o.normals_))
    , colors_ (std::move(o.colors_))
    // KD-tree не переносим: adaptor хранит ссылку на вектор старого объекта
    , kdtree_ (nullptr)
{}

PointCloud& PointCloud::operator=(PointCloud&& o) noexcept {
    if (this != &o) {
        points_  = std::move(o.points_);
        normals_ = std::move(o.normals_);
        colors_  = std::move(o.colors_);
        kdtree_.reset();
    }
    return *this;
}

// ============================================================
//  I/O
// ============================================================

bool PointCloud::load_ply(const std::filesystem::path& path) {
    // Открываем в бинарном режиме — работает на Windows с любыми путями (C++17)
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;

    // --- Разбор заголовка (всегда ASCII) ---
    std::string line;
    std::getline(in, line);
    if (line != "ply" && line != "ply\r") return false;   // не PLY

    enum class Format { ASCII, BIN_LE, UNKNOWN } fmt = Format::UNKNOWN;
    std::size_t n_vertices = 0;
    bool in_vertex_element = false;
    std::vector<PropInfo> props;

    while (std::getline(in, line)) {
        // Убираем \r (Windows CRLF внутри файла)
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line == "end_header") break;

        std::istringstream ss(line);
        std::string token;
        ss >> token;

        if (token == "format") {
            std::string fmt_str; ss >> fmt_str;
            if (fmt_str == "ascii")                    fmt = Format::ASCII;
            else if (fmt_str == "binary_little_endian") fmt = Format::BIN_LE;
        } else if (token == "element") {
            std::string elem; ss >> elem;
            in_vertex_element = (elem == "vertex");
            if (in_vertex_element) ss >> n_vertices;
        } else if (token == "property" && in_vertex_element) {
            std::string type_str, name_str;
            ss >> type_str;
            if (type_str == "list") continue;   // грани — пропускаем
            ss >> name_str;
            props.push_back({name_str, str_to_proptype(type_str)});
        }
    }

    if (fmt == Format::UNKNOWN || n_vertices == 0) return false;

    // Индексы нужных свойств
    auto find_prop = [&](const std::string& n) -> int {
        for (int i = 0; i < static_cast<int>(props.size()); ++i)
            if (props[i].name == n) return i;
        return -1;
    };
    int ix = find_prop("x"), iy = find_prop("y"), iz = find_prop("z");
    if (ix < 0 || iy < 0 || iz < 0) return false;   // без XYZ не имеет смысла
    int inx = find_prop("nx"), iny = find_prop("ny"), inz = find_prop("nz");
    int ir  = find_prop("red"),   ig = find_prop("green"), ib = find_prop("blue");
    // Альтернативные имена цветов
    if (ir < 0) ir = find_prop("r");
    if (ig < 0) ig = find_prop("g");
    if (ib < 0) ib = find_prop("b");

    bool has_normals = (inx >= 0 && iny >= 0 && inz >= 0);
    bool has_colors  = (ir  >= 0 && ig  >= 0 && ib  >= 0);

    points_ .resize(n_vertices);
    normals_.resize(has_normals ? n_vertices : 0);
    colors_ .resize(has_colors  ? n_vertices : 0);

    // --- Чтение данных ---
    for (std::size_t vi = 0; vi < n_vertices; ++vi) {
        std::vector<double> vals(props.size());

        if (fmt == Format::ASCII) {
            std::getline(in, line);
            if (!line.empty() && line.back() == '\r') line.pop_back();
            std::istringstream ls(line);
            for (auto& v : vals) ls >> v;
        } else {   // BIN_LE
            for (std::size_t pi = 0; pi < props.size(); ++pi)
                vals[pi] = read_bin_double(in, props[pi].type);
        }

        points_[vi] = { vals[ix], vals[iy], vals[iz] };
        if (has_normals) normals_[vi] = { vals[inx], vals[iny], vals[inz] };
        if (has_colors)  colors_[vi]  = {
            static_cast<uint8_t>(vals[ir]),
            static_cast<uint8_t>(vals[ig]),
            static_cast<uint8_t>(vals[ib])
        };
    }
    return true;
}

bool PointCloud::save_ply(const std::filesystem::path& path) const {
    if (empty()) return false;

    std::ofstream out(path, std::ios::binary);
    if (!out) return false;

    bool write_normals = !normals_.empty();
    bool write_colors  = !colors_.empty();

    // --- ASCII заголовок ---
    out << "ply\n"
        << "format binary_little_endian 1.0\n"
        << "comment scanner point cloud\n"
        << "element vertex " << points_.size() << "\n"
        << "property float x\n"
        << "property float y\n"
        << "property float z\n";
    if (write_normals)
        out << "property float nx\n"
            << "property float ny\n"
            << "property float nz\n";
    if (write_colors)
        out << "property uchar red\n"
            << "property uchar green\n"
            << "property uchar blue\n";
    out << "end_header\n";

    // --- Бинарные данные (little-endian, родной порядок байт Windows/x86) ---
    for (std::size_t i = 0; i < points_.size(); ++i) {
        auto write_f32 = [&](double v) {
            float f = static_cast<float>(v);
            out.write(reinterpret_cast<const char*>(&f), 4);
        };
        write_f32(points_[i].x());
        write_f32(points_[i].y());
        write_f32(points_[i].z());
        if (write_normals) {
            write_f32(normals_[i].x());
            write_f32(normals_[i].y());
            write_f32(normals_[i].z());
        }
        if (write_colors) {
            out.write(reinterpret_cast<const char*>(&colors_[i].r), 1);
            out.write(reinterpret_cast<const char*>(&colors_[i].g), 1);
            out.write(reinterpret_cast<const char*>(&colors_[i].b), 1);
        }
    }
    return out.good();
}

// ============================================================
//  Геометрия
// ============================================================

BoundingBox PointCloud::bounding_box() const {
    BoundingBox bb;
    if (empty()) return bb;
    bb.min = bb.max = points_[0];
    for (std::size_t i = 1; i < points_.size(); ++i) {
        bb.min = bb.min.cwiseMin(points_[i]);
        bb.max = bb.max.cwiseMax(points_[i]);
    }
    return bb;
}

void PointCloud::center_to_origin() {
    if (empty()) return;
    const Vector3d shift = bounding_box().center();
    for (auto& p : points_) p -= shift;
    kdtree_.reset();   // после сдвига KD-tree недействителен
}

// ============================================================
//  KD-tree
// ============================================================

void PointCloud::ensure_kdtree() const {
    if (!kdtree_ && !empty())
        kdtree_ = std::make_unique<PointCloudKDTreeImpl>(points_);
}

void PointCloud::build_kdtree() {
    if (empty()) return;
    kdtree_ = std::make_unique<PointCloudKDTreeImpl>(points_);
}

std::vector<std::pair<std::size_t, double>>
PointCloud::k_nearest(const Vector3d& query, std::size_t k) const {
    ensure_kdtree();
    if (!kdtree_) return {};
    k = std::min(k, size());
    if (k == 0) return {};

    std::vector<std::size_t> indices(k);
    std::vector<double>      dists2(k);
    kdtree_->tree.knnSearch(query.data(), k, indices.data(), dists2.data());

    std::vector<std::pair<std::size_t, double>> result(k);
    for (std::size_t i = 0; i < k; ++i)
        result[i] = { indices[i], dists2[i] };
    return result;   // nanoflann уже возвращает в порядке возрастания расстояния
}

std::vector<std::pair<std::size_t, double>>
PointCloud::radius_search(const Vector3d& query, double radius) const {
    ensure_kdtree();
    if (!kdtree_) return {};

    // nanoflann::radiusSearch принимает квадрат радиуса
    std::vector<nanoflann::ResultItem<std::size_t, double>> matches;
    nanoflann::SearchParameters params;
    params.sorted = false;
    kdtree_->tree.radiusSearch(query.data(), radius * radius, matches, params);

    std::vector<std::pair<std::size_t, double>> result;
    result.reserve(matches.size());
    for (const auto& m : matches)
        result.push_back({ m.first, m.second });
    return result;
}

// ============================================================
//  Statistical Outlier Removal
// ============================================================

PointCloud PointCloud::statistical_outlier_removal(int k, double std_ratio) const {
    if (empty() || k <= 0) return {};
    ensure_kdtree();

    const std::size_t kk = static_cast<std::size_t>(std::min(k, static_cast<int>(size())));
    const std::size_t n  = size();

    // Для каждой точки — среднее расстояние до k ближайших соседей
    std::vector<double> mean_dists(n);
    for (std::size_t i = 0; i < n; ++i) {
        auto nn = k_nearest(points_[i], kk + 1);   // +1 — сама точка (d²=0)
        double sum = 0.0;
        int cnt = 0;
        for (const auto& [idx, d2] : nn) {
            if (idx == i) continue;   // пропускаем саму точку
            sum += std::sqrt(d2);
            ++cnt;
        }
        mean_dists[i] = (cnt > 0) ? sum / cnt : 0.0;
    }

    // Глобальное mean и stddev
    double global_mean = 0.0;
    for (double d : mean_dists) global_mean += d;
    global_mean /= static_cast<double>(n);

    double variance = 0.0;
    for (double d : mean_dists) {
        double diff = d - global_mean;
        variance += diff * diff;
    }
    double global_std = std::sqrt(variance / static_cast<double>(n));

    const double threshold = global_mean + std_ratio * global_std;

    // Копируем точки-инлаеры
    PointCloud out;
    bool has_n = !normals_.empty();
    bool has_c = !colors_.empty();

    for (std::size_t i = 0; i < n; ++i) {
        if (mean_dists[i] <= threshold) {
            out.points_.push_back(points_[i]);
            if (has_n) out.normals_.push_back(normals_[i]);
            if (has_c) out.colors_.push_back(colors_[i]);
        }
    }
    return out;
}

// ============================================================
//  Voxel Grid Downsampling
// ============================================================

PointCloud PointCloud::voxel_downsample(double voxel_size) const {
    if (empty() || voxel_size <= 0.0) return {};

    struct VoxelKey {
        int64_t i, j, k;
        bool operator==(const VoxelKey& o) const { return i==o.i && j==o.j && k==o.k; }
    };
    struct VoxelKeyHash {
        std::size_t operator()(const VoxelKey& key) const {
            // FNV-like mix
            std::size_t h = 2166136261u;
            auto mix = [&](int64_t v) {
                h ^= static_cast<std::size_t>(v);
                h *= 16777619u;
                h ^= static_cast<std::size_t>(v >> 32);
                h *= 16777619u;
            };
            mix(key.i); mix(key.j); mix(key.k);
            return h;
        }
    };

    struct VoxelData {
        Vector3d sum_pos   = Vector3d::Zero();
        Vector3d sum_norm  = Vector3d::Zero();
        double   sum_r = 0, sum_g = 0, sum_b = 0;
        int      count = 0;
    };

    bool has_n = !normals_.empty();
    bool has_c = !colors_.empty();

    std::unordered_map<VoxelKey, VoxelData, VoxelKeyHash> voxels;
    voxels.reserve(size());

    for (std::size_t i = 0; i < size(); ++i) {
        VoxelKey key {
            static_cast<int64_t>(std::floor(points_[i].x() / voxel_size)),
            static_cast<int64_t>(std::floor(points_[i].y() / voxel_size)),
            static_cast<int64_t>(std::floor(points_[i].z() / voxel_size))
        };
        auto& v = voxels[key];
        v.sum_pos += points_[i];
        if (has_n) v.sum_norm += normals_[i];
        if (has_c) {
            v.sum_r += colors_[i].r;
            v.sum_g += colors_[i].g;
            v.sum_b += colors_[i].b;
        }
        ++v.count;
    }

    PointCloud out;
    out.points_.reserve(voxels.size());
    if (has_n) out.normals_.reserve(voxels.size());
    if (has_c) out.colors_.reserve(voxels.size());

    for (const auto& [key, v] : voxels) {
        const double inv = 1.0 / v.count;
        out.points_.push_back(v.sum_pos * inv);
        if (has_n) {
            Vector3d n = v.sum_norm;
            if (n.squaredNorm() > 0.0) n.normalize();
            out.normals_.push_back(n);
        }
        if (has_c) {
            out.colors_.push_back({
                static_cast<uint8_t>(std::round(v.sum_r * inv)),
                static_cast<uint8_t>(std::round(v.sum_g * inv)),
                static_cast<uint8_t>(std::round(v.sum_b * inv))
            });
        }
    }
    return out;
}

// ============================================================
//  Estimate Normals (PCA, k ближайших соседей)
// ============================================================

void PointCloud::estimate_normals(int k) {
    if (empty() || k <= 0) return;
    ensure_kdtree();

    const std::size_t kk = static_cast<std::size_t>(std::min(k, static_cast<int>(size())));

    // Центр масс для ориентации нормалей
    Vector3d com = Vector3d::Zero();
    for (const auto& p : points_) com += p;
    com /= static_cast<double>(size());

    normals_.resize(size());

    for (std::size_t i = 0; i < size(); ++i) {
        auto nn = k_nearest(points_[i], kk);

        // Центроид окрестности
        Vector3d centroid = Vector3d::Zero();
        for (const auto& [idx, d2] : nn) centroid += points_[idx];
        centroid /= static_cast<double>(nn.size());

        // Ковариационная матрица
        Matrix3d cov = Matrix3d::Zero();
        for (const auto& [idx, d2] : nn) {
            Vector3d d = points_[idx] - centroid;
            cov += d * d.transpose();
        }

        // Собственные векторы — нормаль = вектор с наименьшим с.з.
        Eigen::SelfAdjointEigenSolver<Matrix3d> solver(cov);
        Vector3d normal = solver.eigenvectors().col(0);   // наименьшее с.з.

        // Ориентация: нормаль должна смотреть от центра масс
        if (normal.dot(points_[i] - com) < 0.0)
            normal = -normal;

        normals_[i] = normal;
    }
}

// ============================================================
//  DBSCAN — segment_largest_cluster
// ============================================================

PointCloud PointCloud::segment_largest_cluster(double eps, int min_points,
                                                double min_cluster_fraction) const {
    if (empty() || eps <= 0.0 || min_points <= 0) return {};
    ensure_kdtree();

    const std::size_t n = size();
    // -1 = не посещена, -2 = шум, >= 0 = id кластера
    std::vector<int> labels(n, -1);
    int n_clusters = 0;

    for (std::size_t i = 0; i < n; ++i) {
        if (labels[i] != -1) continue;

        auto nbrs = radius_search(points_[i], eps);

        if (static_cast<int>(nbrs.size()) < min_points) {
            labels[i] = -2;   // шум
            continue;
        }

        const int cid = n_clusters++;
        labels[i] = cid;

        // BFS-очередь: добавляем соседей, сразу помечая кластером
        std::vector<std::size_t> queue;
        queue.reserve(nbrs.size());
        for (const auto& [idx, d2] : nbrs) {
            if (labels[idx] == -1) {
                labels[idx] = cid;
                queue.push_back(idx);
            } else if (labels[idx] == -2) {
                labels[idx] = cid;   // шум поглощается кластером
            }
        }

        for (std::size_t qi = 0; qi < queue.size(); ++qi) {
            auto q_nbrs = radius_search(points_[queue[qi]], eps);
            if (static_cast<int>(q_nbrs.size()) < min_points) continue;  // граничная точка

            for (const auto& [nidx, d2] : q_nbrs) {
                if (labels[nidx] == -1) {
                    labels[nidx] = cid;
                    queue.push_back(nidx);
                } else if (labels[nidx] == -2) {
                    labels[nidx] = cid;
                }
            }
        }
    }

    if (n_clusters == 0) return {};

    // Размеры кластеров
    std::vector<std::size_t> sizes(n_clusters, 0);
    for (int l : labels)
        if (l >= 0) ++sizes[static_cast<std::size_t>(l)];

    const int best_idx = static_cast<int>(
        std::max_element(sizes.begin(), sizes.end()) - sizes.begin());
    const std::size_t best_size = sizes[best_idx];

    // Принимаем наибольший кластер + все, чей размер >= fraction * best_size.
    // min_cluster_fraction <= 0 → только наибольший кластер (старое поведение).
    const std::size_t min_size = (min_cluster_fraction > 0.0)
        ? static_cast<std::size_t>(best_size * min_cluster_fraction)
        : best_size;  // только best

    std::vector<bool> accept(n_clusters, false);
    std::size_t total_accept = 0;
    for (int ci = 0; ci < n_clusters; ++ci) {
        if (sizes[ci] >= min_size) {
            accept[ci] = true;
            total_accept += sizes[ci];
        }
    }

    PointCloud out;
    bool has_n = !normals_.empty();
    bool has_c = !colors_.empty();
    out.points_.reserve(total_accept);
    if (has_n) out.normals_.reserve(total_accept);
    if (has_c) out.colors_.reserve(total_accept);

    for (std::size_t i = 0; i < n; ++i) {
        if (labels[i] >= 0 && accept[static_cast<std::size_t>(labels[i])]) {
            out.points_.push_back(points_[i]);
            if (has_n) out.normals_.push_back(normals_[i]);
            if (has_c) out.colors_.push_back(colors_[i]);
        }
    }
    return out;
}

} // namespace scanner
