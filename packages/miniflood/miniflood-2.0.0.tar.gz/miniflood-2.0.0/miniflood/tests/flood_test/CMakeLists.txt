# CMakeLists.txt
# --- 查找源文件 ---
# 假设你的主源文件在当前目录，例如 main.cpp
# 你可以明确列出，或者使用 glob
file(GLOB SOURCES "*.cpp") # 查找当前目录下的所有 .cpp 文件
# --- 创建可执行文件 ---
set(APP_NAME "flood_test")
add_executable(${APP_NAME} ${SOURCES})

# --- 添加头文件搜索路径 ---
# 将项目根目录下的 src 目录添加为头文件包含路径
# 这样在代码中 #include "flood/xxx.h" 才能正确找到
include_directories(../../lib/flood)


# 方法二：直接使用 target_link_libraries 指定完整路径 (更推荐，避免依赖 link_directories)
# 如果你知道库文件的完整名称（包括路径），可以直接指定：
#  target_link_libraries(${APP_NAME} PRIVATE ${CMAKE_BINARY_DIR}/miniflood/lib/flood/Debug/lib_flood.lib)
  target_link_libraries(${APP_NAME} lib_flood)
# 或者 (Linux/macOS)
# target_link_libraries(${APP_NAME} PRIVATE ${CMAKE_BUILD_DIR}/lib/libflood.a)

# --- 可选：设置输出目录 ---
# 将生成的可执行文件放在 build/bin 目录下
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)

# --- 可选：设置库搜索路径 (如果库有依赖的 DLL 或 .so) ---
# set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
# set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin) # Windows 下 DLL, 可执行文件
