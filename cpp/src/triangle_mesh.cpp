#include "scanner/triangle_mesh.h"
#include "ply_io.h"

#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstring>
#include <fstream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>

namespace scanner {

// ============================================================
//  Вспомогательная функция: запись float32 в поток
// ============================================================

static void write_f32(std::ostream& out, double v) {
    float f = static_cast<float>(v);
    out.write(reinterpret_cast<const char*>(&f), 4);
}

// ============================================================
//  I/O — PLY
// ============================================================

bool TriangleMesh::load_ply(const std::filesystem::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;

    std::string line;
    std::getline(in, line);
    if (line != "ply" && line != "ply\r") return false;

    enum class Fmt { ASCII, BIN_LE, UNKNOWN } fmt = Fmt::UNKNOWN;

    struct ElemInfo {
        std::string            name;
        std::size_t            count = 0;
        std::vector<PropInfo>  props;
        bool                   has_list      = false;
        bool                   list_cnt_int4 = false; // true=int32 count, false=uint8
    };

    std::vector<ElemInfo> elems;
    ElemInfo*             cur = nullptr;

    while (std::getline(in, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line == "end_header") break;

        std::istringstream ss(line);
        std::string tok; ss >> tok;

        if (tok == "format") {
            std::string fmt_str; ss >> fmt_str;
            if (fmt_str == "ascii")                     fmt = Fmt::ASCII;
            else if (fmt_str == "binary_little_endian") fmt = Fmt::BIN_LE;
        } else if (tok == "element") {
            elems.emplace_back();
            cur = &elems.back();
            ss >> cur->name >> cur->count;
        } else if (tok == "property" && cur) {
            std::string type_str; ss >> type_str;
            if (type_str == "list") {
                cur->has_list = true;
                // "property list <count_type> <value_type> <name>"
                // count_type: uchar (1 byte) or int/uint (4 bytes)
                std::string cnt_type; ss >> cnt_type;
                cur->list_cnt_int4 = (cnt_type == "int" || cnt_type == "uint"
                                   || cnt_type == "int32" || cnt_type == "uint32");
            } else {
                std::string name_str; ss >> name_str;
                cur->props.push_back({name_str, str_to_proptype(type_str)});
            }
        }
    }

    if (fmt == Fmt::UNKNOWN) return false;

    vertices_.clear();
    faces_.clear();
    normals_.clear();
    colors_.clear();

    for (const auto& elem : elems) {
        // ---- Вершины ----
        if (elem.name == "vertex" && !elem.has_list) {
            auto fp = [&](const std::string& n) -> int {
                for (int i = 0; i < (int)elem.props.size(); ++i)
                    if (elem.props[i].name == n) return i;
                return -1;
            };
            int ix = fp("x"), iy = fp("y"), iz = fp("z");
            if (ix < 0 || iy < 0 || iz < 0) return false;
            int inx = fp("nx"), iny = fp("ny"), inz = fp("nz");
            int ir  = fp("red"),   ig = fp("green"), ib = fp("blue");
            if (ir < 0) { ir = fp("r"); ig = fp("g"); ib = fp("b"); }

            bool has_n = (inx >= 0 && iny >= 0 && inz >= 0);
            bool has_c = (ir  >= 0 && ig  >= 0 && ib  >= 0);
            vertices_.resize(elem.count);
            if (has_n) normals_.resize(elem.count);
            if (has_c) colors_ .resize(elem.count);

            for (std::size_t vi = 0; vi < elem.count; ++vi) {
                std::vector<double> vals(elem.props.size());
                if (fmt == Fmt::ASCII) {
                    std::getline(in, line);
                    if (!line.empty() && line.back() == '\r') line.pop_back();
                    std::istringstream ls(line);
                    for (auto& v : vals) ls >> v;
                } else {
                    for (std::size_t pi = 0; pi < elem.props.size(); ++pi)
                        vals[pi] = read_bin_double(in, elem.props[pi].type);
                }
                vertices_[vi] = { vals[ix], vals[iy], vals[iz] };
                if (has_n) normals_[vi] = { vals[inx], vals[iny], vals[inz] };
                if (has_c) colors_[vi]  = {
                    static_cast<uint8_t>(vals[ir]),
                    static_cast<uint8_t>(vals[ig]),
                    static_cast<uint8_t>(vals[ib])
                };
            }
        }

        // ---- Грани (list uchar int vertex_indices) ----
        else if (elem.name == "face" && elem.has_list) {
            faces_.reserve(elem.count);
            for (std::size_t fi = 0; fi < elem.count; ++fi) {
                if (fmt == Fmt::ASCII) {
                    std::getline(in, line);
                    if (!line.empty() && line.back() == '\r') line.pop_back();
                    std::istringstream ls(line);
                    int cnt; ls >> cnt;
                    if (cnt == 3) {
                        int a, b, c; ls >> a >> b >> c;
                        faces_.push_back({ a, b, c });
                    }
                } else {
                    // Count field: 1 byte (uchar) or 4 bytes (int/uint)
                    int32_t cnt = 0;
                    if (elem.list_cnt_int4) {
                        in.read(reinterpret_cast<char*>(&cnt), 4);
                    } else {
                        uint8_t c1 = 0;
                        in.read(reinterpret_cast<char*>(&c1), 1);
                        cnt = c1;
                    }
                    if (cnt == 3) {
                        int32_t a, b, c;
                        in.read(reinterpret_cast<char*>(&a), 4);
                        in.read(reinterpret_cast<char*>(&b), 4);
                        in.read(reinterpret_cast<char*>(&c), 4);
                        faces_.push_back({ a, b, c });
                    } else {
                        // Skip non-triangle (polygon with cnt vertices)
                        in.ignore(static_cast<std::streamsize>(cnt) * 4);
                    }
                }
            }
        }

        // ---- Неизвестный элемент без list — пропускаем побайтово ----
        else if (!elem.has_list && fmt != Fmt::ASCII) {
            std::size_t bytes_per_row = 0;
            for (const auto& p : elem.props) bytes_per_row += static_cast<std::size_t>(p.byte_size());
            in.ignore(static_cast<std::streamsize>(elem.count * bytes_per_row));
        }
    }

    return !vertices_.empty() && !faces_.empty();
}

bool TriangleMesh::save_ply(const std::filesystem::path& path) const {
    if (empty()) return false;
    std::ofstream out(path, std::ios::binary);
    if (!out) return false;

    bool write_normals = !normals_.empty();
    bool write_colors  = !colors_.empty();

    out << "ply\n"
        << "format binary_little_endian 1.0\n"
        << "comment scanner triangle mesh\n"
        << "element vertex " << vertices_.size() << "\n"
        << "property float x\nproperty float y\nproperty float z\n";
    if (write_normals)
        out << "property float nx\nproperty float ny\nproperty float nz\n";
    if (write_colors)
        out << "property uchar red\nproperty uchar green\nproperty uchar blue\n";
    out << "element face " << faces_.size() << "\n"
        << "property list uchar int vertex_indices\n"
        << "end_header\n";

    for (std::size_t i = 0; i < vertices_.size(); ++i) {
        write_f32(out, vertices_[i].x());
        write_f32(out, vertices_[i].y());
        write_f32(out, vertices_[i].z());
        if (write_normals) {
            write_f32(out, normals_[i].x());
            write_f32(out, normals_[i].y());
            write_f32(out, normals_[i].z());
        }
        if (write_colors) {
            out.write(reinterpret_cast<const char*>(&colors_[i].r), 1);
            out.write(reinterpret_cast<const char*>(&colors_[i].g), 1);
            out.write(reinterpret_cast<const char*>(&colors_[i].b), 1);
        }
    }

    for (const auto& f : faces_) {
        uint8_t cnt = 3;
        out.write(reinterpret_cast<const char*>(&cnt), 1);
        int32_t a = f[0], b = f[1], c = f[2];
        out.write(reinterpret_cast<const char*>(&a), 4);
        out.write(reinterpret_cast<const char*>(&b), 4);
        out.write(reinterpret_cast<const char*>(&c), 4);
    }
    return out.good();
}

// ============================================================
//  I/O — STL (binary)
// ============================================================

bool TriangleMesh::load_stl(const std::filesystem::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) return false;

