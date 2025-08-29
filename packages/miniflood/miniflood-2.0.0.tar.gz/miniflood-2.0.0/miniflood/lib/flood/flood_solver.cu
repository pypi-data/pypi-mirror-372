// src/flood_solver.cu
#include "flood_solver.h"
#include <cmath>
#include <fstream>
#include <filesystem>
#include <iostream>
#include <vector>
#include <cuda_runtime.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

#ifdef _WIN32
    #include <windows.h>
    #include <direct.h>
    #include <io.h>
    #define ACCESS _access
    #define RMDIR _rmdir
    #define IS_DIR_SEP(c) ((c) == '\\' || (c) == '/')
    #define MKDIR_ERROR -1      // _mkdir 返回 0 表示成功
#else
    #include <sys/stat.h>
    #include <dirent.h>
    #include <unistd.h>
    #define ACCESS access
    #define RMDIR rmdir
    #define IS_DIR_SEP(c) ((c) == '/')
    #define _unlink unlink
    #define _remove remove
    #define MKDIR_ERROR -1     // mkdir 返回 -1 表示失败
#endif

/**
 * @brief 检查路径是否存在
 */
bool path_exists(const std::string& path) {
    return ACCESS(path.c_str(), 0) == 0;
}

/**
 * @brief 删除单个文件
 */
bool delete_file(const std::string& filepath) {
    return _unlink(filepath.c_str()) == 0;
}

#ifdef _WIN32

/**
 * @brief Windows: 递归删除目录（使用 WIN32_FIND_DATA）
 */
bool remove_directory_recursive(const std::string& path) {
    std::string search_path = path + "\\*";
    WIN32_FIND_DATAA fd;
    HANDLE hFind = FindFirstFileA(search_path.c_str(), &fd);

    if (hFind == INVALID_HANDLE_VALUE) {
        return false; // 目录不存在
    }

    do {
        std::string name = fd.cFileName;
        if (name == "." || name == "..") continue;

        std::string full_path = path + "\\" + name;

        if (fd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            // 是子目录，递归删除
            if (!remove_directory_recursive(full_path)) {
                FindClose(hFind);
                return false;
            }
        }
        else {
            // 是文件，直接删除
            if (!delete_file(full_path)) {
                FindClose(hFind);
                return false;
            }
        }
    } while (FindNextFileA(hFind, &fd));

    FindClose(hFind);

    // 最后删除自己
    return RMDIR(path.c_str()) == 0;
}

#else

/**
 * @brief Linux/macOS: 递归删除目录（使用 opendir）
 */
bool remove_directory_recursive(const std::string& path) {
    DIR* dir = opendir(path.c_str());
    if (!dir) return false;

    struct dirent* entry;
    while ((entry = readdir(dir)) != nullptr) {
        std::string name = entry->d_name;
        if (name == "." || name == "..") continue;

        std::string full_path = path + "/" + name;

        struct stat st;
        if (stat(full_path.c_str(), &st) != 0) continue;

        if (S_ISDIR(st.st_mode)) {
            // 子目录，递归删除
            if (!remove_directory_recursive(full_path)) {
                closedir(dir);
                return false;
            }
        }
        else {
            // 文件，删除
            if (unlink(full_path.c_str()) != 0) {
                closedir(dir);
                return false;
            }
        }
    }

    closedir(dir);

    // 删除自己
    return rmdir(path.c_str()) == 0;
}

#endif

/**
 * @brief 安全删除目录（推荐使用）
 * @param path 目录路径
 * @return true 成功，false 失败（如目录不存在或无权限）
 */
bool delete_directory(const std::string& path) {
    if (!path_exists(path)) {
        std::cout << "Directory not exists: " << path << std::endl;
        return true; // 可选：视为成功
    }

    return remove_directory_recursive(path);
}

/**
 * @brief 检查目录是否存在
 * @param dirname 目录路径
 * @return true 存在，false 不存在
 */
bool directory_exists(const char* dirname) {
    return ACCESS(dirname, 0) == 0;  // 0 表示存在
}

/**
 * @brief 创建单层目录（父目录必须存在）
 * @param dirname 目录路径
 * @return true 成功，false 失败
 */
bool create_directory(const char* dirname) {
    return mkdir(dirname) != MKDIR_ERROR;
}

/**
 * @brief 创建多级目录（推荐使用）
 * @param path 路径，如 "a/b/c"
 * @return true 成功，false 失败
 */
bool create_directories(const std::string& path) {
    std::string p = path;
    for (size_t i = 0; i < p.size(); ++i) {
        if (p[i] == '/' || p[i] == '\\') {
            p[i] = '\0';
            if (!directory_exists(p.c_str())) {
                if (!create_directory(p.c_str())) {
                    return false;
                }
            }
            p[i] = '/';
        }
    }
    // 创建最后一层
    if (!directory_exists(p.c_str())) {
        return create_directory(p.c_str());
    }
    return true;
}

