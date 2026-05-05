#pragma once
// Вспомогательные типы и функции для чтения/записи PLY — общие для point_cloud.cpp и triangle_mesh.cpp
#include <cstdint>
#include <istream>
#include <string>

enum class PropType { F32, F64, U8, I8, U16, I16, U32, I32, SKIP };

struct PropInfo {
    std::string name;
    PropType    type = PropType::F32;

    int byte_size() const {
        switch (type) {
            case PropType::F32: case PropType::U32: case PropType::I32: return 4;
            case PropType::F64:                                          return 8;
            case PropType::U8:  case PropType::I8:                      return 1;
            case PropType::U16: case PropType::I16:                     return 2;
            default:                                                     return 0;
        }
    }
};

inline PropType str_to_proptype(const std::string& s) {
    if (s == "float"  || s == "float32") return PropType::F32;
    if (s == "double" || s == "float64") return PropType::F64;
    if (s == "uchar"  || s == "uint8")   return PropType::U8;
    if (s == "char"   || s == "int8")    return PropType::I8;
    if (s == "ushort" || s == "uint16")  return PropType::U16;
    if (s == "short"  || s == "int16")   return PropType::I16;
    if (s == "uint"   || s == "uint32")  return PropType::U32;
    if (s == "int"    || s == "int32")   return PropType::I32;
    return PropType::SKIP;
}

// Читает одно скалярное значение из бинарного потока и возвращает его как double
inline double read_bin_double(std::istream& in, PropType type) {
    switch (type) {
        case PropType::F32: { float    v{}; in.read(reinterpret_cast<char*>(&v), 4); return static_cast<double>(v); }
        case PropType::F64: { double   v{}; in.read(reinterpret_cast<char*>(&v), 8); return v; }
        case PropType::U8:  { uint8_t  v{}; in.read(reinterpret_cast<char*>(&v), 1); return static_cast<double>(v); }
        case PropType::I8:  { int8_t   v{}; in.read(reinterpret_cast<char*>(&v), 1); return static_cast<double>(v); }
        case PropType::U16: { uint16_t v{}; in.read(reinterpret_cast<char*>(&v), 2); return static_cast<double>(v); }
        case PropType::I16: { int16_t  v{}; in.read(reinterpret_cast<char*>(&v), 2); return static_cast<double>(v); }
        case PropType::U32: { uint32_t v{}; in.read(reinterpret_cast<char*>(&v), 4); return static_cast<double>(v); }
        case PropType::I32: { int32_t  v{}; in.read(reinterpret_cast<char*>(&v), 4); return static_cast<double>(v); }
        default:             return 0.0;
    }
}