    // 80-байтовый заголовок (пропускаем)
    char header[80] = {};
    in.read(header, 80);

    uint32_t n_tri = 0;
    in.read(reinterpret_cast<char*>(&n_tri), 4);
    if (!in || n_tri == 0) return false;

    // Дедупликация вершин: (float,float,float) → индекс
    // float32 сохраняется и читается точно, поэтому битовое совпадение гарантировано
    using Key = std::tuple<float, float, float>;
    struct KeyHash {
        std::size_t operator()(const Key& k) const {
            uint32_t a, b, c;
            std::memcpy(&a, &std::get<0>(k), 4);
            std::memcpy(&b, &std::get<1>(k), 4);
            std::memcpy(&c, &std::get<2>(k), 4);
            std::size_t h = 0;
            auto mix = [&](uint32_t v) { h ^= v + 0x9e3779b9u + (h << 6) + (h >> 2); };
            mix(a); mix(b); mix(c);
            return h;
        }
    };
    std::unordered_map<Key, int, KeyHash> vm;

    vertices_.clear();
    faces_.clear();
    normals_.clear();
    vertices_.reserve(n_tri * 3);   // с запасом, дедупликация сожмёт
    faces_  .reserve(n_tri);
    normals_.reserve(n_tri);

    auto get_or_add = [&](float x, float y, float z) -> int {
        Key k{x, y, z};
        auto it = vm.find(k);
        if (it != vm.end()) return it->second;
        int idx = static_cast<int>(vertices_.size());
        vertices_.push_back({ static_cast<double>(x),
                              static_cast<double>(y),
                              static_cast<double>(z) });
        vm[k] = idx;
        return idx;
    };

