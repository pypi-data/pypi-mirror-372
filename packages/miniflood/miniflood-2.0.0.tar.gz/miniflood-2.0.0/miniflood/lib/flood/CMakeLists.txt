# CMakeLists.txt

# -------------------------------
# 构建你的模块-一个目录下的源文件分为lib库和 pyd模块
# -------------------------------
set(BINDPYD flood)
set(SRCS bindings/binding.cpp)
set(LIB lib_flood)
set(LIB_SRCS flood_solver.cu)


add_library(${LIB} STATIC ${LIB_SRCS})
# 链接 json
target_link_libraries(${LIB} nlohmann_json::nlohmann_json)

add_library(${BINDPYD} MODULE ${SRCS})

target_link_libraries(${BINDPYD} ${LIB})
target_link_libraries(${BINDPYD} pybind11::module)

set_target_properties(${BINDPYD} PROPERTIES PREFIX "${PYTHON_MODULE_PREFIX}"
                                        SUFFIX "${PYTHON_MODULE_EXTENSION}")
#set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/release/bin)
#set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/release/lib)

install(
  TARGETS
    ${flood}
  LIBRARY
    DESTINATION ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/miniflow
  )
