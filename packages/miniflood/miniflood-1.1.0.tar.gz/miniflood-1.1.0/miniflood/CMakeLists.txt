# CMakeLists.txt

# 查找 Python
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)

# 启用 CUDA
enable_language(CUDA)

# -------------------------------
# 使用 FetchContent 引入 pybind11
# -------------------------------
include(FetchContent)

# --- 引入 pybind11 ---
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.12.0
)

FetchContent_GetProperties(pybind11)
if(NOT pybind11_POPULATED)
  FetchContent_Populate(pybind11)
  add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

# -------------------------------
# 本地引入 nlohmann/json
# -------------------------------

# 设置本地路径（可根据实际情况调整）
set(NLOHMANN_JSON_ROOT "${CMAKE_SOURCE_DIR}/third_party/nlohmann_json")

# 检查头文件是否存在
if(NOT EXISTS "${NLOHMANN_JSON_ROOT}/include/nlohmann/json.hpp")
  message(FATAL_ERROR "nlohmann/json.hpp not found at ${NLOHMANN_JSON_ROOT}/include/nlohmann/json.hpp. Please check the path or download the library.")
endif()

# 创建 INTERFACE 库
add_library(nlohmann_json INTERFACE)

# 设置 include 目录
target_include_directories(nlohmann_json INTERFACE
  "${NLOHMANN_JSON_ROOT}/include"
)

# 创建别名
add_library(nlohmann_json::nlohmann_json ALIAS nlohmann_json)

# 设置所需 C++ 标准
target_compile_features(nlohmann_json INTERFACE cxx_std_11)

add_subdirectory(lib)