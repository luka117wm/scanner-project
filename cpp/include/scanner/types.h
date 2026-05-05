#pragma once

// Eigen генерирует предупреждения C4127/C4714 на MSVC — глушим на время include
#ifdef _MSC_VER
#  pragma warning(push)
#  pragma warning(disable: 4127 4714)
#endif
#include <Eigen/Dense>
#ifdef _MSC_VER
#  pragma warning(pop)
#endif

#include <string>
#include <vector>
#include <cstdint>

using Vector3d = Eigen::Vector3d;
using Vector3i = Eigen::Vector3i;
using Matrix3d = Eigen::Matrix3d;

struct BoundingBox {
    Vector3d min = Vector3d::Zero();
    Vector3d max = Vector3d::Zero();

    Vector3d size()   const { return max - min; }
    Vector3d center() const { return (min + max) * 0.5; }
    bool     valid()  const { return (max.array() >= min.array()).all(); }
};

struct Color { uint8_t r, g, b; };

enum class LogLevel { DEBUG, INFO, WARNING, ERR };  // ERROR зарезервирован <windows.h>

inline void log(LogLevel level, const std::string& msg)
{
    // TODO: реализовать полноценный логгер (файл + консоль)
    (void)level;
    (void)msg;
}