// CUDA 核函数：简化扩散模型
__global__ void cuda_diffuse(float* h, float* zb, int nx, int ny, float dt, float dx, float dy) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    int idy = blockIdx.y * blockDim.y + threadIdx.y;
    int id = idy * nx + idx;

    if (idx >= nx || idy >= ny) return;

    float diffusion = 0.01;
    float laplacian = 0.0f;

    if (idx > 0)   laplacian += h[id - 1];
    if (idx < nx - 1) laplacian += h[id + 1];
    if (idy > 0)   laplacian += h[id - nx];
    if (idy < ny - 1) laplacian += h[id + nx];
    laplacian = (laplacian - 4 * h[id]) / (dx * dx);

    // 简化更新：dh/dt = diffusion * ∇²h
    h[id] += dt * diffusion * laplacian;

    // 不低于地形
    if (h[id] < 0.0f) h[id] = 0.0f;
}

// CUDA 核函数：填充数组为 pi
__global__ void kernel_fill_pi(float* data, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        data[idx] = 3.14159f;
    }
}

// 读取 ASC 文件（简化版）
std::vector<float> read_asc(const std::string& filename, int& nx, int& ny) {
    std::ifstream file(filename);
    std::string line;
    for (int i = 0; i < 6; i++) std::getline(file, line); // 跳过头

    file >> nx >> ny;
    std::vector<float> data(nx * ny);
    for (int i = 0; i < nx * ny; i++) {
        file >> data[i];
    }
    return data;
}

// 写 ASC 文件
void write_asc(const std::vector<float>& data, const std::string& filename, int nx, int ny) {
    std::ofstream file(filename);
    file << "ncols " << nx << "\n";
    file << "nrows " << ny << "\n";
    file << "xllcorner 0\n";
    file << "yllcorner 0\n";
    file << "cellsize 1.0\n";
    file << "NODATA_value -9999\n";
    for (int i = 0; i < nx * ny; i++) {
        file << data[i] << " ";
        if ((i+1) % nx == 0) file << "\n";
    }
}

// 主函数
int run_simulation(const std::string& work_dir) {
    std::cout << "Running flood simulation in: " << work_dir << std::endl;

    std::string work_dir_output = work_dir + "/output";
	//目录存在则删除，然后创建新目录
    if (directory_exists(work_dir_output.c_str())) {
        delete_directory(work_dir_output);
    }
	
    if (!directory_exists(work_dir_output.c_str())) {
        std::cout << "Creating: " << work_dir_output << std::endl;
        if (create_directory(work_dir_output.c_str())) {
            std::cout << "? Directory created." << std::endl;
        }
        else {
            std::cerr << "? Failed to create directory." << std::endl;
        }
    }
    else {
        std::cout << "?? Directory already exists." << std::endl;
    }
    
    // 1. 读取配置
    std::ifstream f(work_dir + "/config.json");
    json config;
    f >> config;

    int nx, ny;
    float dx = 1.0, dy = 1.0, dt = 1.0;
    int num_steps = config.value("num_steps", 100);

    // 2. 读取地形
    auto zb = read_asc(work_dir + "/dem.asc", nx, ny);
    std::vector<float> h(nx * ny, 0.0f);

    // 初始水深：中间加水
    int center = (nx / 2) * ny + ny / 2;
    h[center] = 10.0f;

    // 3. 分配 GPU 内存
    float* d_h, * d_zb;
    size_t size = nx * ny * sizeof(float);
    cudaMalloc(&d_h, size);
    cudaMalloc(&d_zb, size);

    cudaMemcpy(d_h, h.data(), size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_zb, zb.data(), size, cudaMemcpyHostToDevice);

    // 4. CUDA 网格配置
    dim3 block(16, 16);
    dim3 grid((nx + block.x - 1) / block.x, (ny + block.y - 1) / block.y);

    // 5. 时间步进
    for (int step = 0; step < num_steps; step++) {
        cuda_diffuse << <grid, block >> > (d_h, d_zb, nx, ny, dt, dx, dy);
        cudaDeviceSynchronize();

        // 每 50 步输出一次
        if (step % 50 == 0) {
            cudaMemcpy(h.data(), d_h, size, cudaMemcpyDeviceToHost);
            write_asc(h, work_dir_output + "/h_" + std::to_string(step * 10) + ".asc", nx, ny);
        }
    }

    // 6. 拷贝结果并清理
    cudaMemcpy(h.data(), d_h, size, cudaMemcpyDeviceToHost);
    write_asc(h, work_dir_output + "/h_final.asc", nx, ny);

    cudaFree(d_h);
    cudaFree(d_zb);

    std::cout << "Simulation completed." << std::endl;
    return 0;
}
