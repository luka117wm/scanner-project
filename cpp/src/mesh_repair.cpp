#include "scanner/mesh_repair.h"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <set>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace scanner {

// ============================================================
//  remove_degenerate_faces
// ============================================================

int MeshRepair::remove_degenerate_faces() {
    constexpr double AREA2_EPS = 1e-24;
    int removed = 0;
    std::vector<Vector3i> ok;
    ok.reserve(mesh_.faces_.size());

    for (const auto& f : mesh_.faces_) {
        if (f[0] == f[1] || f[1] == f[2] || f[0] == f[2]) { ++removed; continue; }
        const Vector3d& v0 = mesh_.vertices_[f[0]];
        const Vector3d& v1 = mesh_.vertices_[f[1]];
        const Vector3d& v2 = mesh_.vertices_[f[2]];
        if ((v1-v0).cross(v2-v0).squaredNorm() < AREA2_EPS) { ++removed; continue; }
        ok.push_back(f);
    }

    mesh_.faces_ = std::move(ok);
    if (removed && !mesh_.normals_.empty()) mesh_.normals_.clear();
    return removed;
}

// ============================================================
//  remove_duplicate_faces
// ============================================================

int MeshRepair::remove_duplicate_faces() {
    using Key = std::tuple<int,int,int>;
    std::set<Key> seen;
    int removed = 0;
    std::vector<Vector3i> ok;
    ok.reserve(mesh_.faces_.size());

    for (const auto& f : mesh_.faces_) {
        int a = f[0], b = f[1], c = f[2];
        if (a > b) std::swap(a, b);
        if (b > c) std::swap(b, c);
        if (a > b) std::swap(a, b);
        if (seen.insert(Key{a, b, c}).second) ok.push_back(f);
        else ++removed;
    }

    mesh_.faces_ = std::move(ok);
    return removed;
}

// ============================================================
//  merge_close_vertices  (union-find + x-сортировка)
// ============================================================

int MeshRepair::merge_close_vertices(double threshold) {
    const int n = static_cast<int>(mesh_.vertices_.size());
    if (n == 0) return 0;

    std::vector<int> order(n);
    std::iota(order.begin(), order.end(), 0);
    std::sort(order.begin(), order.end(), [&](int a, int b) {
        return mesh_.vertices_[a].x() < mesh_.vertices_[b].x();
    });

    std::vector<int> parent(n);
    std::iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    };

    int merged = 0;
    for (int i = 0; i < n; ++i) {
        for (int j = i + 1; j < n; ++j) {
            if (mesh_.vertices_[order[j]].x() - mesh_.vertices_[order[i]].x() > threshold)
                break;
            if ((mesh_.vertices_[order[i]] - mesh_.vertices_[order[j]]).norm() <= threshold) {
                int ri = find(order[i]), rj = find(order[j]);
                if (ri != rj) { parent[ri] = rj; ++merged; }
            }
        }
    }

    if (merged == 0) return 0;

    std::vector<int>      new_idx(n, -1);
    std::vector<Vector3d> new_verts;
    bool                  has_c = !mesh_.colors_.empty();
    std::vector<Color>    new_colors;

    for (int i = 0; i < n; ++i) {
        int root = find(i);
        if (new_idx[root] == -1) {
            new_idx[root] = static_cast<int>(new_verts.size());
            new_verts.push_back(mesh_.vertices_[root]);
            if (has_c) new_colors.push_back(mesh_.colors_[root]);
        }
        new_idx[i] = new_idx[root];
    }

    for (auto& f : mesh_.faces_) {
        f[0] = new_idx[f[0]];
        f[1] = new_idx[f[1]];
        f[2] = new_idx[f[2]];
    }

    mesh_.vertices_ = std::move(new_verts);
    if (has_c) mesh_.colors_ = std::move(new_colors);
    mesh_.normals_.clear();
    return merged;
}

// ============================================================
//  make_manifold
// ============================================================

int MeshRepair::make_manifold() {
    auto em = mesh_.build_edge_map();

    std::set<std::pair<int,int>> bad;
    for (const auto& [edge, faces] : em)
        if (faces.size() > 2) bad.insert(edge);

    if (bad.empty()) return 0;

    int removed = 0;
    std::vector<Vector3i> ok;
    ok.reserve(mesh_.faces_.size());

    for (const auto& f : mesh_.faces_) {
        bool is_bad = false;
        for (int e = 0; e < 3 && !is_bad; ++e) {
            int a = f[e], b = f[(e+1)%3];
            if (a > b) std::swap(a, b);
            is_bad = bad.count({a, b}) > 0;
        }
        if (!is_bad) ok.push_back(f);
        else ++removed;
    }

    mesh_.faces_ = std::move(ok);
    if (removed) mesh_.normals_.clear();
    return removed;
}

// ============================================================
//  fill_holes  (трассировка граничных полурёбер → фановая триангуляция)
// ============================================================

