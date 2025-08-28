# 编译运行 

# 1. 安装依赖
pip install pybind11

# 2. 创建构建目录
mkdir build && cd build

# 3. 配置 CMake-windows
cmake .. -DPython3_EXECUTABLE=$(where python)

import sys
sys.path.append(r'E:\dcgit\modelmarkets\MiniFlood\Debug')

import miniflood



## 3.使用setup安装 

3.1 pip install . -v

3.2 打包 pip -m build

3.3 上传 twine upload dist/* 

# 4. 运行 Python 脚本
cd ..
python python/run.py