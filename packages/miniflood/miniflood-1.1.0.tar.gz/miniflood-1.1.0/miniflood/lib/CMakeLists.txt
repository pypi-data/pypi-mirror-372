# CMakeLists.txt

# -------------------------------
# 构建你的模块
# -------------------------------
pybind11_add_module(flood bindings/binding.cpp flood_solver.cu)

# 链接 Python 和 json
target_link_libraries(flood PRIVATE pybind11::module nlohmann_json::nlohmann_json)

# 明确包含 Python 头文件（虽然 pybind11_add_module 通常会处理）
target_include_directories(flood PRIVATE ${Python3_INCLUDE_DIRS})

# 设置输出目录
set_target_properties(flood PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})