    for (uint32_t i = 0; i < n_tri; ++i) {
        float n[3], v[9];
        uint16_t attr;
        in.read(reinterpret_cast<char*>(n), 12);
        in.read(reinterpret_cast<char*>(v), 36);
        in.read(reinterpret_cast<char*>(&attr), 2);
        if (!in) return false;

        normals_.push_back({ static_cast<double>(n[0]),
                             static_cast<double>(n[1]),
                             static_cast<double>(n[2]) });
        int i0 = get_or_add(v[0], v[1], v[2]);
        int i1 = get_or_add(v[3], v[4], v[5]);
        int i2 = get_or_add(v[6], v[7], v[8]);
        faces_.push_back({ i0, i1, i2 });
    }
    return true;
}

bool TriangleMesh::save_stl(const std::filesystem::path& path) const {
    if (empty()) return false;
    std::ofstream out(path, std::ios::binary);
    if (!out) return false;

    // 80-байтовый заголовок
    char header[80] = {};
    const char label[] = "scanner mesh";
    std::memcpy(header, label, sizeof(label) - 1);
    out.write(header, 80);

    uint32_t n = static_cast<uint32_t>(faces_.size());
    out.write(reinterpret_cast<const char*>(&n), 4);

    bool has_normals = (normals_.size() == faces_.size());

    for (std::size_t i = 0; i < faces_.size(); ++i) {
        const Vector3d& v0 = vertices_[faces_[i][0]];
        const Vector3d& v1 = vertices_[faces_[i][1]];
        const Vector3d& v2 = vertices_[faces_[i][2]];

        Vector3d nrm;
        if (has_normals) {
            nrm = normals_[i];
        } else {
            nrm = (v1 - v0).cross(v2 - v0);
            double len = nrm.norm();
            if (len > 0.0) nrm /= len;
        }

        write_f32(out, nrm.x()); write_f32(out, nrm.y()); write_f32(out, nrm.z());
        write_f32(out, v0.x());  write_f32(out, v0.y());  write_f32(out, v0.z());
        write_f32(out, v1.x());  write_f32(out, v1.y());  write_f32(out, v1.z());
        write_f32(out, v2.x());  write_f32(out, v2.y());  write_f32(out, v2.z());
        uint16_t attr = 0;
        out.write(reinterpret_cast<const char*>(&attr), 2);
    }
    return out.good();
}

// ============================================================
//  I/O — OBJ (ASCII, только запись)
// ============================================================

