#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: wanglongyang
"""

import os
import pathlib
import sys
import platform

from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as build_ext_orig


class CMakeExtension(Extension):

    def __init__(self, name):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[])


class build_ext(build_ext_orig):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)
        super().run()

    def build_cmake(self, ext):
        cwd = pathlib.Path().absolute()


        build_temp = pathlib.Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)
        extdir = pathlib.Path(self.get_ext_fullpath(ext.name))
        extdir.mkdir(parents=True, exist_ok=True)

        #the following has not been tested for windows yet
        cuda_path = os.environ.get("CUDAToolkit_ROOT","")
        print('The cuda toolkit root path is '+ cuda_path)
        if cuda_path == "":
            cmake_args = []
        else:
            cmake_args = ['-DCUDA_TOOLKIT_ROOT_DIR=' + os.environ['CUDAToolkit_ROOT']]
        build_type = os.environ.get("BUILD_TYPE", "Release")
        build_args = ['--config', build_type]
        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(build_type.upper(), extdir.parent.parent.parent.absolute())]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + build_type]
            cmake_args += [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + str(extdir.parent.parent.parent.absolute()),
            ]
            build_args += ['--', '-j16']

        os.chdir(str(build_temp))
        self.spawn(['cmake', str(cwd)] + cmake_args)
        if not self.dry_run:
            self.spawn(['cmake', '--build', '.'] + build_args)
        os.chdir(str(cwd))

version = {}
_here = os.path.abspath(os.path.dirname(__file__))
_this_package = 'miniflood'
with open(os.path.join(_here, _this_package, 'version.py')) as f:
    exec(f.read(), version)

setup(
    name='miniflood',
    version=version['__version__'],
    author='wang longyang',
    author_email='451215954@qq.com',
    packages=find_packages(),
    ext_modules=[CMakeExtension('miniflood.lib.flood.cp313-win_amd64')],
    # ✅ 修改后（正确）
    long_description = (
        open("README.md", "r", encoding="utf-8").read()
        if os.path.exists("README.md")
        else ""
    ),
    long_description_content_type='text/markdown',
    description='a demo ',
    cmdclass={
        'build_ext': build_ext,
    },
    license='GPLv3',
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: C++',
        'Intended Audience :: Science/Research'
    ],
    package_data={'miniflood': ['examples/case01/config.json',
                            'examples/case01/dem.asc'],},
)
