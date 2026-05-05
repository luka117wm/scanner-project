cmake_minimum_required(VERSION 3.16)
project(scanner LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Eigen3 REQUIRED)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)

set(SCANNER_SOURCES
    src/point_cloud.cpp
    src/triangle_mesh.cpp
    src/mesh_repair.cpp
    src/print_preparation.cpp
)

add_library(scanner_core STATIC ${SCANNER_SOURCES})

target_include_directories(scanner_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party
)

target_link_libraries(scanner_core PUBLIC Eigen3::Eigen)

if(MSVC)
    target_compile_options(scanner_core PRIVATE /utf-8 /EHsc /W3)
endif()

pybind11_add_module(_scanner_cpp python/bindings.cpp)
target_link_libraries(_scanner_cpp PRIVATE scanner_core Eigen3::Eigen)

if(MSVC)
    target_compile_options(_scanner_cpp PRIVATE /utf-8 /EHsc /W3)
endif()

enable_testing()

add_executable(test_point_cloud tests/test_point_cloud.cpp)
target_link_libraries(test_point_cloud PRIVATE scanner_core)
if(MSVC)
    target_compile_options(test_point_cloud PRIVATE /utf-8 /EHsc /W3)
endif()
add_test(NAME test_point_cloud COMMAND test_point_cloud)

add_executable(test_triangle_mesh tests/test_triangle_mesh.cpp)
target_link_libraries(test_triangle_mesh PRIVATE scanner_core)
if(MSVC)
    target_compile_options(test_triangle_mesh PRIVATE /utf-8 /EHsc /W3)
endif()
add_test(NAME test_triangle_mesh COMMAND test_triangle_mesh)

add_executable(test_mesh_repair tests/test_mesh_repair.cpp)
target_link_libraries(test_mesh_repair PRIVATE scanner_core)
if(MSVC)
    target_compile_options(test_mesh_repair PRIVATE /utf-8 /EHsc /W3)
endif()
add_test(NAME test_mesh_repair COMMAND test_mesh_repair)

add_executable(test_print_preparation tests/test_print_preparation.cpp)
target_link_libraries(test_print_preparation PRIVATE scanner_core)
if(MSVC)
    target_compile_options(test_print_preparation PRIVATE /utf-8 /EHsc /W3)
endif()
add_test(NAME test_print_preparation COMMAND test_print_preparation)

add_executable(demo_synthetic tests/demo_synthetic.cpp)
target_link_libraries(demo_synthetic PRIVATE scanner_core)
if(MSVC)
    target_compile_options(demo_synthetic PRIVATE /utf-8 /EHsc /W3)
endif()