bool TriangleMesh::save_obj(const std::filesystem::path& path) const {
    if (empty()) return false;
    std::ofstream out(path);
    if (!out) return false;

    out << "# scanner mesh\n";
    out << "# vertices: " << vertices_.size()
        << "  faces: "    << faces_.size() << "\n\n";

    for (const auto& v : vertices_)
        out << "v " << v.x() << " " << v.y() << " " << v.z() << "\n";

    bool has_normals = !normals_.empty();
    if (has_normals) {
        out << "\n";
        for (const auto& n : normals_)
            out << "vn " << n.x() << " " << n.y() << " " << n.z() << "\n";
    }

    out << "\n";
    if (has_normals && normals_.size() == faces_.size()) {
        // Одна нормаль на грань: f v1//n v2//n v3//n (1-индексация)
        for (std::size_t i = 0; i < faces_.size(); ++i) {
            int ni = static_cast<int>(i) + 1;
            out << "f " << faces_[i][0]+1 << "//" << ni
                << " "  << faces_[i][1]+1 << "//" << ni
                << " "  << faces_[i][2]+1 << "//" << ni << "\n";
        }
    } else {
        for (const auto& f : faces_)
            out << "f " << f[0]+1 << " " << f[1]+1 << " " << f[2]+1 << "\n";
    }
    return out.good();
}

// ============================================================
//  Геометрия
// ============================================================

BoundingBox TriangleMesh::bounding_box() const {
    BoundingBox bb;
    if (vertices_.empty()) return bb;
    bb.min = bb.max = vertices_[0];
    for (std::size_t i = 1; i < vertices_.size(); ++i) {
        bb.min = bb.min.cwiseMin(vertices_[i]);
        bb.max = bb.max.cwiseMax(vertices_[i]);
    }
    return bb;
}

void TriangleMesh::compute_normals() {
    normals_.resize(faces_.size());
    for (std::size_t i = 0; i < faces_.size(); ++i) {
        const Vector3d& v0 = vertices_[faces_[i][0]];
        const Vector3d& v1 = vertices_[faces_[i][1]];
        const Vector3d& v2 = vertices_[faces_[i][2]];
        Vector3d n = (v1 - v0).cross(v2 - v0);
        double len = n.norm();
        normals_[i] = (len > 0.0) ? Vector3d(n / len) : Vector3d::Zero();
    }
}

double TriangleMesh::surface_area() const {
    double area = 0.0;
    for (const auto& f : faces_) {
        const Vector3d& v0 = vertices_[f[0]];
        const Vector3d& v1 = vertices_[f[1]];
        const Vector3d& v2 = vertices_[f[2]];
        area += 0.5 * (v1 - v0).cross(v2 - v0).norm();
    }
    return area;
}

double TriangleMesh::volume() const {
    // Знаковый объём по теореме Гаусса: V = (1/6) Σ v0·(v1×v2)
    // Для замкнутой сетки с согласованным обходом вершин даёт ±объём.
    double vol = 0.0;
    for (const auto& f : faces_) {
        const Vector3d& v0 = vertices_[f[0]];
        const Vector3d& v1 = vertices_[f[1]];
        const Vector3d& v2 = vertices_[f[2]];
        vol += v0.dot(v1.cross(v2));
    }
    return std::abs(vol) / 6.0;
}

// ============================================================
//  Топология
// ============================================================

TriangleMesh::EdgeMap TriangleMesh::build_edge_map() const {
    EdgeMap em;
    for (int fi = 0; fi < static_cast<int>(faces_.size()); ++fi) {
        const auto& f = faces_[fi];
        for (int e = 0; e < 3; ++e) {
            int a = f[e], b = f[(e + 1) % 3];
            if (a > b) std::swap(a, b);
            em[{a, b}].push_back(fi);
        }
    }
    return em;
}

bool TriangleMesh::is_watertight() const {
    auto em = build_edge_map();
    for (const auto& [edge, faces] : em)
        if (faces.size() != 2) return false;
    return true;
}

std::vector<std::pair<int, int>> TriangleMesh::find_boundary_edges() const {
    auto em = build_edge_map();
    std::vector<std::pair<int, int>> result;
    for (const auto& [edge, faces] : em)
        if (faces.size() != 2) result.push_back(edge);
    return result;
}

std::vector<int> TriangleMesh::get_vertex_neighbors(int v) const {
    std::set<int> seen;
    for (const auto& f : faces_) {
        for (int e = 0; e < 3; ++e) {
            if (f[e] == v) {
                seen.insert(f[(e + 1) % 3]);
                seen.insert(f[(e + 2) % 3]);
            }
        }
    }
    return { seen.begin(), seen.end() };
}

} // namespace scanner