int MeshRepair::fill_holes(int max_hole_edges) {
    if (mesh_.faces_.empty()) return 0;

    const int64_t N = static_cast<int64_t>(mesh_.vertices_.size());

    // Набор всех направленных рёбер из граней
    std::unordered_set<int64_t> de_set;
    de_set.reserve(mesh_.faces_.size() * 3);
    for (const auto& f : mesh_.faces_) {
        de_set.insert(static_cast<int64_t>(f[0]) * N + f[1]);
        de_set.insert(static_cast<int64_t>(f[1]) * N + f[2]);
        de_set.insert(static_cast<int64_t>(f[2]) * N + f[0]);
    }

    // Для каждого ребра (a→b) в грани, у которого нет обратного (b→a):
    // Отсутствующее ребро — это (b→a).  Граничный контур идёт по отсутствующим рёбрам,
    // т.е. boundary_next[b] = a ("из b следующий шаг — a").
    std::unordered_map<int,int> boundary_next;
    for (int64_t de : de_set) {
        int a = static_cast<int>(de / N);
        int b = static_cast<int>(de % N);
        if (!de_set.count(static_cast<int64_t>(b) * N + a))
            boundary_next.emplace(b, a);   // emplace игнорирует дублирование (non-manifold)
    }

    if (boundary_next.empty()) return 0;

    // Трассируем граничные петли
    std::vector<std::vector<int>> loops;
    std::unordered_set<int> visited;

    for (const auto& [start, ignored] : boundary_next) {
        if (visited.count(start)) continue;

        std::vector<int> loop;
        int cur = start;
        while (!visited.count(cur)) {
            auto it = boundary_next.find(cur);
            if (it == boundary_next.end()) { loop.clear(); break; }
            visited.insert(cur);
            loop.push_back(cur);
            cur = it->second;
            if (cur == start) break;
        }

        if (!loop.empty() && cur == start
                && static_cast<int>(loop.size()) <= max_hole_edges)
            loops.push_back(std::move(loop));
    }

    // Заполняем фановой триангуляцией: все треугольники от loop[0]
    int filled = 0;
    for (const auto& loop : loops) {
        for (int i = 1; i + 1 < static_cast<int>(loop.size()); ++i)
            mesh_.faces_.push_back({ loop[0], loop[i], loop[i+1] });
        ++filled;
    }

    if (filled) mesh_.normals_.clear();
    return filled;
}

// ============================================================
//  laplacian_smooth
// ============================================================

void MeshRepair::laplacian_smooth(int iterations, double lambda) {
    const int N = static_cast<int>(mesh_.vertices_.size());
    if (N == 0 || mesh_.faces_.empty() || iterations <= 0) return;

    // Список рёберных соседей
    std::vector<std::vector<int>> adj(N);
    for (const auto& f : mesh_.faces_) {
        for (int e = 0; e < 3; ++e) {
            int a = f[e], b = f[(e+1)%3];
            adj[a].push_back(b);
            adj[b].push_back(a);
        }
    }
    for (auto& nbrs : adj) {
        std::sort(nbrs.begin(), nbrs.end());
        nbrs.erase(std::unique(nbrs.begin(), nbrs.end()), nbrs.end());
    }

    // Граничные вершины (не двигаем)
    const int64_t Nl = static_cast<int64_t>(N);
    std::unordered_set<int64_t> de_set;
    de_set.reserve(mesh_.faces_.size() * 3);
    for (const auto& f : mesh_.faces_) {
        de_set.insert(static_cast<int64_t>(f[0]) * Nl + f[1]);
        de_set.insert(static_cast<int64_t>(f[1]) * Nl + f[2]);
        de_set.insert(static_cast<int64_t>(f[2]) * Nl + f[0]);
    }
    std::unordered_set<int> bnd;
    for (int64_t de : de_set) {
        int a = static_cast<int>(de / Nl), b = static_cast<int>(de % Nl);
        if (!de_set.count(static_cast<int64_t>(b) * Nl + a))
            { bnd.insert(a); bnd.insert(b); }
    }

    for (int it = 0; it < iterations; ++it) {
        std::vector<Vector3d> next = mesh_.vertices_;
        for (int v = 0; v < N; ++v) {
            if (bnd.count(v) || adj[v].empty()) continue;
            Vector3d cen = Vector3d::Zero();
            for (int nb : adj[v]) cen += mesh_.vertices_[nb];
            cen /= static_cast<double>(adj[v].size());
            next[v] = mesh_.vertices_[v] + lambda * (cen - mesh_.vertices_[v]);
        }
        mesh_.vertices_ = std::move(next);
    }

    mesh_.normals_.clear();
}

// ============================================================
//  repair_all
// ============================================================

RepairReport MeshRepair::repair_all(int smooth_iterations, int max_hole_edges) {
    RepairReport r;
    r.degenerate_removed   = remove_degenerate_faces();
    r.duplicate_removed    = remove_duplicate_faces();
    r.vertices_merged      = merge_close_vertices(1e-6);
    r.degenerate_removed  += remove_degenerate_faces();   // второй проход после слияния
    r.non_manifold_removed = make_manifold();
    r.holes_filled         = fill_holes(max_hole_edges);
    if (smooth_iterations > 0) {
        laplacian_smooth(smooth_iterations, 0.5);
        r.smooth_iterations = smooth_iterations;
    }
    return r;
}

} // namespace scanner
